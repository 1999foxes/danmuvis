import xml.sax
import json
import os.path
import ahocorasick
from .danmaku2ass import Danmaku2ASS


def make_AC(AC, word_set):
    for word in word_set:
        AC.add_word(word, word)
    return AC


AC_funny = ahocorasick.Automaton()
key_list_funny = ['233', '哈', 'hhh', '草', '？？', '??']
make_AC(AC_funny, set(key_list_funny))
AC_funny.make_automaton()

AC_exciting = ahocorasick.Automaton()
key_list_exciting = ['666', '强', 'oh']
make_AC(AC_exciting, set(key_list_exciting))
AC_exciting.make_automaton()

AC_lovely = ahocorasick.Automaton()
key_list_lovely = ['awsl', 'kksk', '切片', '？？', '??', 'hso']
make_AC(AC_lovely, set(key_list_lovely))
AC_lovely.make_automaton()


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

    def calcHightlight(self, d):
        # print(d)
        interval = 10
        for key in self.highlight:
            while len(self.highlight[key]) <= d.time // interval:
                self.highlight[key].append(0)
        self.highlight['density'][-1] += 1
        name_list = list(AC_funny.iter(d.content))
        if len(name_list) > 0:
            self.highlight['funny'][-1] += 1
        name_list = list(AC_exciting.iter(d.content))
        if len(name_list) > 0:
            self.highlight['exciting'][-1] += 1
        name_list = list(AC_lovely.iter(d.content))
        if len(name_list) > 0:
            self.highlight['lovely'][-1] += 1
    
    def generateASS(self):
        Danmaku2ASS(os.path.join(self.path, self.filename), 'Bilibili',
                    os.path.join(self.path, self.filename).replace('.xml', '.ass'),
                    1280, 720,
                    font_size=30, text_opacity=0.8)
    
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
        parser.parse(os.path.join(self.path, self.filename))


if __name__ == '__main__':
    danmaku = Danmaku(r"C:\my_code\danmuvis\resource\白雪艾莉娅_Official.20210504.【突击直播】一起来修仙.xml", '')
    danmaku.generateHighlight()
    print(danmaku.highlight)
