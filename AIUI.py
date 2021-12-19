import viVoicecloud as vv
from random import randint

class AIUI:
    def __init__(self):
        self.can = 0
    def getAnswer(self,text):
        answer = vv.aiui(text)
        #print(answer)
        if answer[0] != self.can or not answer[3]:
            res =  '回答不了'
        else:
            res = answer[3]
            if len(res) > 1:
                res = res[1]
            else:
                res = res[0]
        #print('机器人：',res)
        return res

if __name__ == '__main__':
    try:
        aiui = AIUI()
        while True:
            text = input('输入问题：')
            ans = aiui.getAnswer(text)
            print(ans)
    except Exception as e:
        print(e)
        pass
