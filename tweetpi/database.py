from abc import ABCMeta, abstractmethod
from urllib.parse import urlparse
import uuid
import hashlib
import platform
import sys
from contextlib import contextmanager
import time

try:
    import pymysql
    MYSQL_READY = True
except ImportError:
    MYSQL_READY = False
try:
    import pymongo
    MONGODB_READY = True
except ImportError:
    MONGODB_READY = False


def init(db_uri):
    """Get appropriate DBClient according to db_uri"""
    if db_uri.startswith("mysql") or db_uri.startswith("mariadb"):
        if MYSQL_READY:
            return MySQLDBClient(db_uri)
        else:
            raise ImportError("pymysql is required to interact with the db")
    if db_uri.startswith("mongodb"):
        if MONGODB_READY:
            return MongoDBClient(db_uri)
        else:
            raise ImportError("pymongo is required to interact with the db")
    if not db_uri:
        return NoDBClient(debug=True)

    raise ValueError("Unknown database URI")

class DBClientAbstract:
    __metaclass__ = ABCMeta
    uri = ""
    session_id = ""
    manual_connection = False

    def __init__(self, uri=None, manual_connection=False):
        self.uri = uri
        self.session_id = self.get_fingerprint()
        self.manual_connection = manual_connection

    def get_fingerprint(self):
        sb = []
        sb.append(platform.node())
        sb.append(platform.architecture()[0])
        sb.append(platform.architecture()[1])
        sb.append(platform.machine())
        sb.append(platform.processor())
        sb.append(platform.system())
        sb.append(str(uuid.getnode())) # MAC address
        text = '#'.join(sb)
        return "{}_{:.0f}".format(hashlib.md5(text.encode('utf-8')).hexdigest()[0:16], time.time())

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def log(self, type, keyword, key, text, metadata):
        # session_id, timestamp
        pass

    @abstractmethod
    def batch_logs(self, data):
        pass

    @abstractmethod
    def search_by_keyword(self, keyword):
        pass

    @abstractmethod
    def get_total_by_type(self):
        pass

    @abstractmethod
    def get_annotation_keywords_list(self, limit=20):
        pass

class MongoDBClient(DBClientAbstract):
    conn = None
    db_name = "admin"

    def connect(self):
        self.conn = pymongo.mongo_client.MongoClient(self.uri)
        URL_CONFIG = urlparse(self.uri)
        self.db_name = URL_CONFIG.path[1:]

    def close(self):
        self.conn.close()
        self.conn = None

    @contextmanager
    def get_connection(self, close=True):
        if not self.conn:
            self.connect()
        try:
            yield self.conn
        finally:
            if close:
                self.close()

    def install(self):
        # logs
        pass

    def log(self, type, keyword, key, text="", metadata={}):
        with self.get_connection() as conn:
            doc = self._log_doc(type, keyword, key, text, metadata)
            conn[self.db_name]["logs"].insert_one(doc)

    def _log_doc(self, type, keyword, key, text="", metadata={}):
        if isinstance(keyword, str):
            keyword = [keyword]
        return {"type": type, "keyword": keyword, "key": key, "text": text, "metadata": metadata, "session_id": self.session_id, "timestamp": time.time()}

    def batch_logs(self, data):
        with self.get_connection() as conn:
            conn[self.db_name]["logs"].insert_many([self._log_doc(**d) for d in data])

    def search_by_keyword(self, keyword):
        with self.get_connection() as conn:
            return list(conn[self.db_name]["logs"].find({"keyword": {"$in": [keyword]}}))

    def get_total_by_type(self):
        with self.get_connection() as conn:
            return list(
                conn[self.db_name]["logs"].aggregate([
                    {"$group": {"_id": "$type", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}}
                ]))

    def get_annotation_keywords_list(self, limit=20):
        with self.get_connection() as conn:
            return list(
                conn[self.db_name]["logs"].aggregate([
                    {"$match": {"type": "annotate"}},
                    {"$unwind": "$keyword"},
                    {"$group": {"_id": "$keyword", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": limit}
                ]))

class MySQLDBClient(DBClientAbstract):
    conn = None

    def connect(self, autocommit=True):
        URL_CONFIG = urlparse(self.uri)

        self.conn       = pymysql.connect(
            host        = URL_CONFIG.hostname,
            port        = URL_CONFIG.port,
            user        = URL_CONFIG.username,
            password    = URL_CONFIG.password,
            db          = URL_CONFIG.path[1:],
            charset     = 'utf8mb4',
            autocommit  = autocommit,
            cursorclass = pymysql.cursors.DictCursor
        )

    def close(self):
        self.conn.close()
        self.conn = None

    @contextmanager
    def get_connection(self, close=True):
        if not self.conn:
            self.connect()
        try:
            yield self.conn
        except Exception:
            self.conn.rollback()
            raise
        else:
            self.conn.commit()
        finally:
            if close:
                self.close()

    def install(self):
        pass

    def log(self, type, keyword, key, text, metadata):
        with self.get_connection() as conn:
            self._log(conn, type, keyword, key, text, metadata)

    def _log(self, conn, type, keyword, key, text, metadata):
        pass

    def batch_logs(self, data):
        with self.get_connection() as conn:
            for d in data:
                self._log(conn, **d)

    def search_by_keyword(self, keyword):
        pass

    def get_total_by_type(self):
        pass

    def get_annotation_keywords_list(self, limit=20):
        pass

class NoDBClient(DBClientAbstract):
    debug = False

    def __init__(self, uri=None, manual_connection=False, debug=False):
        super().__init__(uri=uri, manual_connection=manual_connection)
        self.debug = debug

    def connect(self):
        pass

    def close(self):
        pass

    def install(self):
        pass

    def log(self, type, keyword, key, text="", metadata={}):
        self._log(type, keyword, key, text, metadata)

    def _log(self, type, keyword, key, text="", metadata={}):
        if isinstance(keyword, str):
            keyword = [keyword]
        if self.debug:
            print("{} {} {} {} {}".format(type, ",".join(keyword), key, text, metadata), file=sys.stderr)

    def batch_logs(self, data):
        for d in data:
            self._log(**d)

    def search_by_keyword(self, keyword):
        return []

    def get_total_by_type(self):
        return {}

    def get_annotation_keywords_list(self, limit=20):
        return []
