from aip import AipOcr
import cv2
from KEY import *
from threading import Thread
from time import sleep
class OCR:
    def __init__(self,show = False):
        self.client = AipOcr(APP_ID,API_KEY,SECRET_KEY)
        self.camera = cv2.VideoCapture(0)
        self.trigger = False
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
        except:
            return []

    def recognize(self):
        self.trigger = True

    def finish(self):
        self.stop = True

    def start(self):
        success,frame = self.camera.read()
        while success:
            if self.show:
                cv2.imshow('window',frame)
            success,frame = self.camera.read()
            cv2.waitKey(10)

        
            #if cv2.waitKey(10) == ord('s'):
            if self.trigger:
                self.words = self.analyze(frame)
                self.trigger = False
                #print('words:',self.words)
            #if cv2.waitKey(100) == ord('q'):
            if self.stop:
                break
        if self.show: 
            cv2.destroyAllWindows()
        
    def __del__(self):
        self.camera.release()

if __name__ == '__main__':
    model = OCR()
    t = Thread(target = model.start).start()
    while True:
        try:
            c = input()
            if c == 'q':
                model.finish()
            elif c == 's':
                model.recognize()
                sleep(2)
                print(model.words)
        except:
            break
        
