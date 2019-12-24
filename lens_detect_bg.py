from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import cv2, sys, time
from playsound import playsound

class screenguard():
    def __init__(self):
        self.login = Login()
        self.cam = cv2.VideoCapture(0)
        self.index = 1

    def lensDetect(self):
        while True:
            _, fr = self.cam.read()
            frame = cv2.cvtColor(fr, cv2.COLOR_RGB2GRAY)
            frame = cv2.GaussianBlur(frame, (5, 5), 0)
            ret, frame_binary = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
            contour, hierarcy = cv2.findContours(frame_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for c in contour:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, peri * 0.0001, True)

                size = len(approx)
                if size == 4 and 2000 < peri:  # print(peri)#2236
                    cv2.imwrite("proof " + str(self.index) + ".jpg", fr)
                    self.index += 1
                    self.camDetect()
            time.sleep(1)

    def camDetect(self):
        warning = cv2.imread("C:\Python\web_cam\warning.jpg", cv2.IMREAD_COLOR)
        cv2.namedWindow("Warning!", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Warning!", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow("Warning!", warning)
        playsound('C:\Python\web_cam\siren.mp3', False)
        self.login.exec_()

class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle("관리자 로그인")
        self.setWindowIcon(QIcon("C:\Python\web_cam\icon.png"))
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

    def handle_login(self):
        if (self.login_check() == True):
            cv2.destroyAllWindows()
            self.inputID.setText("")
            self.inputPW.setText("")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, '오류', '아이디나 비밀번호가 틀렸습니다.')

    def login_check(self):
        for line in open("C:\Python\web_cam\security.jpg", "r").readlines():
            login_info = line.split()
            if self.inputID.text() == login_info[0] and self.inputPW.text() == login_info[1]:
                return True
        return False

def main():
    print("Screen Guard On")
    sg = screenguard()
    sg.lensDetect()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()
    app.exec_()
