
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
from functools import partial
import os
import threading
import pygame.mixer as pm
import math
import pygame
import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery




class MultiTask(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.database = DataBase()
        self.filename = "data/music.txt"
        self.folders = [
            'C:\\Users\SUC\Downloads',
            'C:\\Users\SUC\Desktop',
            'C:\\Users\SUC\Music'
        ]

    def run(self):
        with open(self.filename, 'w+') as filewriter:
            for folder in self.folders:
                for r, d, f in os.walk(folder):
                    for file in f:
                        if file.endswith(".mp3"):
                            music = "{}\{}\n".format(r, file)
                            # filewriter.write(music)
                            self.database.addMusic(music)



class DataBase():
    def __init__(self):
        self.folders = [
            'C:\\Users\SUC\Downloads',
            'C:\\Users\SUC\Desktop',
            'C:\\Users\SUC\Music'
        ]
        self.con = QSqlDatabase.addDatabase("QSQLITE")
        self.con.setDatabaseName("data/musicplayer")
        self.con.open()
        
        if not self.con.open():
            print("Database cannot Conected successfully")
        self.createTable()


    def createTable(self):
        createTableQuery = QSqlQuery()
        createTableQuery.exec("""
            CREATE TABLE IF NOT EXISTS musiclist (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                music TEXT NOT NULL
            )
            """)
        createTableQuery.exec("""
            CREATE TABLE IF NOT EXISTS musicfolder (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                folder TEXT NOT NULL
            )
            """)
        print(self.con.tables())
    
    def fetchMusic(self):
        query = QSqlQuery()
        query.exec(
            f"""SELECT * FROM musiclist"""
        )
        query.last()
        query = query.value(1).split("\n")
        return query
    
    def searchMusic(self):
        old_music = self.fetchMusic()
        all_music = []
        for folder in self.folders:
            for r, d, f in os.walk(folder):
                for file in f:
                    if file.endswith(".mp3"):
                        music = "{}\{}\n".format(r, file)
                        if not music in old_music:
                            all_music.append(music)
        all_music = "".join(all_music)
        self.addMusic(all_music)
        # print(all_music)

    def clearMusic(self):
        query = QSqlQuery()
        query.exec(
            f"""DELETE * FROM musiclist"""
        )
        
    def addMusic(self, music):
        self.clearMusic()
        query = QSqlQuery()
        query.exec(
            f"""INSERT INTO musiclist (music)
              VALUES ('{music}')"""
        )


class SettingsView():
    def __init__(self, parent):
        self.general_layout = parent.generalLayout
        self.createUI()

    def createUI(self):
        self.general_layout.addWidget(QLabel("Settings Layout"))
        


class NowPlayingView():
    def __init__(self, parent):
        self.general_layout = parent.generalLayout
        self.createThumbnail(self.general_layout)
        self.createSLider()
        self.createMusicButton()


    def createThumbnail(self, layout):
        frm = QGridLayout()
        frm.addWidget(QLabel(), 0, 0)
        self.image = QLabel()
        self.image.setFixedSize(400, 400)
        self.image.setPixmap(self.setPlayingImage())
        self.image.setStyleSheet('padding-top:10px')
        self.image.move(180,0)
        frm.addWidget(self.image,0,1)
        frm.addWidget(QLabel(),0,2)
        layout.addLayout(frm)

    def setPlayingImage(self):
        try:
            music_file = self.all_music[self.current_playing_pos]
            pixmap = self.extractThumbnail(music_file)
            pixmap = pixmap.scaledToHeight(400)
            pixmap = pixmap.scaledToHeight(400)
            # pixmap.setDevicePixelRatio(10)
            # self.image.setPixmap(pixmap)
            return pixmap
        except:
            pixmap = QPixmap("image/now.jpg")
            pixmap = pixmap.scaledToHeight(400)
            pixmap = pixmap.scaledToHeight(400)
            return pixmap

    def extractThumbnail(self, music_file):
        import mutagen
        pixmap = QPixmap()
        metadata = mutagen.File(music_file)
        for tag in metadata.tags.values():
            if tag.FrameID == 'APIC':
                pixmap.loadFromData(tag.data)
                break
        return pixmap

    def createSLider(self):
        self.playing_text = QLabel(str("Hello all"))
        self.playing_text.setAlignment(Qt.AlignCenter)
        self.playing_text.setObjectName("playing_text")
        self.general_layout.addWidget(self.playing_text)

        # sound = pm.Sound(self.all_music[self.current_playing_pos])
        # length = sound.get_length()
        length = 188

        frm = QHBoxLayout()
        self.initial_time = QLabel("0:00")
        frm.addWidget(self.initial_time)
        self.slider = QSlider(Qt.Horizontal, objectName="slider")
        self.slider.setValue(0)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int(length))
        # self.slider.valueChanged.connect(self.changeMusicPosition)
        # self.slider.sliderMoved.connect(self.sliderMoved)
        # self.slider.sliderReleased.connect(self.sliderRelease)
        frm.addWidget(self.slider)
        self.final_time = QLabel("3:20")
        self.final_time.setText(self.sec2time(length))
        frm.addWidget(self.final_time)
        self.general_layout.addLayout(frm)

    def sec2time(self, length):
        min = math.floor(length/60)
        sec = math.ceil(length - (min*60))
        return "{}:{}".format(min,sec if sec > 9 else "0" + str(sec))

    def createMusicButton(self):
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        rep_btn = self.createNavBtn(30, 30, 'repeat.png', 'repeat_btn')
        prv_btn = self.createNavBtn(50, 50, 'prev.png', 'prev_btn')
        self.play_btn = self.createNavBtn(80, 80, 'play.png', 'play_btn')
        self.pause_btn = self.createNavBtn(80, 80, 'pause.png', 'pause_btn')
        next_btn = self.createNavBtn(50, 50, 'next.png', 'next_btn')
        shuf_btn = self.createNavBtn(30, 30, 'shuffle.png', 'shuf_btn')

        btn_layout.addWidget(QLabel(), 1)
        btn_layout.addWidget(rep_btn, 1)
        btn_layout.addWidget(prv_btn, 1)
        btn_layout.addWidget(self.play_btn, 1)
        btn_layout.addWidget(self.pause_btn, 1)
        btn_layout.addWidget(next_btn, 1)
        btn_layout.addWidget(shuf_btn, 1)
        self.vol_slider = QSlider(Qt.Horizontal, objectName="volslider")
        self.vol_slider.setValue(10)
        # self.vol_slider.valueChanged.connect(self.volumeChange)
        self.vol_slider.setMaximum(100)
        btn_layout.addWidget(self.vol_slider, 1)
        self.pause_btn.hide()
        self.general_layout.addLayout(btn_layout)

    def createNavBtn(self, x, y, image, objectname):
        rep_btn = QPushButton(objectName=objectname)
        rep_btn.setIcon(QIcon('image/{image}'.format(image=image)))
        rep_btn.setIconSize(QSize(x,y))
        rep_btn.setCursor(QCursor(Qt.PointingHandCursor))
        # rep_btn.clicked.connect(partial(self.musicButtonClicked, rep_btn))
        return rep_btn
    
class MusicListView():
    def __init__(self, parent):
        self.parent = parent
        self.createMusicList()

    def createMusicList(self):
        self.scroll = QScrollArea(objectName="scroll_area")   
        self.scroll.setStyleSheet("""QWidget{ background-color: transparent }
         QScrollBar{ background-color: none;  }""")
        self.widget = QWidget()                
        self.vbox = QVBoxLayout()
        self.addMusicToList()
        self.widget.setLayout(self.vbox)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.parent.music_list_layout.addWidget(self.scroll)

    def addMusicToList(self):
        i = 0
        for music in self.parent.all_music:
            widg = QWidget()
            widg.setCursor(QCursor(Qt.PointingHandCursor))  
            lay = QHBoxLayout()
            music = music.split("\\")
            music = music[-1]    
            music = music.split(".")
            music = ".".join(music[:-1])
            pers_music = str(music)
            music_btn = QPushButton(pers_music)
            music_btn.setStyleSheet("""
                QPushButton{background:transparent; font-size:14px; text-align:left}
            """)
            music_btn.clicked.connect(partial(self.parent.clickedMusic, i))

            if self.parent.current_playing_pos == i:
                self.setPlayingRow(widg, music_btn, True)
            else:
                self.setPlayingRow(widg, music_btn, False)

            music_btn.setIconSize(QSize(30, 30))
            self.parent.all_music_row.append([widg, music_btn])
            lay.addWidget(music_btn, 10)

            object = QPushButton("...")
            object.setStyleSheet("background:transparent; font-size:17px")
            lay.addWidget(object, 1)
            widg.setLayout(lay)
            self.vbox.addWidget(widg)
            i+=1


    def setPlayingRow(self, widg, music_btn, isplaying):
        if isplaying:
            music_btn.setIcon(QIcon('image/{}'.format("musiciconplaying.png")))
            widg.setStyleSheet("""
                QWidget:hover{background-color:#ff4444}
                QWidget{border-bottom: 1px solid gray; padding:0;margin:0;background-color:red;color:black}
            """)
        else:
            music_btn.setIcon(QIcon('image/{}'.format("musicicon.png")))
            widg.setStyleSheet("""
                QWidget:hover{background-color:#ff4444}
                QWidget{border-bottom: 1px solid gray; padding:0;margin:0;background-color:none;color:white}
            """)





class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        # file_write = MultiTask()
        # file_write.start()
        self.database = DataBase()
        self.database.searchMusic()

        self.initUi()
        self.setDefaults()
        self.fetchMusic()
        self.showTime(self.generalLayout)
        self.createtabs()
        # self.createMusicList()

        # self._update_timer = QTimer()
        # self._update_timer.timeout.connect(self.updateUi)
        # self._update_timer.start(500)
        # file_write.join()
          
    def setDefaults(self):
        # pm.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pm.init()
        pm.music.set_volume(0.1)
        self.current_playing_pos = 1
        self.previous_playing_pos = 0
        self.is_music_playing = False
        self.all_music_row = []
        self.is_sliding = False

    def initUi(self):
        self.setWindowTitle('Music Player')
        self.setGeometry(350, 50, 700, 300)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        style = open('style.css').read()
        self._centralWidget.setStyleSheet('background:black;color:white')
        self.setStyleSheet(style)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        
    def fetchMusic(self):
        self.all_music = []
        self.all_music = self.database.fetchMusic()
        self.all_music.pop()
    
    def createtabs(self):
        tabs = QTabWidget(objectName="nav_tab")
        tabs.addTab(self.playingTabUI(), "Now Playing")
        tabs.addTab(self.musicTabUI(), "All Songs")
        tabs.addTab(self.playlistTabUI(), "Playlists")
        tabs.addTab(self.settingsTabUI(), "Settings")
        tabs.setCursor(QCursor(Qt.PointingHandCursor))
        self.generalLayout.addWidget(tabs)
        # self.createNowPlaying()
        nowplay = NowPlayingView(self)
        musiclist = MusicListView(self)
        settings = SettingsView(self)


    def playingTabUI(self):
        playingTab = QWidget()
        self.now_playing_layout = QVBoxLayout()
        playingTab.setLayout(self.now_playing_layout)
        return playingTab

    def musicTabUI(self):
        musicTab = QWidget()
        self.music_list_layout = QVBoxLayout()
        musicTab.setLayout(self.music_list_layout)
        return musicTab  
    
    def playlistTabUI(self):
        playlistTab = QWidget()
        self.playlist_layout = QVBoxLayout()
        playlistTab.setLayout(self.playlist_layout)
        return playlistTab  

    def settingsTabUI(self):
        playlistTab = QWidget()
        self.settings_layout = QVBoxLayout()
        playlistTab.setLayout(self.settings_layout)
        return playlistTab  

    def showTime(self, layout):
        current_time = datetime.datetime.now()
        time = "{}:{}:{} {}".format(current_time.hour if current_time.hour < 13 else current_time.hour-12, 
                current_time.minute, 
                current_time.second if current_time.second > 9 else "0" + str(current_time.second), 
                "PM" if current_time.hour > 11 else "AM") 
        self.time = QLabel("{}".format(time))
        self.time.setObjectName('time')
        self.time.setAlignment(Qt.AlignRight)
        layout.addWidget(self.time)
        
    def updateTime(self):
        current_time = datetime.datetime.now()
        hr = current_time.hour if current_time.hour < 13 else current_time.hour-12
        time = "{}:{}:{} {}".format(
                (hr) if hr > 9 else "0" + str(hr), 
                current_time.minute if current_time.minute > 9 else "0" + str(current_time.minute), 
                current_time.second if current_time.second > 9 else "0" + str(current_time.second), 
                "PM" if current_time.hour > 11 else "AM") 
        self.time.setText(time)
    
    def updateSlider(self):
        # if not self.is_sliding:
        current_pos = max(0, pm.music.get_pos()/1000)
        self.slider.setValue(int(current_pos))
        self.initial_time.setText(str(self.sec2time(current_pos)))

    def updateUi(self):
        self.updateTime()
        # self.updateSlider()
        # self.checkSongEnd()
        # self.changeMusicTitle()
        # self.setPlayingImage()

    def checkSongEnd(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                print('down pressed playing')
                

    def updateMusicRow(self):
        widg = self.all_music_row[self.current_playing_pos][0]
        btn = self.all_music_row[self.current_playing_pos][1]
        self.setPlayingRow(widg, btn, True)
        widg = self.all_music_row[self.previous_playing_pos][0]
        btn = self.all_music_row[self.previous_playing_pos][1]
        self.setPlayingRow(widg, btn, False)
        
    def createMusicList(self):
        self.scroll = QScrollArea(objectName="scroll_area")   
        self.scroll.setStyleSheet("""QWidget{ background-color: transparent }
         QScrollBar{ background-color: none;  }""")
        self.widget = QWidget()                
        self.vbox = QVBoxLayout()
        self.addMusicToList()
        self.widget.setLayout(self.vbox)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.widget)
        self.music_list_layout.addWidget(self.scroll)

    def addMusicToList(self):
        i = 0
        for music in self.all_music:
            widg = QWidget()
            widg.setCursor(QCursor(Qt.PointingHandCursor))  
            lay = QHBoxLayout()
            music = music.split("\\")
            music = music[-1]    
            music = music.split(".")
            music = ".".join(music[:-1])
            pers_music = str(music)
            music_btn = QPushButton(pers_music)
            music_btn.setStyleSheet("""
                QPushButton{background:transparent; font-size:14px; text-align:left}
            """)
            music_btn.clicked.connect(partial(self.clickedMusic, i))

            if self.current_playing_pos == i:
                self.setPlayingRow(widg, music_btn, True)
            else:
                self.setPlayingRow(widg, music_btn, False)

            music_btn.setIconSize(QSize(30, 30))
            self.all_music_row.append([widg, music_btn])
            lay.addWidget(music_btn, 10)

            object = QPushButton("...")
            object.setStyleSheet("background:transparent; font-size:17px")
            lay.addWidget(object, 1)
            widg.setLayout(lay)
            self.vbox.addWidget(widg)
            i+=1
           
    def clickedMusic(self, index):
        self.previous_playing_pos = self.current_playing_pos
        self.current_playing_pos = index
        pm.music.stop()
        self.updateFinalMusicTime()
        self.playMusic()
        self.play_btn.hide()
        self.pause_btn.show()
        # print(index)
    
  
    def setPlayingRow(self, widg, music_btn, isplaying):
        if isplaying:
            music_btn.setIcon(QIcon('image/{}'.format("musiciconplaying.png")))
            widg.setStyleSheet("""
                QWidget:hover{background-color:#ff4444}
                QWidget{border-bottom: 1px solid gray; padding:0;margin:0;background-color:red;color:black}
            """)
        else:
            music_btn.setIcon(QIcon('image/{}'.format("musicicon.png")))
            widg.setStyleSheet("""
                QWidget:hover{background-color:#ff4444}
                QWidget{border-bottom: 1px solid gray; padding:0;margin:0;background-color:none;color:white}
            """)


    def extractThumbnail(self, music_file):
        import mutagen
        pixmap = QPixmap()
        metadata = mutagen.File(music_file)
        for tag in metadata.tags.values():
            if tag.FrameID == 'APIC':
                pixmap.loadFromData(tag.data)
                break
        return pixmap
    
    def setPlayingImage(self):
        music_file = self.all_music[self.current_playing_pos]
        pixmap = self.extractThumbnail(music_file)
        pixmap = pixmap.scaledToHeight(400)
        pixmap = pixmap.scaledToHeight(400)
        # pixmap.setDevicePixelRatio(10)
        self.image.setPixmap(pixmap)
        return pixmap


    def createThumbnail(self, layout):
        frm = QGridLayout()
        frm.addWidget(QLabel(), 0, 0)
        self.image = QLabel(self)
        self.image.setFixedSize(400, 400)
        self.setPlayingImage()
        self.image.setStyleSheet('padding-top:10px')
        self.image.move(180,0)
        frm.addWidget(self.image,0,1)
        frm.addWidget(QLabel(),0,2)
        layout.addLayout(frm)

 
    def changeMusicTitle(self):
        music_list = self.all_music[self.current_playing_pos]
        music_list = music_list.split("\\")
        music_list = music_list[-1]
        music_list = music_list.split(".")
        music_list = ".".join(music_list[:-1])
        self.playing_text.setText(str(music_list))

    def createSlider(self, layout):
        music_list = self.all_music[self.current_playing_pos]
        music_list = music_list.split("\\")
        music_list = music_list[-1]
        music_list = music_list.split(".")
        music_list = ".".join(music_list[:-1])
        
        self.playing_text = QLabel(str(music_list))
        self.playing_text.setAlignment(Qt.AlignCenter)
        self.playing_text.setObjectName("playing_text")
        layout.addWidget(self.playing_text)

        sound = pm.Sound(self.all_music[self.current_playing_pos])
        length = sound.get_length()

        frm = QHBoxLayout()
        self.initial_time = QLabel("0:00")
        frm.addWidget(self.initial_time)
        self.slider = QSlider(Qt.Horizontal, objectName="slider")
        self.slider.setValue(0)
        self.slider.setMinimum(0)
        self.slider.setMaximum(int(length))
        self.slider.valueChanged.connect(self.changeMusicPosition)
        self.slider.sliderMoved.connect(self.sliderMoved)
        self.slider.sliderReleased.connect(self.sliderRelease)
        frm.addWidget(self.slider)
        self.final_time = QLabel("3:20")
        self.final_time.setText(self.sec2time(length))
        frm.addWidget(self.final_time)
        layout.addLayout(frm)
    
    def changeMusicPosition(self):
        return
        self.is_sliding = False
        pos = self.slider.value()
        try:
            pm.music.set_pos(pos)
        except:
            pass
        print(f"Pos = {pm.music.get_pos()}")
    
    def sliderMoved(self):
        self.is_sliding = True
    
    def sliderRelease(self):
        self.is_sliding = False
        #  self.is_sliding = False
        pos = self.slider.value()
        try:
            pm.music.set_pos(pos)
        except:
            pass
        print(f"Pos = {pm.music.get_pos()}")

    def updateFinalMusicTime(self):
        sound = pm.Sound(self.all_music[self.current_playing_pos])
        length = sound.get_length()
        self.slider.setMaximum(int(length))
        self.final_time.setText(self.sec2time(length))

    def sec2time(self, length):
        min = math.floor(length/60)
        sec = math.ceil(length - (min*60))
        return "{}:{}".format(min,sec if sec > 9 else "0" + str(sec))

    def createNavBtn(self, x, y, image, objectname):
        rep_btn = QPushButton(objectName=objectname)
        rep_btn.setIcon(QIcon('image/{image}'.format(image=image)))
        rep_btn.setIconSize(QSize(x,y))
        rep_btn.setCursor(QCursor(Qt.PointingHandCursor))
        rep_btn.clicked.connect(partial(self.musicButtonClicked, rep_btn))
        return rep_btn

    def playMusic(self, pos=0):
        try:
            music_file = self.all_music[self.current_playing_pos]
            pm.music.stop()
            pm.music.load(music_file)
            pm.music.play(loops=0, start=pos)
        except:
            print('Could not play music')
        self.updateMusicRow()
        self.changeMusicTitle()
        self.setPlayingImage()
        self.updateFinalMusicTime()

    def nextMusic(self):
        pm.music.stop()
        self.previous_playing_pos = self.current_playing_pos
        if self.current_playing_pos >= len(self.all_music)-1:
            self.current_playing_pos = 0
        else:
            self.current_playing_pos+=1
        self.playMusic()

    def previousMusic(self):
        current_pos = int(pm.music.get_pos()/1000)
        if current_pos < 10:
            if self.current_playing_pos > 0:
                self.previous_playing_pos = self.current_playing_pos
                self.current_playing_pos = self.current_playing_pos-1
                self.playMusic()
        else:
            self.playMusic()
            
    def musicButtonClicked(self, btn):
        if btn.objectName() == "play_btn":
            self.play_btn.hide()
            self.pause_btn.show()
            if self.is_music_playing:
                pm.music.unpause()
            else:
                self.playMusic()
        elif btn.objectName() == "pause_btn":
            self.play_btn.show()
            self.pause_btn.hide()
            pm.music.pause()
            self.is_music_playing = True
        elif btn.objectName() == "next_btn":
            self.nextMusic()
        elif btn.objectName() == "prev_btn":
            self.previousMusic()


    def createNavigation(self, layout):
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        rep_btn = self.createNavBtn(30, 30, 'repeat.png', 'repeat_btn')
        prv_btn = self.createNavBtn(50, 50, 'prev.png', 'prev_btn')
        self.play_btn = self.createNavBtn(80, 80, 'play.png', 'play_btn')
        self.pause_btn = self.createNavBtn(80, 80, 'pause.png', 'pause_btn')
        next_btn = self.createNavBtn(50, 50, 'next.png', 'next_btn')
        shuf_btn = self.createNavBtn(30, 30, 'shuffle.png', 'shuf_btn')

        btn_layout.addWidget(QLabel(), 1)
        btn_layout.addWidget(rep_btn, 1)
        btn_layout.addWidget(prv_btn, 1)
        btn_layout.addWidget(self.play_btn, 1)
        btn_layout.addWidget(self.pause_btn, 1)
        btn_layout.addWidget(next_btn, 1)
        btn_layout.addWidget(shuf_btn, 1)
        self.vol_slider = QSlider(Qt.Horizontal, objectName="volslider")
        self.vol_slider.setValue(10)
        self.vol_slider.valueChanged.connect(self.volumeChange)
        self.vol_slider.setMaximum(100)
        btn_layout.addWidget(self.vol_slider, 1)
        self.pause_btn.hide()
        layout.addLayout(btn_layout)


    def volumeChange(self, value):
        pm.music.set_volume(float(value/100))
        vol = pm.music.get_volume()

    def createNowPlaying(self):
        self.content_layout = self.now_playing_layout
        self.createThumbnail(self.content_layout)
        self.createSlider(self.content_layout)
        self.createNavigation(self.content_layout)

        self.generalLayout.addLayout(self.content_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


