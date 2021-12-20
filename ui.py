import sys
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QPushButton, QGridLayout,QTextBrowser
from PyQt5.QtCore import QTimer
from Voice import VoiceAssistant
from threading import Thread
class VoiceGUI(QWidget):
    def __init__(self):
        super(VoiceGUI,self).__init__()
        self.va = VoiceAssistant(True)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.resize(900,600)
        self.move(50,50)
        self.running = False
        self.setWindowTitle('语音助手')
        self.label_user = QLabel('我：')
        self.layout.addWidget(self.label_user,3,1)
        self.label_assistant = QLabel('语音助手：')
        self.layout.addWidget(self.label_assistant,4,1)

        self.text_user_content = QTextBrowser()
        self.layout.addWidget(self.text_user_content,3,2,3,4)
        self.text_assistant_content = QTextBrowser()
        self.layout.addWidget(self.text_assistant_content,4,2,4,4)
       
        self.button_switch = QPushButton('开启语音助手')
        self.button_switch.clicked.connect(self.switch_status)
        self.layout.addWidget(self.button_switch,1,1)
        
       
        self.button_loginWechat = QPushButton('登录微信')
        self.button_loginWechat.clicked.connect(self.loginWechat)
        self.layout.addWidget(self.button_loginWechat,2,3)

        self.button_music = QPushButton('点歌')
        self.button_music.clicked.connect(self.music)
        self.layout.addWidget(self.button_music,2,1)

        self.button_translate = QPushButton('翻译')
        self.button_translate.clicked.connect(self.translate)
        self.layout.addWidget(self.button_translate,2,2)

        self.button_ocr = QPushButton('文字识别')
        self.button_ocr.clicked.connect(self.ocr)
        self.layout.addWidget(self.button_ocr,2,4)

        self.button_yolo = QPushButton('物体识别')
        self.button_yolo.clicked.connect(self.yolo)
        self.layout.addWidget(self.button_yolo,2,5)

        self.timer_refresh = QTimer()
        self.timer_refresh.timeout.connect(self.refresh)
        self.timer_refresh.start(1000)

    def music(self):
        if not self.running :
            return
        self.va.toMusic()
 
    def translate(self):
        if not self.running :
            return
        self.va.toTranslate()

    def ocr(self):
        if not self.running :
            return
        self.va.toOCR()

    def yolo(self):
        if not self.running :
            return
        self.va.toYOLO()

    def loginWechat(self):
        if not self.running:
            return
        self.va.loginWechat()
    def refresh(self):
        self.text_user_content.clear()
        self.text_user_content.append(self.va.user_content)
        self.text_assistant_content.clear()
        self.text_assistant_content.append(self.va.assistant_content)
        if self.running:
            self.button_switch.setText('关闭语音助手')
        else:
            self.button_switch.setText('开启语音助手')

    def switch_status(self):
        self.running = not self.running
        if self.running:
            Thread(target=self.va.run).start()
            self.button_switch.setText('关闭语音助手')
        else:
            self.va.finish()
            self.button_switch.setText('开启语音助手')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    voice = VoiceGUI()
    voice.show()
    sys.exit(app.exec_())
