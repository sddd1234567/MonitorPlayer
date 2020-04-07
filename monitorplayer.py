from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

from MainWindow import Ui_MainWindow
import time
from PyQt5 import QtCore
from threading import Thread

class FloatingWidget(QWidget):
    def __init__(self):
        super(FloatingWidget, self).__init__()        
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

def hhmmss(ms):
    # s = 1000
    # m = 60000
    # h = 360000
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, _ = divmod(r, 1000)
    return ("%d:%02d:%02d" % (h, m, s)) if h else ("%d:%02d" % (m, s))



class ControlPanel(FloatingWidget):
    def __init__(self, player, window, videoWidget):
        super(ControlPanel, self).__init__()        
        self.isMouseFocused = False
        self.initUI(videoWidget)
        self.player = player
        # self.setParent(window)

    def initUI(self, videoWidget):
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color:rgba(0,0,0,70%);")
        self.container.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)

        sliderContainer = QWidget()

        self.timeSlider = QSlider(Qt.Horizontal, self)
        self.timeSlider.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.timeSlider.valueChanged.connect(videoWidget.setPosition)

        sliderLayout = QHBoxLayout()
        sliderLayout.setContentsMargins(3,0,3,0)
        self.startTimeLabel = QLabel("0:00")
        self.stopTimeLabel = QLabel("2:22")
        sliderLayout.addWidget(self.startTimeLabel)
        sliderLayout.addWidget(self.timeSlider)
        sliderLayout.addWidget(self.stopTimeLabel)

        sliderContainer.setLayout(sliderLayout)
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(sliderContainer)
        layout.addWidget(self.container)
        self.setLayout(layout)

        playButton = QPushButton()
        playButton.setIcon(QIcon("./images/icons/play.png"))
        playButton.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)
        playButton.setFlat(True)
        playButton.clicked.connect(videoWidget.play)

        pauseButton = QPushButton()
        pauseButton.setIcon(QIcon("./images/icons/pause.png"))
        pauseButton.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)
        pauseButton.setFlat(True)
        pauseButton.clicked.connect(videoWidget.pause)

        stopButton = QPushButton()
        stopButton.setIcon(QIcon("./images/icons/stop.png"))
        stopButton.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)
        stopButton.setFlat(True)
        stopButton.clicked.connect(videoWidget.stop)

        fasterButton = QPushButton()
        fasterButton.setIcon(QIcon("./images/icons/faster.png"))
        fasterButton.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)
        fasterButton.setFlat(True)
        fasterButton.clicked.connect(videoWidget.faster)

        slowerButton = QPushButton()
        slowerButton.setIcon(QIcon("./images/icons/slower.png"))
        slowerButton.setSizePolicy(
             QSizePolicy.Expanding, QSizePolicy.Expanding)
        slowerButton.setFlat(True)
        slowerButton.clicked.connect(videoWidget.slower)

        layout = QHBoxLayout()
        layout.addWidget(slowerButton)
        layout.addWidget(playButton)
        layout.addWidget(pauseButton)
        layout.addWidget(stopButton)
        layout.addWidget(fasterButton)
        self.container.setLayout(layout)

    def enterEvent(self,e):
        self.isMouseFocused = True
    
    def leaveEvent(self, e):
        self.isMouseFocused = False

class VideoWidget(QVideoWidget):
    def __init__(self):
        super(VideoWidget, self).__init__()
        self.offset = None
        self.size = None
        self.endTime = 0
        self.startTime=0
        self.speed = 1
        self.isFocused = False
    
    def enterEvent(self,e):
        self.window.displayAllUI(False)
        self.isFocused = True
        self.displayUI(True)
    
    def leaveEvent(self, e):
        self.isFocused = False

    def resizeEvent(self, e):
        self.updateSize(e.size())

    def updateSize(self,size = None):
        if size != None:
            self.size = size
        if self.offset != None and self.size != None:
            x = (self.size.width() + 6) * (self.id % 3) + self.offset.x() + 11
            y = (self.size.height() + 6) * int((self.id / 3)) + self.size.height() + self.offset.y() - 28
            self.ui.move(x,y)
            self.speedLabelContainer.move(x + self.size.width() - 33,(self.size.height() + 6) * int((self.id / 3)) + self.offset.y() + 36)
            self.speedLabelContainer.resize(self.size.width(), self.size.height())
            self.speedLabel.resize(self.size.width(), 20)
            self.ui.resize(self.size.width(), 50)

    def updatePos(self, pos):
        self.offset = pos
        self.updateSize()

    def initPlayer(self, num, videoFrame):
        newPlayer = QMediaPlayer()
        newPlayer.setVideoOutput(self)
        newPlayer.setMuted(True)
        newPlayer.durationChanged.connect(self.onDurationChanged)
        newPlayer.positionChanged.connect(self.positionChanged)
        newPlayer.positionChanged.connect(self.updatePosition)
        newPlayer.playbackRateChanged.connect(self.playbackRateChanged)
        self.player = newPlayer
        self.id = num
        self.videoFrame = videoFrame
        return newPlayer

    def setPosition(self, position):
        self.player.setPosition(self.startTime + position)

    def positionChanged(self, position):
        if self.endTime > 0:
            if position >= self.endTime :
                self.stop()

    def playbackRateChanged(self,rate):
        self.displaySpeed(True)

    def initUI(self, window):
        self.ui = ControlPanel(self.player, window, self)
        self.speedLabelContainer = FloatingWidget()
        self.speedLabelContainer.setContentsMargins(0,0,0,0)
        self.speedLabel = QLabel("1x",self.speedLabelContainer)
        self.speedLabel.setStyleSheet("color:white;")
        self.speedLabel.setFont(QFont("Roman times",10,QFont.Bold))
        self.speedLabelContainer.resize(200,60)
        self.window = window
    
    def onDurationChanged(self, duration):
        self.duration = duration
        # if duration > 0:
        #     self.startPlay()

    def startPlay(self):
        duration = self.player.duration()
        if duration > 0:
            self.segmentVideo(duration)
            self.player.play()

    def segmentVideo(self, totalDuration):
        self.endTime = (totalDuration / 9) * (self.id + 1)
        self.startTime = (int(totalDuration / 9) * self.id)
        self.player.setPosition(int(totalDuration / 9) * self.id)

        self.ui.timeSlider.setMaximum(int(totalDuration / 9))
        self.ui.stopTimeLabel.setText(hhmmss(self.endTime))

    def displayUI(self, isVisible):
        if self.player.isVideoAvailable() == False:
            return

        self.ui.setVisible(isVisible)
        self.ui.raise_()

        if isVisible == False or self.speed != 1:
            self.displaySpeed(isVisible)

    def displaySpeed(self, isVisible):
        self.speedLabelContainer.setVisible(isVisible)
        self.speedLabelContainer.raise_()

    def play(self):
        if self.player.state() == QMediaPlayer.StoppedState:
            self.startPlay()
        elif self.duration > 0:
            self.player.play()

    def stop(self):
        self.player.stop()
        self.player.setPlaybackRate(1)

    def pause(self):
        self.player.pause()

    def faster(self):
        if self.speed < 4:
            if self.speed < 1:
                self.speed = self.speed * 2
                if self.speed >= 1:
                    self.speed = int(self.speed)
            else:
                self.speed = self.speed + 1
        
        self.player.setPlaybackRate(self.speed)            
        self.speedLabel.setText(str(self.speed) + "x")

    def slower(self):
        if self.speed > 1:
            self.speed = self.speed- 1
        else:
            self.speed = self.speed/ 2.0

        self.player.setPlaybackRate(self.speed)        
        self.speedLabel.setText(str(self.speed) + "x")
        
    def updatePosition(self, position):
        self.ui.startTimeLabel.setText(hhmmss(position))
        self.ui.timeSlider.blockSignals(True)
        self.ui.timeSlider.setValue(position - self.startTime)
        self.ui.timeSlider.blockSignals(False)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.initMainControlPanel()
        self.setMinimumSize(1226,796)
        self.open_file_action.triggered.connect(self.open_file)
        self.players = []
        self.playerWidgets = []
        self.setAcceptDrops(True)
        self.initPlayers()
        self.show()
        self.centralWidget.setHandler(self.onMouseLeaveFrame)

    def initMainControlPanel(self):
        playButton = QPushButton()
        playButton.setIcon(QIcon("./images/icons/play.png"))
        playButton.setFlat(True)
        playButton.clicked.connect(self.playAll)

        pauseButton = QPushButton()
        pauseButton.setIcon(QIcon("./images/icons/pause.png"))
        pauseButton.setFlat(True)
        pauseButton.clicked.connect(self.pauseAll)

        stopButton = QPushButton()
        stopButton.setIcon(QIcon("./images/icons/stop.png"))
        stopButton.setFlat(True)
        stopButton.clicked.connect(self.stopAll)

        fasterButton = QPushButton()
        fasterButton.setIcon(QIcon("./images/icons/faster.png"))
        fasterButton.setFlat(True)
        fasterButton.clicked.connect(self.fasterAll)

        slowerButton = QPushButton()
        slowerButton.setIcon(QIcon("./images/icons/slower.png"))
        slowerButton.setFlat(True)
        slowerButton.clicked.connect(self.slowerAll)

        self.controlPanelLayout.setContentsMargins(6,10,6,10)
        self.controlPanelLayout.addWidget(slowerButton)
        self.controlPanelLayout.addWidget(playButton)
        self.controlPanelLayout.addWidget(pauseButton)
        self.controlPanelLayout.addWidget(stopButton)
        self.controlPanelLayout.addWidget(fasterButton)


    def onMouseLeaveFrame(self):
        self.displayAllUI(False)
    
    def initPlayers(self):
        count = 0
        for i in range(0, 3):
            for j in range(0, 3):
                videoWidget = VideoWidget()
                videoWidget.setSizePolicy(
                    QSizePolicy.Expanding, QSizePolicy.Expanding)
                self.videoFrame.addWidget(videoWidget, i, j)
                player = videoWidget.initPlayer(count, self.videoFrame)
                videoWidget.initUI(self)
                self.players.append(player)
                self.playerWidgets.append(videoWidget)
                count+=1

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.setVideoUrl(QMediaContent(url))

    def mousePressEvent(self, event):
        self.raiseAllUI()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open file", "", "mp3 Audio (*.mp3);mp4 Video (*.mp4);Movie files (*.mov);All files (*.*)")

        if path:
            self.setVideoUrl(QMediaContent(QUrl.fromLocalFile(path)))
    
    def setVideoUrl(self, url):
        for player in self.players:
            player.setMedia(url)

    def playAll(self):
        for vw in self.playerWidgets:
            vw.play()

    def pauseAll(self):
        for vw in self.playerWidgets:
            vw.pause()

    def stopAll(self):
        for vw in self.playerWidgets:
            vw.stop()

    def fasterAll(self):
        def run() :
            for vw in self.playerWidgets:
                vw.faster()
                time.sleep(0.1)
        
        Thread(target = run).start()
        

    def slowerAll(self):
        def run() :
            for vw in self.playerWidgets:
                vw.slower()
                time.sleep(0.1)

        Thread(target = run).start()
    
    def moveEvent(self, e):
        self.updateControlPanel(e.pos())

    def updateControlPanel(self, pos):
        for vw in self.playerWidgets:
            vw.updatePos(pos)

    def raiseAllUI(self):
        for vw in self.playerWidgets:
            vw.ui.raise_()
            vw.speedLabelContainer.raise_()

    def displayAllUI(self, isShown):
        for vw in self.playerWidgets:
            vw.displayUI(isShown)

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