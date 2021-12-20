from aip import AipOcr
import cv2
from KEY import *
from threading import Thread
from time import sleep
class OCR:
    def __init__(self,show = False):
        self.client = AipOcr(APP_ID,API_KEY,SECRET_KEY)
        self.trigger = False
        self.waitForRes = 5
        self.maxFail = self.waitForRes
        self.fail = 0
        self.stop = False
        self.words = []
        self.show = show
    def read(self,name):
        with open(name,'rb') as f:
            return f.read()

    def encode(self,img):
        return cv2.imencode('.jpg',img)[1].tobytes()

    def analyze(self,img):
        try:
            res = self.client.general(self.encode(img))
            words = [item['words'] for item in res['words_result']]
            return words
        except Exception as e:
            print(e)
            return []

    def recognize(self):
        self.trigger = True
        self.fail = 0

    def finish(self):
        self.stop = True

    def start(self):
        #摄像头就一个 OCR和YOLO都得用 要么在Voice里获得对象 传到OCR和YOLO的类里 要么就进入模式再用 用完直接release
        camera = cv2.VideoCapture(0)
        success,frame = camera.read()
        while success:
            if self.show:
                cv2.imshow('window',frame)
            
            success,frame = camera.read()
            sleep(1) 
            #如果这里用cv.waitKey(10) 单独运行Voice可以跑 但是运行ui 就跑不了 会卡在这句话上 不知道为什么 好坑
            #if cv2.waitKey(10) == ord('s'):
            if self.trigger:
                if success:
                    self.words = self.analyze(frame)
                else:
                    self.words = []
                if not self.words:
                    self.fail += 1
                    if self.fail > self.maxFail:
                        self.trigger = False

                #print('words:',self.words)
            #if cv2.waitKey(100) == ord('q'):
            if self.stop:
                break
        if self.show: 
            cv2.destroyAllWindows()
        
        camera.release()

if __name__ == '__main__':
    model = OCR(True)
    t = Thread(target = model.start).start()
    while True:
        try:
            c = input()
            if c == 'q':
                model.finish()
                break
            elif c == 's':
                model.recognize()
                sleep(2)
                print(model.words)
        except:
            break
        
