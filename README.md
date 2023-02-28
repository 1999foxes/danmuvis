# danmuvis


本项目是我出于兴趣开发的，作用是在冗长的直播录像中快速定位精彩片段并剪辑。
主要功能有：
1. 根据视频弹幕的内容和频率计算“精彩值”并绘制可视化图表。
2. 视频片段的播放、剪辑和字幕压制。


使用方法：
    set FLASK_APP=danmuvis
    python -m flask update-files -p YOUR_PATH_TO_RESOURCE_FOLDER
    python -m flask run


界面：
![index](https://github.com/1999foxes/danmuvis/blob/main/1.png?raw=true)
![player](https://github.com/1999foxes/danmuvis/blob/main/2.png?raw=true)
