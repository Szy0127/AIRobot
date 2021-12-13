import itchat
from time import sleep
from pypinyin import lazy_pinyin as get_pinyin

class Wechat:
    def __init__(self,fromUI=False):
        self.sendToName = '' 
        self.isLogin = False
        self.fromUI = fromUI
        self.enableCmdQR = not self.fromUI if self.fromUI else 2
        self.hotReload = False
    def login(self):
        if self.isLogin:
            return True
        try:
            #需要sudo 否则QR.png权限不够
            itchat.auto_login(enableCmdQR = self.enableCmdQR,hotReload = self.hotReload)
            self.friends = itchat.get_friends(update=True)
            self.pinyin2name = {self.name2pinyin(fri['RemarkName']):fri['RemarkName'] for fri in self.friends}
            self.isLogin = True
            return True
        except Exception as e:
            print(e)
            return False
    def name2pinyin(self,name):
        pinyin = get_pinyin(name)
        return '-'.join(pinyin)
    
    def check(self,name):
        assert self.isLogin
        pinyin = self.name2pinyin(name)
        if pinyin in self.pinyin2name:
            self.sendToName = self.pinyin2name[pinyin]
            return self.sendToName

    def send(self,msg):
        assert self.isLogin
        try:
            user = itchat.search_friends(name=self.sendToName)[0]
            user.send(msg)
            sleep(0.5)
            return True
        except:
            return False

if __name__ == '__main__':
    wechat = Wechat()
    wechat.login()
    wechat.check('童楚炎')
    wechat.send('你好')
