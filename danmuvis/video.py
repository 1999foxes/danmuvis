import os
import os.path
import subprocess
import random


class Video:
    def __init__(self, filename, path):
        self.filename = filename
        self.path = path
        self.highlight = None

    def update_metadata(self):
        pass

    def clip(self, range, clipname, with_ass=True):
        tag_start = str(range[0])
        tag_end = str(range[1])

        input_file = os.path.join(self.path, self.filename)
        output_file = os.path.join(self.path, clipname)

        if not with_ass:
            cmd = r'./danmuvis/tools/ffmpeg.exe -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda ' \
                  + ' -i ' + '"' + input_file + '"' \
                  + ' -ss ' + tag_start + ' -to ' + tag_end \
                  + ' -c:a copy -c:v copy -b:v 5M ' \
                  + '"' + output_file + '"'
            print(cmd)
            subprocess.call(cmd, shell=False)
        else:
            input_assfile = os.path.join(self.path, self.filename.replace('.ready', '').replace('.flv', '.ass'))
            tmp_assfile = os.path.join(self.path, str(random.randint(0, 999999)) + '.ass')
            cmd = r'./danmuvis/tools/ffmpeg.exe -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda ' \
                  + r' -itsoffset -' + tag_start + r' -i "' + input_assfile + r'" ' \
                  + r' -c copy "' + tmp_assfile + r'"'
            print(cmd)
            subprocess.call(cmd, shell=False)

            tmp_file = os.path.join(self.path, 'tmp_' + str(random.randint(0, 999999)) + '_' + clipname)
            cmd = r'./danmuvis/tools/ffmpeg.exe -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda ' \
                  + ' -i ' + '"' + input_file + '"' \
                  + ' -ss ' + tag_start + ' -to ' + tag_end \
                  + ' -c:a copy -c:v copy -b:v 5M ' \
                  + '"' + tmp_file + '"'
            print(cmd)
            subprocess.call(cmd, shell=False)
            #
            # cmd = r'./danmuvis/tools/ffmpeg.exe' \
            #       + r' -i "' + tmp_file + r'" ' \
            #       + r'-vf "subtitles=' + tmp_assfile.replace('\\', '\\\\\\\\').replace(':', '\\\\:') + r'" ' \
            #       + r' "' + output_file + r'"'
            cmd = r'./danmuvis/tools/ffmpeg.exe -vsync 0 -c:v h264_cuvid ' \
                  + r' -i "' + tmp_file + r' " -vf "subtitles=' + tmp_assfile.replace('\\', '\\\\\\\\').replace(':', '\\\\:') + r',hwupload_cuda,scale_cuda=1280:720" -c:v h264_nvenc' \
                  + r' "' + output_file + r'"'
            print(cmd)
            subprocess.call(cmd, shell=False)

            os.remove(tmp_assfile)
            os.remove(tmp_file)

    def clip_and_merge(self, ranges, clipname, assfilenames=None):
        pass  # not implemented yet
