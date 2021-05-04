import os
import os.path
import subprocess


class Video:
    def __init__(self, filename, path):
        self.filename = filename
        self.path = path
        self.highlight = None

    def update_metadata(self):
        pass

    def clip(self, range, clipname, assfilename=None):
        tag_start = str(range[0])
        tag_end = str(range[1])

        input_file = os.path.join(self.path, self.filename)
        output_file = os.path.join(self.path, clipname)

        cmd = ''
        if assfilename is None:
            cmd = r'./danmuvis/tools/ffmpeg.exe -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i ' \
                  + '"' + input_file + '"' \
                  + ' -ss ' + tag_start + ' -to ' + tag_end \
                  + ' -c:a copy -c:v copy -b:v 5M ' \
                  + '"' + output_file + '"'
        else:
            pass        # not implemented yet

        print(cmd)

        subprocess.call(cmd, shell=False)

    def clip_and_merge(self, ranges, clipname, assfilenames=None):
        pass            # not implemented yet
