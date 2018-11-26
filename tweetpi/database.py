from abc import ABCMeta, abstractmethod
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

    raise ValueError("Unknown database URI")

class DBClientAbstract:
    __metaclass__ = ABCMeta
    session_id = ""

    @abstractmethod
    def __init__(self, uri):
        self.session_id = self.get_fingerprint()
        pass

    def get_fingerprint(self):
        return ""

    @abstractmethod
    def install(self):
        pass

    @abstractmethod
    def log(self, type, keyword, key, text, metadata):
        # session_id, timestamp
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
    def __init__(self, uri):
        pass

class MySQLDBClient(DBClientAbstract):
    def __init__(self, uri):
        pass
