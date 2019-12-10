from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import cv2, sys, time
import numpy as np
from matplotlib import pyplot as plt
from playsound import playsound
import bcrypt

class Detect(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cam_Test")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(150, 150, 650, 540)
        self.initUI();
        finish = QAction("Quit", self)
        finish.triggered.connect(self.closeEvent)

    def initUI(self):
        self.cpt = cv2.VideoCapture(0)
        self.fps = 24
        self.sens = 300
        #_, self.img_o = self.cpt.read()
        #cv2.imwrite('img_o.jpg', self.img_o)

        self.frame = QLabel(self)
        self.frame.resize(640, 480)
        self.frame.setScaledContents(True)
        self.frame.move(5, 5)

        self.btn_on = QPushButton("켜기", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5, 490)
        self.btn_on.clicked.connect(self.start)

        self.btn_on = QPushButton("끄기", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5+100+5, 490)
        self.btn_on.clicked.connect(self.stop)

        self.prt = QLabel(self)
        self.prt.resize(200, 25)
        self.prt.move(5+105+105, 490)

        self.prt1 = QLabel(self)
        self.prt1.resize(200, 25)
        self.prt1.move(5+105+105+200, 490)

    def faceDetect(self):
        playsound('1.mp3', False)
        self.prt.setText("얼굴 탐지하였습니다.")
        '''
        login = Login()
        if login.exec_() == QtWidgets.QDialog.Accepted:
            window = Window()
            window.show()
            sys.exit(app.exec_())
        '''
    def faceUnDetect(self):
        self.prt.setText("")

    def camDetect(self):
        playsound('2.mp3', False)
        self.prt1.setText("촬영이 탐지되었습니다.")
        login = Login()
        if login.exec_() == QtWidgets.QDialog.Accepted:
            window = Window()
            window.show()
            sys.exit(app.exec_())

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(int(1000./self.fps))

    def nextFrameSlot(self):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontface.xml')
        _, cam_real = self.cpt.read()
        cam_color = cv2.cvtColor(cam_real, cv2.COLOR_BGR2RGB)
        cam = cv2.cvtColor(cam_real, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(cam, 1.3, 5)#얼굴검출 (x,y,w,h)를 return
        cam = cv2.GaussianBlur(cam, (5, 5), 0)
        if len(faces) != 0:
            self.faceDetect()
        else:
            self.faceUnDetect()

        #line모두 그리기
        ret, image_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        contour, hierarcy = cv2.findContours(image_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for c in contour:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, peri * 0.0001, True)
            x, y, w, h = cv2.boundingRect(c)

            size = len(approx)
            if size == 4 and 2000 < peri:
                cv2.imwrite("Evidence.jpg", cam_real)
                warning = cv2.imread("warning1.jpg", cv2.IMREAD_COLOR)
                cv2.namedWindow("Warning!", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Warning!", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Warning!", warning)
                self.camDetect()
                #print(peri)#2236
            cv2.line(cam_color, tuple(approx[0][0]), tuple(approx[size - 1][0]), (0, 255, 0), 3)
            for k in range(size - 1):
                cv2.line(cam_color, tuple(approx[k][0]), tuple(approx[k + 1][0]), (0, 255, 0), 3)

        img = QImage(cam_color, cam_real.shape[1], cam_real.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.frame.setPixmap(pix)

    def stop(self):
        self.frame.setPixmap(QPixmap.fromImage(QImage()))
        self.timer.stop()

    def closeEvent(self, event):
        close = QMessageBox.question(self, "안내", "종료할 수 없습니다.", QMessageBox.Ok)
        event.ignore()

class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("관리자 로그인")
        self.setWindowIcon(QIcon("icon.png"))
        self.inputID = QtWidgets.QLineEdit(self)
        self.inputPW = QtWidgets.QLineEdit(self)
        self.inputPW.setEchoMode(QtWidgets.QLineEdit.Password)
        self.buttonLogin = QtWidgets.QPushButton('로그인', self)
        self.buttonLogin.clicked.connect(self.handle_login)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.inputID)
        layout.addWidget(self.inputPW)
        layout.addWidget(self.buttonLogin)
        finish = QAction("Quit", self)
        finish.triggered.connect(self.closeEvent)

    def closeEvent(self, event):
        close = QMessageBox.question(self, "안내", "종료할 수 없습니다.", QMessageBox.Ok)
        event.ignore()

    def login_check(self):
        for line in open("security.gif","r").readlines():
            login_info = line.split()
            if self.inputID.text() == login_info[0] and self.inputPW.text() == login_info[1]:
                return True
        return False
    
    def handle_login(self):
        if (self.login_check() == True):
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, '오류', '아이디나 비밀번호가 틀렸습니다.')

class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    detect = Detect()
    detect.show()
    app.exec_()






