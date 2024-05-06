


from asyncio.windows_events import NULL
from pickle import TRUE
import sys
from turtle import back
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import datetime
from functools import partial
import os
import threading
from matplotlib import container
from numpy import tile
import pygame.mixer as pm
import math
import pygame
import sys
from PyQt5.QtSql import QSqlDatabase, QSqlQuery



class Helper():
    def __init__(self, parent):
        self.parent = parent

    def fetchSongPixmap(self, index, music_list):
        try:
            music_file = music_list[index]
            pixmap = self.extractThumbnail(music_file)
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

    def clearLayout(self, layout):
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if isinstance(item, QWidgetItem):
                item.widget().close()
                # or
                # item.widget().setParent(None)
            elif isinstance(item, QSpacerItem):
                pass
            else:
                self.clearLayout(item.layout())

            # remove the item from layout
            layout.removeItem(item) 

    def createScrollBar(self, music_list, all_music_row, method):
        self.scroll_music_list = music_list
        scroll = QScrollArea(objectName="scroll_area")   
        scroll.setStyleSheet("""QWidget{ background-color: transparent }
         QScrollBar{ background-color: none;  }""")
        widget = QWidget()                
        music_rows = QVBoxLayout()
        music_rows.setAlignment(Qt.AlignTop)
        self.addMusicToList(music_rows, all_music_row, music_list, method)
        widget.setLayout(music_rows)
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        return scroll

    def addMusicToList(self, music_rows, all_music_row, music_list, method):
        i = 0
        for music in music_list:
            raw_music = music
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
            music_btn.clicked.connect(partial(method, i))
            if self.parent.current_playing_pos == i:
                self.setPlayingRow(widg, music_btn, i, True, music_list)
            else:
                self.setPlayingRow(widg, music_btn, i, False, music_list)
            music_btn.setIconSize(QSize(30, 30))
            all_music_row.append([widg, music_btn])
            lay.addWidget(music_btn, 10)
            object = QPushButton("")
            # object.clicked.connect(partial(optionMethod, i))
            menu = QMenu()
            self.createButtonMenu(menu, i, raw_music)
            object.setMenu(menu)
            object.setStyleSheet("background:transparent; font-size:17px")
            lay.addWidget(object, 1)
            widg.setLayout(lay)
            music_rows.addWidget(widg)
            i+=1

    def createButtonMenu(self, menu, index, music):
        menu.setStatusTip("Options")
        menu.setCursor(Qt.PointingHandCursor)
        menu.setStyleSheet("""
            QMenu { padding:10px;background:white;font-weight:400;font-size:13px}
            QMenu::item { background:white;width:150px;padding:10px;color:black;}
            QMenu::item::hover { background:red;}
            """)
        sub_menu = QMenu("Add to Playlist", menu)
        self.createAction(sub_menu, "new.png","New Playlist", self.newPlaylist, index)

        playlist = self.parent.database.fetchAllPlaylist()
        for data in playlist:
            self.createAction(sub_menu, "musiciconplaying.png", data[0], self.updatePlaylist, [data, music])
        menu.addMenu(sub_menu)
        self.createAction(menu, "delete.png","Delete song")

    def updatePlaylist(self, data):
        playlst = data[0][1]
        music = data[1]
        list_count = playlst.count(music)
        if list_count<1:
            playlst.append(music)
            title = data[0][0]
            songs = "\n".join(playlst)
            res = self.parent.database.updatePlaylist(title, songs)
        else:
            self.showWarning("Song already in playlist")

    def newPlaylist(self, value):
        self.dialog = QDialog(self.parent)
        self.dialog.setWindowTitle("Create New Playlist")
        self.dialog.setWindowModality(Qt.ApplicationModal)
        container = QWidget(self.dialog)
        container.setFixedSize(250, 180)
        container.setStyleSheet("""
            background:black;color:white;
        """)
        content = QVBoxLayout()
        content.setAlignment(Qt.AlignTop)
        header = QLabel("Enter playlist name")
        header.setStyleSheet("font-size:14px;margin:10px 0px")
        content.addWidget(header)

        self.title = QLineEdit()
        self.title.setStyleSheet("""
            QLineEdit{ padding:10px;border-radius:5px; margin:15px 0px; font-weight:bold; font-size:15px;border:1px solid white}
            QLineEdit::focus{ background:white;color:black}
            """)
        content.addWidget(self.title)
        row = QHBoxLayout()

        add_btn = QPushButton("Add")
        add_btn.setStyleSheet("background:green; padding:7px 10px;border-radius:5px; font-size:13px;")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(partial(self.addPlayList, value))
        row.addWidget(add_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.dialog.close)
        cancel_btn.setStyleSheet("background:red; padding:7px 10px;border-radius:5px; font-size:13px")
        row.addWidget(cancel_btn)

        content.addLayout(row)
        container.setLayout(content)
        self.dialog.exec_()

    def savePlaylist(self, title, song):
        res = self.parent.database.createPlaylist(title, song)
        # print(res)

    def showWarning(self, error):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(error)
        msgBox.setWindowTitle("Warning")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec()


    def addPlayList(self, index):
        title = self.title.text()
        if len(title) > 2:
            song = self.scroll_music_list[index]
            self.savePlaylist(title, song)
            self.dialog.close()
        else:
            self.showWarning("Text length is too short")

    def createAction(self, menu, image, title, trigger=NULL, val=0):
        icon = QIcon("image/{}".format(image))
        item = QAction(icon, str(title), menu)
        if trigger != NULL:
            item.triggered.connect(partial(trigger, val))
        menu.addAction(item)
        menu.addSeparator()
 

    def setPlayingRow(self, widg, music_btn, index, isplaying, music_list):
        if isplaying:
            music_btn.setIcon(QIcon('image/{}'.format("musiciconplaying.png")))
            widg.setStyleSheet("""
                QWidget:hover{background-color:#ff4444}
                QWidget{border-bottom: 1px solid gray; padding:0;margin:0;background-color:red;color:black}
            """)
        else:
            music_btn.setIcon(QIcon(self.fetchSongPixmap(index, music_list)))
            # music_btn.setIcon(QIcon('image/{}'.format("musicicon.png")))
            widg.setStyleSheet("""
                QWidget:hover{background-color:#ff4444}
                QWidget{border-bottom: 1px solid gray; padding:0;margin:0;background-color:none;color:white}
            """)
  

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
        createTableQuery.exec("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                songs TEXT NOT NULL
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

    def fetchPlaylistSongs(self, title):
        query = QSqlQuery()
        query.exec(
            f"""SELECT * FROM playlists WHERE title='{title}'"""
        )
        query.last()
        query = query.value(2).split("\n")
        return query

    def fetchAllPlaylist(self):
        query = QSqlQuery()
        query.exec(
            f"""SELECT * FROM playlists"""
        )
        playlist = []
        while query.next():
            title = query.value(1)
            song = query.value(2).split("\n")
            playlist.append([title, song])
        return playlist

    def updatePlaylist(self, title, songs):
        query = QSqlQuery()
        res = query.exec(
            f"""UPDATE playlists SET songs='{songs}' WHERE title='{title}'"""
        )
        return res


    def createPlaylist(self, title, song):
        query = QSqlQuery()
        res = query.exec(
            f"""INSERT INTO playlists (title, songs)
              VALUES ('{title}', '{song}')"""
        )
        return res


class NowPlayingView():
    def __init__(self, parent, layout):
        self.parent = parent
        self.is_sliding = False
        self.createThumbnail(layout)
        self.createSLider(layout)
        self.createMusicButton(layout)

    def createThumbnail(self, layout):
        frm = QGridLayout()
        frm.addWidget(QLabel(), 0, 0)
        self.image = QLabel()
        self.image.setFixedSize(400, 400)
        # self.image.setPixmap(self.fetchPixmap())
        self.fetchImagePixmap()
        self.image.setStyleSheet('padding-top:10px')
        self.image.move(180,0)
        frm.addWidget(self.image,0,1)
        frm.addWidget(QLabel(),0,2)
        layout.addLayout(frm)

    def fetchImagePixmap(self):
        try:
            music_file = self.parent.all_music[self.parent.current_playing_pos]
            pixmap = self.extractThumbnail(music_file)
            pixmap = pixmap.scaledToHeight(400)
            pixmap = pixmap.scaledToHeight(400)
        except:
            pixmap = QPixmap("image/now.jpg")
            pixmap = pixmap.scaledToHeight(400)
            pixmap = pixmap.scaledToHeight(400)
        self.image.setPixmap(pixmap)

    def extractThumbnail(self, music_file):
        import mutagen
        pixmap = QPixmap()
        metadata = mutagen.File(music_file)
        for tag in metadata.tags.values():
            if tag.FrameID == 'APIC':
                pixmap.loadFromData(tag.data)
                break
        return pixmap

    def createSLider(self, layout):
        music_list = self.parent.all_music[self.parent.current_playing_pos]
        music_list = music_list.split("\\")
        music_list = music_list[-1]
        music_list = music_list.split(".")
        music_list = ".".join(music_list[:-1])

        self.playing_text = QLabel(str(music_list))
        self.playing_text.setAlignment(Qt.AlignCenter)
        self.playing_text.setObjectName("playing_text")
        layout.addWidget(self.playing_text)
        sound = pm.Sound(self.parent.all_music[self.parent.current_playing_pos])
        length = sound.get_length()
        frm = QHBoxLayout()
        self.initial_time = QLabel("0:00")
        frm.addWidget(self.initial_time)
        self.slider = QSlider(Qt.Horizontal, objectName="slider")
        self.slider.setValue(0)
        self.slider.setMinimum(0)
        self.slider.setFocusPolicy(Qt.NoFocus)
        self.slider.setMaximum(int(length))
        # self.slider.valueChanged.connect(self.changeMusicPosition)
        self.slider.sliderMoved.connect(self.sliderMoved)
        self.slider.sliderReleased.connect(self.sliderReleased)
        frm.addWidget(self.slider)
        self.final_time = QLabel("3:20")
        self.final_time.setText(self.sec2time(length))
        frm.addWidget(self.final_time)
        layout.addLayout(frm)

    def sliderMoved(self):
        self.is_sliding = True
        self.initial_time.setText(str(self.sec2time(self.slider.value())))

    def sliderReleased(self):
        value = self.slider.value()
        self.parent.forward_position = -max(0, pm.music.get_pos()/1000)
        self.parent.forward_position += value
        try:
            pm.music.set_pos(value)
        except:
            pass
        self.is_sliding = False

    def sec2time(self, length):
        min = math.floor(length/60)
        sec = math.ceil(length - (min*60))
        return "{}:{}".format(min,sec if sec > 9 else "0" + str(sec))

    def createMusicButton(self, layout):
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
        self.vol_slider.setFocusPolicy(Qt.NoFocus)
        btn_layout.addWidget(self.vol_slider, 1)
        self.pause_btn.hide()
        layout.addLayout(btn_layout)

    def createNavBtn(self, x, y, image, objectname):
        rep_btn = QPushButton(objectName=objectname)
        rep_btn.setIcon(QIcon('image/{image}'.format(image=image)))
        rep_btn.setIconSize(QSize(x,y))
        rep_btn.setFocusPolicy(Qt.NoFocus)
        rep_btn.setCursor(QCursor(Qt.PointingHandCursor))
        rep_btn.clicked.connect(partial(self.musicButtonClicked, rep_btn))
        return rep_btn

    def volumeChange(self, value):
        vol = value/100
        pm.music.set_volume(vol)

    def showPlayButton(self):
        self.play_btn.show()
        self.pause_btn.hide()

    def showPauseButton(self):
        self.play_btn.hide()
        self.pause_btn.show()

    def musicButtonClicked(self, btn):
        if btn.objectName() == "play_btn":
            self.parent.playMusic()
        elif btn.objectName() == "pause_btn":
            self.parent.pauseMusic()
        elif btn.objectName() == "next_btn":
            self.parent.nextMusic()
        elif btn.objectName() == "prev_btn":
            self.parent.previousMusic()

    def update(self):
        if not self.is_sliding:
            current_pos = max(0, max(0, pm.music.get_pos()/1000) + self.parent.forward_position)
            self.slider.setValue(int(current_pos))
            self.initial_time.setText(str(self.sec2time(current_pos)))

    def updateOnce(self):
        self.changeMusicTitle()
        self.updateFinalMusicTime()
        self.fetchImagePixmap()

    def updateVol(self):
        self.vol_slider.setValue(int(pm.music.get_volume()*100))

    def changeMusicTitle(self):
        music_list = self.parent.all_music[self.parent.current_playing_pos]
        music_list = music_list.split("\\")
        music_list = music_list[-1]
        music_list = music_list.split(".")
        music_list = ".".join(music_list[:-1])
        self.playing_text.setText(str(music_list))

    def updateFinalMusicTime(self):
        sound = pm.Sound(self.parent.all_music[self.parent.current_playing_pos])
        length = sound.get_length()
        self.slider.setMaximum(int(length))
        self.final_time.setText(self.sec2time(length))

    
class MusicListView():
    def __init__(self, parent, layout):
        self.parent = parent
        self.all_music_row = []
        self.createMusicList(layout)

    def createMusicList(self, layout):
        scroll = Helper(self.parent).createScrollBar(self.parent.all_music, 
        self.all_music_row, self.clickedMusic)
        layout.addWidget(scroll)


    def clickedMusic(self, index):
        self.parent.all_music = self.parent.all_music_database
        self.parent.self_end_music = True
        self.parent.previous_playing_pos = self.parent.current_playing_pos
        self.parent.current_playing_pos = index
        self.parent.playMusicNow()

    def update(self):
        widg = self.all_music_row[self.parent.current_playing_pos][0]
        btn = self.all_music_row[self.parent.current_playing_pos][1]
        Helper(self.parent).setPlayingRow(widg, btn, self.parent.current_playing_pos, True, self.parent.all_music)
        widg = self.all_music_row[self.parent.previous_playing_pos][0]
        btn = self.all_music_row[self.parent.previous_playing_pos][1]
        Helper(self.parent).setPlayingRow(widg, btn, self.parent.previous_playing_pos, False, self.parent.all_music)


class PlaylistView():
    def __init__(self, parent, layout):
        self.parent = parent
        self.playlist_container = layout
        layout.setContentsMargins(0,10,0,0)
        self.playlist_music = []
        for i in range(5):
            self.playlist_music.append(self.parent.all_music[i])
        self.createPlayListView(layout)
        self.createSongView(layout)

    def createSongView(self, layout):
        self.song_layout = QWidget()
        song_lay = QVBoxLayout()
        # song_lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        song_lay.setAlignment(Qt.AlignTop)
        self.createPlaylistSongs(song_lay)
        self.song_layout.setLayout(song_lay)
        layout.addWidget(self.song_layout)
        self.song_layout.hide()

    def createPlayListView(self, layout):
        self.playlist_layout = QWidget()
        list_layout = QVBoxLayout()
        self.createHead(list_layout)
        self.createList(list_layout)
        self.playlist_layout.setLayout(list_layout)
        layout.addWidget(self.playlist_layout)

    def createPlaylistSongs(self, layout):
        lay = QHBoxLayout()
        # lay.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        lay.setAlignment(Qt.AlignTop)
        col = QHBoxLayout()
        col.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        back_btn = QPushButton("Back")
        back_btn.setIcon(QIcon("image/back.png"))
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""font-size:15px""")
        back_btn.clicked.connect(self.showPlayList)
        col.addWidget(back_btn)

        self.playlist_title = QLabel("Playlist title")
        self.playlist_title.setStyleSheet("""font-size:20px; font-weight:bold; margin-left:40px""")
        col.addWidget(self.playlist_title)
        lay.addLayout(col)

        add_btn = QPushButton("+ Add song")
        add_btn.setStyleSheet("""
            QPushButton{ background:green;font-size:15px;padding:10px 15px;border-radius:5px}
            QPushButton:hover{ background:#040;}
        """)
        delete_btn = QPushButton("Delete Playlist")
        delete_btn.setStyleSheet("""
            QPushButton{ background:red;margin-left:10px;font-size:15px;padding:10px 15px;border-radius:5px}
            QPushButton:hover{ background:#400;}
        """)
        delete_btn.setCursor(Qt.PointingHandCursor)
        btn_lay = QHBoxLayout()
        btn_lay.setAlignment(Qt.AlignRight | Qt.AlignTop)
        add_btn.clicked.connect(partial(self.addSong, layout))
        add_btn.setCursor(Qt.PointingHandCursor)
        btn_lay.addWidget(add_btn)
        btn_lay.addWidget(delete_btn)
        lay.addLayout(btn_lay)
        layout.addLayout(lay)
        self.createMusicList(layout)
    
    def createMusicList(self, layout):
        self.all_music_row = []
        self.music_scroll = Helper(self.parent).createScrollBar(self.playlist_music, 
        self.all_music_row, self.clickedMusic)
        layout.addWidget(self.music_scroll)
        self.first_clicked = True
        
    def addSong(self, layout):
        return
        # playlist = self.parent.database.fetchAllPlaylist()
        # playlist_songs = self.parent.database.fetchPlaylistSongs("Trending")
        # print(playlist_songs)
        if self.first_clicked:
            self.scroll.setParent(None)
            self.first_clicked = False
        else:
            self.createMusicList(layout)
            self.first_clicked = True
        print("add songs")

    def clickedMusic(self, index):
        self.parent.all_music = self.playlist_music
        self.parent.self_end_music = True
        self.parent.previous_playing_pos = self.parent.current_playing_pos
        self.parent.current_playing_pos = index
        self.parent.playMusicNow()

    def showPlayList(self):
        self.playlist_layout.show()
        self.song_layout.hide()
        self.music_scroll.setParent(None)

    def createHead(self, layout):
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        add_btn = QPushButton("+ New Playlist", objectName="newplaylist")
        add_btn.setStyleSheet("""
        QPushButton{background-color:red;padding:10px 15px;font-weight:bold; font-size:15px;border-radius:5px}
        QPushButton:hover{background-color:#aa0000}
        """)
        row.addWidget(add_btn)
        layout.addLayout(row)

    def fetchImagePixmap(self, index, image, size, file):
        try:
            music_file = file[index]
            pixmap = Helper(self.parent).extractThumbnail(music_file)
        except:
            pixmap = QPixmap("image/now.jpg")
        pixmap = pixmap.scaled(size, size, aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation)
        image.setPixmap(pixmap)

    def createImageThumbnail(self, layout, file):
        col = QVBoxLayout()
        col.setContentsMargins(0,0,0,0)
        size = 100
        for i in range(2):
            row = QHBoxLayout()
            row.setContentsMargins(0,0,0,0)
            for j in range(2):
                image = QLabel(f"image {i + j}")
                image.setStyleSheet("padding:0px;margin:0px;border:none")
                image.setFixedSize(size, size)
                image.setContentsMargins(0,0,0,0)
                self.fetchImagePixmap(i+j, image, size, file)
                row.addWidget(image)
            col.addLayout(row)
        layout.addLayout(col, 4)

    def playlistClicked(self, index, event):
        self.playlist_layout.hide()
        self.song_layout.show()
        all_music = self.parent.database.fetchAllPlaylist()
        self.playlist_music = all_music[index][1]
        self.playlist_title.setText(f"{all_music[index][0]}")
        self.music_scroll.setParent(None)
        self.createMusicList(self.playlist_container)

    def createPlaylistItem(self, index, playlist):
        content = QWidget()
        content.setStyleSheet("""
            QWidget{ background:#333;border: 2px solid white; border-radius:2px; margin:10px;}
            QWidget:hover{ background:#900; }
        """)
        lay = QVBoxLayout()
        lay.setAlignment(Qt.AlignTop)
        content.mouseReleaseEvent=partial(self.playlistClicked, index)
        content.setCursor(Qt.PointingHandCursor)
        lay.setContentsMargins(15,15,15,15)
        lay.setAlignment(Qt.AlignTop)
        self.createImageThumbnail(lay, playlist[index][1])
        playlist_name = QLabel(f"{playlist[index][0]}")
        playlist_name.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        playlist_name.setStyleSheet("""
            border:none;font-size:15px;font-weight:500;background:transparent;
        """)
        lay.addWidget(playlist_name)
        content.setLayout(lay)
        return content

    def createPlayList(self, layout):
        playlist = self.parent.database.fetchAllPlaylist()
        total = len(playlist)
        index = 0
        while index < total:
            row = QHBoxLayout()
            row.setAlignment(Qt.AlignLeft)
            row.setContentsMargins(0,0,0,0)
            items = 0
            for i in range(5):
                if index < total:
                    content = self.createPlaylistItem(index, playlist)
                    row.addWidget(content)
                    index+=1
                    items = i
            layout.addLayout(row)

    def createList(self, layout):
        scroll = QScrollArea()
        scroll.setStyleSheet("""QWidget{ background-color: transparent;border:none;outline:none }
         QScrollBar{ background-color: white;  }""")
        widget = QWidget()                
        playlist_rows = QVBoxLayout()
        playlist_rows.setAlignment(Qt.AlignTop|Qt.AlignCenter)
        self.createPlayList(playlist_rows)
        widget.setLayout(playlist_rows)
        # scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setWidgetResizable(False)
        # scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(scroll)
        

class Window(QMainWindow):
    """Main Window."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.database = DataBase()
        self.setDefaults()
        self.fetchMusic()
        self.initUi()
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self.updateUi)
        self._update_timer.start(500)

    def fetchMusic(self):
        self.all_music = self.database.fetchMusic()
        self.all_music.pop()
        self.all_music_database = self.all_music

    def setDefaults(self):
        # pm.pre_init(44100, -16, 2, 2048)
        pygame.init()
        pm.init()
        pm.music.set_volume(0.1)
        self.MUSIC_END = pygame.USEREVENT+1
        pm.music.set_endevent(self.MUSIC_END)
        self.current_playing_pos = 4
        self.previous_playing_pos = 0
        self.was_music_playing = False
        self.is_playing = False
        self.all_music = []
        self.forward_position = 0
        self.self_end_music = False

        
    def initUi(self):
        self.setWindowTitle('Music Player')
        self.setGeometry(350, 50, 800, 300)
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        style = open('style.css').read()
        self._centralWidget.setStyleSheet('background:black;color:white')
        self.setStyleSheet(style)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        self.createViews(self.generalLayout)

    def keyPressEvent(self, e):
        self.setFocusPolicy(Qt.NoFocus)
        if e.key() == Qt.Key_Space:
            self.togglePlayPause()
        elif e.key() == Qt.Key_Up:
            self.increaseVolume()
        elif e.key() == Qt.Key_Down:
            self.reduceVolume()
        elif e.key() == Qt.Key_N:
            self.nextMusic()
        elif e.key() == Qt.Key_P:
            self.previousMusic()
        elif e.key() == Qt.Key_A:
            print("Music End")
        elif e.key() == Qt.Key_Right:
            print("Right key")
        elif e.key() == Qt.Key_Left:
            print("left key")
        elif e.key() == Qt.Key_Escape:
            self.close()

    def musicEnd(self):
        if not self.self_end_music:
            self.forward_position = 0
            self.nextMusic()
        else:
            self.self_end_music = False

    def togglePlayPause(self):
        if self.is_playing:
            self.pauseMusic()
        else:
            self.playMusic()

    def increaseVolume(self):
        vol = pm.music.get_volume()
        if vol < 1:
            vol += 0.02
        pm.music.set_volume(vol)
        self.now_playing_view.updateVol()

    def reduceVolume(self):
        vol = pm.music.get_volume()
        if vol > 0:
            vol -= 0.02
        pm.music.set_volume(vol)
        self.now_playing_view.updateVol()

    def updateUi(self):
        self.time.setText(self.getTime())
        self.now_playing_view.update() 
        for event in pygame.event.get():
            if event.type == self.MUSIC_END:
                self.musicEnd()
    
    def updateOnce(self):
        self.now_playing_view.updateOnce()
        self.music_list_view.update()

    def createViews(self, layout):
        self.showTime(layout)
        self.createTabs(layout)

    def showTime(self, layout):
        self.time = QLabel("{}".format(self.getTime()))
        self.time.setObjectName('time')
        self.time.setAlignment(Qt.AlignRight)
        layout.addWidget(self.time)

    def getTime(self):
        current_time = datetime.datetime.now()
        hr = current_time.hour if current_time.hour < 13 else current_time.hour-12
        time = "{}:{}:{} {}".format(
                (hr) if hr > 9 else "0" + str(hr), 
                current_time.minute if current_time.minute > 9 else "0" + str(current_time.minute), 
                current_time.second if current_time.second > 9 else "0" + str(current_time.second), 
                "PM" if current_time.hour > 11 else "AM") 
        return time

    def createTabs(self, layout):
        tabs = QTabWidget(objectName="nav_tab")
        now_playing_layout = self.createTabPane(tabs, "Now Playing")
        music_list_layout = self.createTabPane(tabs, "All Songs")
        playlist_layout = self.createTabPane(tabs, "Playlist")
        settings_layout = self.createTabPane(tabs, "Settings")
        tabs.tabBar().setCursor(Qt.PointingHandCursor)
        layout.addWidget(tabs)
        self.now_playing_view = NowPlayingView(self, now_playing_layout)
        self.music_list_view = MusicListView(self, music_list_layout)
        self.playlist_view = PlaylistView(self, playlist_layout)

    def createTabPane(self, tabs, title):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        tabs.addTab(tab, title)
        return layout

    def playMusicNow(self, pos=0):
        try:
            pm.music.stop()
            music_file = self.all_music[self.current_playing_pos]
            pm.music.load(music_file)
            pm.music.play(loops=0, start=pos)
            self.was_music_playing = False
            self.forward_position = 0
        except:
            print('Could not play music')
        self.updateOnce()

    def playMusic(self):
        if self.was_music_playing:
            pm.music.unpause()
        else:
            self.playMusicNow()
        self.is_playing = True
        self.now_playing_view.showPauseButton()
            
    def pauseMusic(self):
        if pm.music.get_busy():
            pm.music.pause()
            self.is_playing = False
            self.was_music_playing = True
            self.now_playing_view.showPlayButton()

    def nextMusic(self):
        pm.music.stop()
        self.previous_playing_pos = self.current_playing_pos
        if self.current_playing_pos >= len(self.all_music)-1:
            self.previous_playing_pos = self.current_playing_pos
            self.current_playing_pos = 0
        else:
            self.previous_playing_pos = self.current_playing_pos
            self.current_playing_pos+=1
        self.was_music_playing = False
        self.self_end_music = True
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
        self.self_end_music = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


