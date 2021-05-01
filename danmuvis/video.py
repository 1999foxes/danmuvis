import os
import shutil
import subprocess
import time
          

class Video:
    def __init__(self, filename):
        self.filename = filename

    def clip(self, range, clipname, assfilename=None):
        INPUT_MEDIA = self.filename
        OUTPUT_NAME = './' + INPUT_MEDIA + '.clip.' + clipname
        OUTPUT_TYPE = '.mp4'

        tag_start = str(range[0])
        tag_end = str(range[1])

        output_file = OUTPUT_NAME + OUTPUT_TYPE

        cmd = ''
        if assfilename is None:
            cmd = r'ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i "' + INPUT_MEDIA \
                   + '" -ss ' + tag_start + ' -to ' + tag_end \
                   + ' -c:a copy -c:v copy -b:v 5M ' + output_file
        else:
            pass        # not implemented yet

        print(cmd)
        subprocess.call(cmd, shell=False)

    def clip_and_merge(self, ranges, clipname, assfilenames=None):
        pass            # not implemented yet


if __name__ == "__main__":
    time0 = time.time()
    v = Video("录制-21402309-20210314-192137-【B限】9万人記念回！ガチ恋距離歌回！.flv")
    v.clip([5, 15], 'test')
    print("clipping takes:", time.time()-time0, "s. ")
