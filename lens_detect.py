from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QtCore import *
import cv2, sys, time
import numpy as np
from matplotlib import pyplot as plt

class Test(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cam_Test")
        self.setGeometry(150, 150, 650, 540)
        self.initUI()

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

        self.sldr = QSlider(Qt.Horizontal, self)
        self.sldr.resize(100, 25)
        self.sldr.move(5+105+105+200, 490)
        self.sldr.setMinimum(1)
        self.sldr.setMaximum(30)
        self.sldr.setValue(24)
        self.sldr.valueChanged.connect(self.setFps)

        self.sldr1 = QSlider(Qt.Horizontal, self)
        self.sldr1.resize(100, 25)
        self.sldr1.move(5 + 105 + 105 + 200 + 105, 490)
        self.sldr1.setMinimum(50)
        self.sldr1.setMaximum(500)
        self.sldr1.setValue(300)
        self.sldr1.valueChanged.connect(self.setSens)
        self.show()

    def setFps(self):
        self.fps = self.sldr.value()
        self.prt.setText("FPS" + str(self.fps) + "로 조정합니다.")
        self.timer.stop()
        self.timer.start(1000. / self.fps)

    def setSens(self):
        self.sens = self.sldr1.value()
        self.prt.setText("감도" + str(self.sens) + "로 조정합니다.")

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000. / self.fps)

    def nextFrameSlot(self):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontface.xml')
        _, cam_real = self.cpt.read()
        cam = cv2.cvtColor(cam_real, cv2.COLOR_BGR2RGB)
        cam = cv2.cvtColor(cam, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(cam, 1.3, 5)#얼굴검출 (x,y,w,h)를 return
        cam = cv2.GaussianBlur(cam, (5, 5), 0)
        print(faces)
        #self.img_p = cv2.cvtColor(cam, cv2.COLOR_BGR2GRAY)
        #cv2.imwrite('img_p.jpg', self.img_p)
        #self.compare(self.img_o, self.img_p) 사용X


        #line모두 그리기
        ret, image_binary = cv2.threshold(cam, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        contour, hierarcy = cv2.findContours(image_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        for c in contour:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, peri * 0.0001, True)
            x, y, w, h = cv2.boundingRect(c)

            size = len(approx)
            if size == 4 and 1200 < peri < 2400:
                cv2.imwrite("rectangle.jpg", cam_real)
                print("Camera Detect!!")
                print(peri)#2236
            cv2.line(cam_real, tuple(approx[0][0]), tuple(approx[size - 1][0]), (0, 255, 0), 3)
            for k in range(size - 1):
                cv2.line(cam_real, tuple(approx[k][0]), tuple(approx[k + 1][0]), (0, 255, 0), 3)

        #self.img_o = self.img_p.copy()
        img = QImage(cam_real, cam_real.shape[1], cam_real.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.frame.setPixmap(pix)

    def stop(self):
        self.frame.setPixmap(QPixmap.fromImage(QImage()))
        self.timer.stop()
    '''
    def compare(self, img_o, img_p):
        err = np.sum((img_o.astype("float") - img_p.astype("float")) ** 2)
        err /= float(img_o.shape[0] * img_p.shape[1])
        if(err>=self.sens):
            t = time.localtime()
            self.prt.setText("{}-{}-{} {}:{}:{} 탐지".format(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec))
    '''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test = Test()
    test.show()
    app.exec_()






