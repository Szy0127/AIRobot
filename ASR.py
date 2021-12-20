# -*- coding: utf-8 -*-
import pyaudio
import viVoicecloud as vv
#from sjtu.audio import findDevice
from get_device import getDeviceIndexByName

class ASR:
    def __init__(self,running):
        self.device_in = getDeviceIndexByName("ac108")
        self.Sample_channels = 1  
        self.Sample_rate = 16000  
        self.Sample_width = 2         
        self.time_seconds = 0.5  #录音片段的时长，建议设为0.2-0.5秒
        self.sessionFinishFlag = 3
        self.audio = pyaudio.PyAudio() 
        self.stream = self.audio.open(rate=self.Sample_rate,format=self.audio.get_format_from_width(self.Sample_width),
            channels=self.Sample_channels,input=True,input_device_index=self.device_in,start = False)
        vv.Login()
        self.asr = vv.asr()
        self.running = running 

    def startSession(self,language='Chinese'):
        self.asr.SessionBegin(language=language)#开始语音识别
        self.stream.start_stream()
        print('***Listening...')
        #录音并上传到讯飞，当判定一句话已经结束时，status返回3
        status=0
        while status!= self.sessionFinishFlag and self.running():
            frames=self.stream.read(int(self.Sample_rate*self.time_seconds),exception_on_overflow = False)
            ret,status,recStatus=self.asr.AudioWrite(frames)
    
        self.stream.stop_stream()
        print ('---GetResult...')
    
        words=self.asr.GetResult()  #获取结果
        self.asr.SessionEnd()#结束语音识别
        #print('用户：',words)
        return words
    def __del__(self):
        vv.Logout()#注销
        self.stream.close()
        self.audio.terminate()

if __name__ == '__main__':
    asr = ASR()
    asr.startSession()




