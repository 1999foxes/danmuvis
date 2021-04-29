# 待实现
class ASS:
    def __init__(self, filename, range):
        self.filename = filename
        self.range = range
        self.str = ''
    
    def append(self, d):
        if d.time >= self.range[0] and d.time < self.range[1]:
            self.str += str(d)
    
    # write str to file
    def flush(self):
        print(self.str)