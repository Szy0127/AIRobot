import sys
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QPushButton, QGridLayout
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

        self.label_user_content = QLabel()
        self.layout.addWidget(self.label_user_content,3,2)
        self.label_assistant_content = QLabel()
        self.layout.addWidget(self.label_assistant_content,4,2)
       
        self.button_switch = QPushButton('开启语音助手')
        self.button_switch.clicked.connect(self.switch_status)
        self.layout.addWidget(self.button_switch,1,1)
        
       
        self.button_loginWechat = QPushButton('登录微信')
        self.button_loginWechat.clicked.connect(self.va.loginWechat)
        self.layout.addWidget(self.button_loginWechat,2,3)

        self.button_music = QPushButton('点歌')
        self.button_music.clicked.connect(self.va.toMusic)
        self.layout.addWidget(self.button_music,2,1)

        self.button_translate = QPushButton('翻译')
        self.button_translate.clicked.connect(self.va.toTranslate)
        self.layout.addWidget(self.button_translate,2,2)

        self.timer_refresh = QTimer()
        self.timer_refresh.timeout.connect(self.refresh)
        self.timer_refresh.start(1000)

    def loginWechat(self):
        self.va.loginWechat()
    def refresh(self):
        self.label_user_content.setText(self.va.user_content)
        self.label_assistant_content.setText(self.va.assistant_content)
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
