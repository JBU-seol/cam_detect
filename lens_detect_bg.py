from PyQt5.QtWidgets import *
from PyQt5.QtGui import  *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import cv2, sys, time, os
import numpy as np
import tensorflow
from PIL import Image
from playsound import playsound
import bcrypt

class screenguard():
    def __init__(self):
        self.login = Login()
        self.cam = cv2.VideoCapture(0)
        self.index = 1
        np.set_printoptions(suppress=True)

        # Load the model
        self.model = tensorflow.keras.models.load_model('keras_model.h5', compile= False)

        # Create the array of the right shape to feed into the keras model
        # The 'length' or number of images you can put into the array is
        # determined by the first position in the shape tuple, in this case 1.
        self.data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    def lensDetect(self):
        while True:
            _, frame = self.cam.read()
            cv2.imwrite("a.jpg", frame)
            image = Image.open("a.jpg")
            # Make sure to resize all images to 224, 224 otherwise they won't fit in the array
            image = image.resize((224, 224))
            image_array = np.asarray(image)
            # Normalize the image
            normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
            # Load the image into the array
            self.data[0] = normalized_image_array
            # run the inference
            prediction = self.model.predict(self.data)
            pred = str(prediction[0])
            if int(pred[3:6]) >= 800:
                cv2.imwrite("proof " + str(self.index) + ".jpg", frame)
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
            pw = login_info[1]
            pw_en = pw[2:-1].encode()
            if self.inputID.text() == login_info[0] and bcrypt.checkpw(self.inputPW.text().encode(), pw_en):
                return True
        return False

def main():
    print("Screen Guard On")
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    sg = screenguard()
    sg.lensDetect()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main()
    app.exec_()
