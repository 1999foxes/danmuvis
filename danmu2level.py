import xml.sax
import re


class Danmu2Level:
    class DanmuHandler(xml.sax.ContentHandler):
        def __init__(self, pattern):
            self.is_danmu = False
            self.pattern_time = re.compile(r'\d+', re.I)
            self.pattern_joy = re.compile(pattern, re.I)
            self.pattern_trans = re.compile(r'(【)([^】]*)', re.I)

            self.last_time = -1
            self.joy_level = []
            self.translation = []

        def startElement(self, tag, attributes):
            if tag == "d":
                self.is_danmu = True
                time = int(self.pattern_time.match(attributes["p"]).group())
                while time // 10 >= len(self.joy_level):
                    self.joy_level.append(0)
                self.last_time = time

        def endElement(self, tag):
            if tag == "d":
                self.is_danmu = False

        def characters(self, content):
            if self.is_danmu:
                m = self.pattern_trans.match(content)
                if m is not None:
                    self.translation.append([self.last_time, m[2]])
                if self.pattern_joy.match(content) is not None:
                    self.joy_level[-1] += 1

    @staticmethod
    def smooth(joy_level):
        if len(joy_level) < 2:
            return
        smoothed = [joy_level[0]]
        for i in range(1, len(joy_level)):
            smoothed.append((joy_level[i] + joy_level[i-1]) // 2)
        return smoothed


    @staticmethod
    def decode_xml(path, pattern):
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        dh = Danmu2Level.DanmuHandler(pattern)
        parser.setContentHandler(dh)
        parser.parse(path)
        return Danmu2Level.smooth(dh.joy_level), dh.translation
