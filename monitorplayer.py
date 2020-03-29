from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from MainWindow import Ui_MainWindow
import time
from PyQt5 import QtCore

class VideoWidget(QVideoWidget):
    def __init__(self):
        super(VideoWidget, self).__init__()
    
    def enterEvent(self,e):
        print("on mouse hover")

    def initPlayer(self, num):
        newPlayer = QMediaPlayer()
        newPlayer.setVideoOutput(self)
        newPlayer.setVolume(0)
        newPlayer.durationChanged.connect(self.onDurationChanged)
        self.player = newPlayer
        self.id = num
        return newPlayer
    
    def onDurationChanged(self, duration):
        if duration > 0:
            print("on duration changed")
            self.player.play()
            self.segmentVideo(duration)

    def segmentVideo(self, totalDuration):
        print("segment videos")
        self.player.setPosition((totalDuration / 9) * self.id)
        

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setMouseTracking(True)
        self.open_file_action.triggered.connect(self.open_file)
        self.players = []
        self.setAcceptDrops(True)
        self.initPlayers()
        self.show()

    
    def initPlayers(self):
        count = 0
        for i in range(0, 3):
            for j in range(0, 3):
                videoWidget = VideoWidget()
                videoWidget.setSizePolicy(
                    QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.videoFrame.addWidget(videoWidget, i, j)
                player = videoWidget.initPlayer(count)
                self.players.append(player)
                count+=1


    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.setVideoUrl(QMediaContent(url))

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "mp3 Audio (*.mp3);mp4 Video (*.mp4);Movie files (*.mov);All files (*.*)")

        if path:
            self.setVideoUrl(QMediaContent(QUrl.fromLocalFile(path)))
    
    def setVideoUrl(self, url):
        for player in self.players:
            player.setMedia(url)

    def playAll(self):
        for player in self.players:
            player.play()

    def play(self, num):
        self.players[num].play()


if __name__ == '__main__':
    app = QApplication([])
    app.setApplicationName("VideoPlayer")
    app.setStyle("Fusion")

    # Fusion dark palette from https://gist.github.com/QuantumCD/6245215.
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    app.setStyleSheet(
        "QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    window = MainWindow()
    app.exec_()