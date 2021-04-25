import os
import shutil
import subprocess
import time


class VideoClipper:
    @staticmethod
    def clip(input_media, durations):
        INPUT_MEDIA = input_media
        OUTPUT_NAME = './clips/clip_'
        OUTPUT_TYPE = '.mp4'

        # $ ffmpeg -i in.mpn -ss [start] -to [end] out.mpn
        # Note:
        #    '[start]' - The start point of original media 'in.mpn'.
        #    '[start]' - The format is 'hh:mm:ss.xxx' or 'nnn', '00:01:15.000' or '75'.
        #    '[end]'   - The end point of original media 'in.mpn'.
        #    '[end]'   - The format is 'hh:mm:ss.xxx' or 'nnn', '00:01:25.000' or '85'.
        # Note:
        #     Setting '-i in.mpn' before '-ss [start]' avoids inaccurate clips.
        #     Removing 'copy' re-encodes clips and avoids black screen/frames.
        #     Removing 'copy' leads to high CPU load and long operating time.
        for i in range(len(durations)):
            d = durations[i]
            tag_start = str(d[0])
            tag_end = str(d[1])
            # tag_time = str(d[1]-d[0])

            output_file = OUTPUT_NAME + str(i + 1) + OUTPUT_TYPE

            # cmd = 'ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i ' + INPUT_MEDIA \
            #       + ' -ss ' + tag_start + ' -to ' + tag_end \
            #       + ' -vf scale_cuda=1280:720 -c:a copy -c:v h264_nvenc -b:v 5M ' + output_file

            cmd = r'ffmpeg_win64\ffmpeg -y -vsync 0 -hwaccel cuda -hwaccel_output_format cuda -i "' + INPUT_MEDIA \
                   + '" -ss ' + tag_start + ' -to ' + tag_end \
                   + ' -c:a copy -c:v copy -b:v 5M ' + output_file

            # cmd = r'ffmpeg_win64\ffmpeg -hwaccel auto -i "' + INPUT_MEDIA \
            #       + r'" -preset medium -max_muxing_queue_size 2048 -vcodec h264_qsv -acodec libfdk_aac -map_metadata -1 -map_chapters -1 -movflags faststart' \
            #       + r' -ss ' + tag_start + r' -to ' + tag_end \
            #       + r' -map 0:v:0 -map 0:a:0 -vb 1200k -ab 128k -profile:v high -pix_fmt yuv420p -y "' \
            #       + output_file +r'"'
            
            print(cmd)
            subprocess.call(cmd, shell=False)


if __name__ == "__main__":
    time0 = time.time()
    vc = VideoClipper.clip("./22671795-暗妃鲁咪蕾Official/录制-22671795-20210222-201234-【B限】天才MC.flv", [[50, 80], [500, 800]])
    print("clipping takes:", time.time()-time0, "s. ")
