from Music import Music
from AIUI import AIUI
from ASR import ASR
from translate import Translate
from wechat import Wechat
from OCR import OCR
from YOLO import YOLO
import viVoicecloud as vv
import os
from time import sleep
from threading import Thread
from os import system
INTERACTIVE_MODE = 0
MUSIC_MODE = 1
TRANSLATE_MODE = 2
WECHAT_MODE = 3
OCR_MODE = 4
YOLO_MODE = 5

class Running:
    def __init__(self):
        self.running = False
    def run(self):
        self.running = True
    def stop(self):
        self.running = False
    def __call__(self):
        return self.running


class VoiceAssistant:
    def __init__(self,fromUI = False):
        self.flag = False # 防止应该接受的话被过滤
        self.fromUI = fromUI
        self.volume = 20 
        self.setVolume()
        self.running = Running()
        self.asr = ASR(self.running)
        self.aiui = AIUI()
        self.music = Music()
        self.translate = Translate()
        self.voice = vv.tts()
        self.wechat = Wechat(self.fromUI)
        #self.ocr = OCR(self.fromUI)
        #self.yolo = YOLO(self.fromUI)
        self.ocr = OCR()
        self.yolo = YOLO()
        self.translateLan = 'zh'
        self.wait_lan = False
        self.status = INTERACTIVE_MODE
        self.voiceDict = {'zh':'xiaofeng','en':'henry'}
        self.waitSongName = False
        self.user_content = ''
        self.assistant_content = ''
        self.saying = False 
    def setVolume(self):
        if self.volume < 0:
            self.volume = 0
        if self.volume > 100:
            self.volume = 100
        os.system('amixer -M set PCM '+str(self.volume)+'%')
    def increaseVolume(self):
        self.volume += 10
        self.setVolume()
    def decreaseVolume(self):
        self.volume -= 10
        self.setVolume()

    def _say(self,text,language):
        self.saying = True
        self.voice.say(text = text,voice = self.voiceDict[language])
        self.saying = False

    def say(self,text,language = 'zh'):
        print('语音助手：',text)
        self.assistant_content = text
        #say的阻塞会导致ui刷新有延迟 使用多线程调用say
        #为了不影响多个say同时发生导致的问题 其余的say不发声 但不影响正常功能（ui和cmd会显示）
        #但是登录微信的时候还是只有声音 ui不会显示
        if not self.saying:
            Thread(target=self._say,args=(text,language)).start()

    def keyWord(self,key,content):
        return key in content and len(content) < 8 

    def wechatWord(self,content):
        if '给' in content and '发消息' in content:
            name = content[content.index('给')+1:content.index('发')]
            return name
    
    def finish(self):
        self.status = TRANSLATE_MODE
        self.waitSongName = False
        self.flag = False
        self.music.release()
        self.running.stop()

    def toTranslate(self):
        self.say('你想要翻译的源语言是中文还是英文')
        self.status = TRANSLATE_MODE
        self.flag = True
        self.wait_lan = True
    def toMusic(self):
        self.say('你想听什么歌')
        self.status = MUSIC_MODE
        self.waitSongName = True
    
    def toWechat(self):
        inputName = self.wechatWord(self.user_content)
        outputName = self.wechat.check(inputName)
        if outputName : 
            self.say('你想给'+outputName+'发什么消息')
            self.status = WECHAT_MODE
        else:
            self.say('不存在备注为'+inputName+'的好友')

    def loginWechat(self):
        self.say('请扫码登录微信')
        if self.wechat.login():
            self.say('登录成功')
            #删掉扫描的二维码
            system("t=`ps x|grep QR | awk '{print $1}' | awk 'NR==1'`&&kill ${t}")
            sleep(2)
        else:
            self.say('登录失败')


    def toOCR(self):
        self.say('请将摄像头对准需要识别的区域')
        self.status = OCR_MODE
        Thread(target=self.ocr.start).start()
    
    def toYOLO(self):
        self.say('请将摄像头对准需要识别的区域')
        self.status = YOLO_MODE
        Thread(target=self.yolo.start).start()


    def process(self,content):
        if self.status == INTERACTIVE_MODE:
            if self.keyWord('退出',content):
                self.running.stop()
                return
            if self.keyWord('点歌',content):
                self.toMusic()    
                return
            if self.keyWord('翻译',content):
                self.toTranslate()
                return 
            if self.keyWord('登录微信',content):
                self.loginWechat()
                return
            if self.keyWord('文字识别',content):
                self.toOCR()
                return
            if self.keyWord('物体识别',content):
                self.toYOLO()
                return

            if self.keyWord('提高音量',content):
                self.increaseVolume()
                self.say('音量提高至'+str(self.volume))
                return 
            if self.keyWord('降低音量',content):
                self.decreaseVolume()
                self.say('音量降低至'+str(self.volume))
                return
            if self.wechatWord(content): #name:= self.wechatWord(content)    
                if self.wechat.isLogin:
                    self.toWechat()
                else:
                    self.loginWechat()
                    self.toWechat()  
                return
            answer = self.aiui.getAnswer(content)
            self.say(answer)
            return
        if self.status == MUSIC_MODE:
            if self.keyWord('暂停',content):
                self.music.pause()
                return
            if self.keyWord('继续' ,content):
                self.music.resume()
                return
            if self.keyWord('返回',content):
                self.music.release()
                self.say('返回交互模式')
                self.status = INTERACTIVE_MODE
                return
            if self.keyWord('换一首',content):
                self.say('换什么歌')
                self.waitSongName = True
                return    
            if self.waitSongName:
                if self.music.getMusic(content):
                    self.music.play()
                    self.waitSongName = False
                else:
                    self.say('出错了，请再说一遍')
                return
        if self.status == TRANSLATE_MODE:
            if self.keyWord('返回',content):
                self.say('返回交互模式')
                self.status = INTERACTIVE_MODE
                return        
            if self.wait_lan:
                if self.keyWord('中文',content):
                    self.flag = False
                    self.wait_lan = False
                    self.translateLan = 'zh'
                    self.say('你想翻译什么内容')
                    return
                if self.keyWord('英文',content):
                    self.wait_lan = False
                    self.translateLan = 'en'
                    self.say('what do you want to translate','en')
                    return
                return
            self.flag = False
            res = self.translate.translate(content,self.translateLan)
            lanTo = 'zh' if self.translateLan == 'en' else 'en'
            self.say(res,lanTo)
            return
        if self.status == WECHAT_MODE:
            if self.keyWord('返回',content):
                self.say('返回交互模式')
                self.status = INTERACTIVE_MODE
                return
            if self.wechat.send(content):
                self.say('发送成功')
                self.status = INTERACTIVE_MODE 
            else:
                self.say('发送失败,请再说一遍')
            return
        if self.status == OCR_MODE:
            if self.keyWord('返回',content):
                self.say('返回交互模式')
                self.status = INTERACTIVE_MODE
                self.ocr.finish()
                return
            if self.keyWord('这是什么',content):
                self.say('正在识别')
                self.ocr.recognize()
                sleep(self.ocr.waitForRes)#识别需要时间 否则会读到上一次的结果
                if self.ocr.words:
                    self.say(''.join(self.ocr.words))
                else:
                    self.say('识别失败')
                return
        if self.status == YOLO_MODE:
            if self.keyWord('返回',content):
                self.say('返回交互模式')
                self.status = INTERACTIVE_MODE
                self.yolo.finish()
                return
            if self.keyWord('这是什么',content):
                self.say('正在识别')
                self.yolo.recognize()
                sleep(self.yolo.waitForRes)#识别需要时间 否则会读到上一次的结果
                if self.yolo.objects:
                    self.say(max(self.yolo.objects))
                else:
                    self.say('识别失败')
                return
                

    def run(self):
        self.running.run()
        if 1==1:
        #try:
            self.say('你好，我是你的语音助手')
            while self.running():
                content = self.asr.startSession()
                if not self.running():
                    break
                if not content or len(content)<=1:
                    continue
                if content[-1] in '.。':
                    content = content[:-1]
                #say是开线程的 say的时候也在listen 很容易听到say的内容
                if not self.flag and len(set(content) & set(self.assistant_content)) > int(len(set(content))*0.5):
                #if content in self.assistant_content:
                    continue 
                print('用户:',content)
                self.user_content = content
                self.process(content)
        try:
            pass
        except Exception as e:
            print(e)
        finally:
            self.running.stop()
            self.say('再见')


if __name__ == '__main__':
    va = VoiceAssistant()
    va.run()
