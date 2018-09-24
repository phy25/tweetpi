import os
import tempfile
from PIL import Image

class LocalPhoto:
    local_path = ""
    PILim = None
    def __init__(self, local_path):
        self.local_path = local_path

    def resize(self, width=1280, height=720, fill_color=(0, 0, 0)):
        # https://stackoverflow.com/a/44231784/4073795
        if not self.PILim:
            self.PILim = Image.open(self.local_path)
        x, y = self.PILim.size
        final_x, final_y = width, height
        if x/y > width/height:
            # too long
            final_y = round(y*(width/x))
        else:
            final_x = round(x*(height/y))
        resized_im = self.PILim.resize((final_x, final_y), Image.LANCZOS)
        new_im = Image.new('RGB', (width, height), fill_color)
        new_im.paste(resized_im, (round((width - final_x) / 2), round((height - final_y) / 2)))
        resized_im = None
        return new_im

    def resize_to_temp(self, width=1280, height=720, fill_color=(0, 0, 0, 0)):
        im = self.resize(width=width, height=height, fill_color=fill_color)
        name = os.path.join(tempfile.gettempdir(), os.path.basename(self.local_path))
        im.save(name)
        return name

    def add_annotation(self, width=1280, height=720, fill_color=(0, 0, 0, 0)):
        # TODO: extract PhotoList.generate_annotated_video to here,
        # and tackling ttf performance issue
        raise Exception("add_annotation not implemented")
