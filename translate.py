import viVoicecloud as vv
from time import sleep
class Translate:
    def __init__(self):
        self.tr = vv.baidu_translate()
    def c2e(self,text):
        try:
            res = self.tr.translate(text,'zh','en')
            sleep(0.8)
        except:
            res = 'Translation failed'
        return res
    def e2c(self,text):
        try:
            res = self.tr.translate(text,'en','zh')
            sleep(0.8)
        except:
            res = '翻译失败'
        return res
    def translate(self,text,lan):
        if lan == 'zh':
            return self.c2e(text)
        elif lan == 'en':
            return self.e2c(text)



if __name__ == '__main__':
    t = Translate()
    t1 = '大家晚上好'
    t2 = 'Good evening,everyone'
    print(t.c2e(t1))
    print(t.e2c(t2))
