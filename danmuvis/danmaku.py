import xml.sax
import json
import os.path


class Danmaku:
    def __init__(self, filename, path):
        self.filename = filename
        self.path = path
        self.highlight = None

    def generateHighlight(self):
        self.highlight = {'density': [], 'funny': [], 'exciting': [], 'lovely': []}
        self.decodeDanmakuXML(self.calcHightlight)
        with open(os.path.join(self.path, self.filename).replace('xml', 'json'), 'w') as highlight_file:
            json.dump(self.highlight, highlight_file)

    # 待实现，使用多个DFA过滤弹幕计算精彩值
    def calcHightlight(self, d):
        # print(d)
        interval = 10
        for key in self.highlight:
            while len(self.highlight[key]) <= d.time // interval:
                self.highlight[key].append(0)
        self.highlight['density'][-1] += 1
    
    def generateASS(self):
        pass
    
    class D:
        def __init__(self, p, user, content):
            attr = p.split(',')
            self.time = float(attr[0])
            self.user = user
            self.content = content
        
        def __str__(self):
            return ','.join([str(self.time), self.user, self.content])

    class DanmakuHandler(xml.sax.ContentHandler):
        def __init__(self, handler):
            self.handler = handler
            
            self.p = None
            self.user = None
            self.content = None

        def startElement(self, tag, attributes):
            if tag == "d":
                self.p = attributes['p']
                self.user = attributes['user']

        def endElement(self, tag):
            if tag == "d":
                self.handler(Danmaku.D(self.p, self.user, self.content))

        def characters(self, content):
            self.content = content

    def decodeDanmakuXML(self, handler):
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        danmakuHandler = Danmaku.DanmakuHandler(handler)
        parser.setContentHandler(danmakuHandler)
        parser.parse(self.filename)


if __name__ == '__main__':
    danmaku = Danmaku(r'录制-22853788-20210311-190152-【B限】5万人纪念晩酌配信.xml')
    print(danmaku.highlight)