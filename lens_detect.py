from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import cv2, sys
from playsound import playsound
import hashlib, binascii, os
import bz2, bcrypt

class Detect(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Guarder")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(150, 150, 650, 540)
        self.setFixedSize(650,540)
        self.initUI()
        finish = QAction("Quit", self)
        finish.triggered.connect(self.closeEvent)

    def initUI(self):
        self.introduction = open("introduction.txt", "r").read()
        self.manual = open("manual.txt","r").read()
        self.cpt = cv2.VideoCapture(0)
        self.fps = 24
        self.sens = 300

        self.mainframe = QLabel(self.introduction,self)
        self.mainframe.resize(400,480)
        self.mainframe.setScaledContents(True)
        self.mainframe.move(125,5)

        self.frame = QLabel(self)
        self.frame.resize(100, 100)
        self.frame.setScaledContents(True)
        self.frame.setPixmap(QPixmap('icon.png'))
        self.frame.move(500, 5)

        self.btn_intro = QPushButton("소개", self)
        self.btn_intro.resize(100, 25)
        self.btn_intro.move(5, 25)
        self.btn_intro.clicked.connect(self.intro)

        self.btn_manual = QPushButton("매뉴얼", self)
        self.btn_manual.resize(100, 25)
        self.btn_manual.move(5, 75)
        self.btn_manual.clicked.connect(self.showmanual)

        self.btn_on = QPushButton("켜기", self)
        self.btn_on.resize(100, 25)
        self.btn_on.move(5, 125)
        self.btn_on.clicked.connect(self.start)

        self.btn_off = QPushButton("끄기", self)
        self.btn_off.setEnabled(False)
        self.btn_off.resize(100, 25)
        self.btn_off.move(5, 175)
        self.btn_off.clicked.connect(self.stop)

        self.btn_pw = QPushButton("패스워드 관리",self)
        self.btn_pw.resize(100, 25)
        self.btn_pw.move(5, 440)
        self.btn_pw.clicked.connect(self.manage_password)

        self.btn_end = QPushButton("종료", self)
        self.btn_end.resize(100, 25)
        self.btn_end.move(5, 490)
        self.btn_end.clicked.connect(self.end)


        self.prt = QLabel(self)
        self.prt.resize(200, 25)
        self.prt.move(5+105+105, 490)

        self.prt1 = QLabel(self)
        self.prt1.resize(200, 25)
        self.prt1.move(5+105+105+200, 490)

    def intro(self):
        self.mainframe.setText(self.introduction)

    def showmanual(self):
        self.mainframe.setText(self.manual)

    def end(self):
        sys.exit(0)

    def manage_password(self):
        pw = Password()
        pw.exec_()

    def faceDetect(self):
        self.prt.setText("얼굴 인식")

    def faceUnDetect(self):
        self.prt.setText("")

    def camDetect(self):
        #playsound('.mp3\\2.mp3', False)
        warning = cv2.imread("warning.jpg", cv2.IMREAD_COLOR)
        cv2.namedWindow("Warning!", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Warning!", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Warning!", warning)
        playsound('siren.mp3', False)
        self.prt1.setText("촬영이 탐지되었습니다.")
        login = Login()
        login.exec_()


    def start(self):
        self.btn_off.setEnabled(True)
        self.timer = QTimer()
        self.timer.start()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.nextFrameSlot)

    def nextFrameSlot(self):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontface.xml')#.xml\\
        _, cam_real = self.cpt.read()
        cam_color = cv2.cvtColor(cam_real, cv2.COLOR_BGR2RGB)
        cam = cv2.cvtColor(cam_real, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(cam, 1.3, 5)#얼굴검출 (x,y,w,h)를 return
        cam = cv2.GaussianBlur(cam, (5, 5), 0)
        #print(faces);
        if len(faces) != 0:
            self.faceDetect()
        else:
            self.faceUnDetect()

        ret, image_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        contour, hierarcy = cv2.findContours(image_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for c in contour:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, peri * 0.0001, True)
            x, y, w, h = cv2.boundingRect(c)
            size = len(approx)
            if size == 4 and 2000 < peri: #print(peri)#2236
                cv2.imwrite("Evidence.jpg", cam_real)
                self.camDetect()
        #     Line 그리기
        #     cv2.line(cam_color, tuple(approx[0][0]), tuple(approx[size - 1][0]), (0, 255, 0), 3)
        #     for k in range(size - 1):
        #         cv2.line(cam_color, tuple(approx[k][0]), tuple(approx[k + 1][0]), (0, 255, 0), 3)

        img = QImage(cam_color, cam_real.shape[1], cam_real.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.frame.setPixmap(pix)

    def stop(self):
        if self.timer.isActive():
            self.frame.setPixmap(QPixmap('icon.png'))
            self.timer.stop()
            self.btn_off.setEnabled(False)


    def closeEvent(self, event):
        QMessageBox.question(self, "안내", "종료할 수 없습니다.", QMessageBox.Ok)
        event.ignore()

class Password(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Password, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("패스워드 등록")
        self.setWindowIcon(QIcon(".img\\icon.png"))
        self.inputID = QtWidgets.QLineEdit(self)
        self.inputPW = QtWidgets.QLineEdit(self)
        self.inputPW.setEchoMode(QtWidgets.QLineEdit.Password)
        self.buttonLogin = QtWidgets.QPushButton('등록', self)
        self.buttonLogin.clicked.connect(self.manage_pw)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.inputID)
        layout.addWidget(self.inputPW)
        layout.addWidget(self.buttonLogin)

    def manage_pw(self):
        f = open("security.jpg","a")
        f.write(str(self.inputID.text()))
        f.write(" ")
        bc_pw = bcrypt.hashpw(self.inputPW.text().encode(), bcrypt.gensalt())
        f.write(str(bc_pw))
        f.write("\n")
        QtWidgets.QMessageBox.warning(self, '완료', '등록이 완료 되었습니다.')
        self.accept()

        # bz2_pw = bz2.compress(self.inputPW.text().encode())
        # f.write(str(bz2_pw))

class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("관리자 로그인")
        self.setWindowIcon(QIcon(".img\\icon.png"))
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
        QMessageBox.question(self, "안내", "종료할 수 없습니다.", QMessageBox.Ok)
        event.ignore()

    def login_check(self):
        for line in open("security.jpg","r").readlines():
            login_info = line.split()
            # bzpw = login_info[1] + " " + login_info[2]
            # if self.inputID.text() == login_info[0] and str(bz2.compress(self.inputPW.text().encode())) == bzpw:
            #     return True
            #print(self.inputPW.text().encode())
            pw = login_info[1]
            #print(pw[1:-1])
            pw_en = pw[2:-1].encode()
            #print(pw_en)
            if self.inputID.text() == login_info[0] and bcrypt.checkpw(self.inputPW.text().encode(), pw_en):
                return True
        return False
    
    def handle_login(self):
        if (self.login_check() == True):
            cv2.destroyAllWindows()
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, '오류', '아이디나 비밀번호가 틀렸습니다.')




if __name__ == "__main__":
    app = QApplication(sys.argv)
    detect = Detect()
    detect.show()
    app.exec_()






