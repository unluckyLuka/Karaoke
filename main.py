from PyQt5 import QtWidgets, QtCore
from pygame import mixer
from scroll_label import ScrollLabel
from pydub import AudioSegment
import sys
import os
import pars
import argparse
import random


class GUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Караоке')
        self.images = pars.find(['.png', '.jpeg', '.jpg'], directory_image)
        music_file = ''
        self.image = ''
        self.text = ''
        self.text_song = pars.TextParser(music_file)
        self.flag_load = False
        self.cur_time = 0
        self.time = 0
        self.flag_pause = False
        self.all_text = ''
        self.text_write = ''
        self.rev_text = ''
        self.queue_songs = []
        self.label = ScrollLabel(self)
        self.change_backgrounds()

        self.timer_paint = QtCore.QTimer(self)
        self.timer_paint.setInterval(10000)
        self.timer_paint.timeout.connect(self.change_backgrounds)
        if not is_background_const:
            self.timer_paint.start()

        self.timer_text = QtCore.QTimer(self)
        self.timer_text.setInterval(150)
        self.timer_text.timeout.connect(self.get_time_and_text)
        self.timer_text.start()

        self.current_file = QtWidgets.QLabel(self)
        self.current_file.setText('')

        self.text_time = QtWidgets.QLabel(self)
        self.text_time.setText('')

        self.text_time_c = QtWidgets.QLabel(self)
        self.text_time_c.setText('')

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setValue(0)
        self.slider.setTickInterval(10)

        self.btn_play = QtWidgets.QPushButton(self)
        self.btn_play.setText('Play')
        self.btn_play.clicked.connect(self.play)

        self.btn_pause = QtWidgets.QPushButton(self)
        self.btn_pause.setText('Пауза')
        self.btn_pause.clicked.connect(self.pause)

        self.btn_stop = QtWidgets.QPushButton(self)
        self.btn_stop.setText('Stop')
        self.btn_stop.clicked.connect(self.stop)

        self.btn_next_song = QtWidgets.QPushButton(self)
        self.btn_next_song.setText('Next song')
        self.btn_next_song.clicked.connect(self.play_next)

        self.btn_prev_song = QtWidgets.QPushButton(self)
        self.btn_prev_song.setText('Previous song')
        self.btn_prev_song.clicked.connect(self.play_previous)

        self.list_songs = QtWidgets.QListWidget(self)
        self.list_songs.setMinimumSize(200, 200)
        self.label.resize(round(self.size().width()/2),
                          round(self.size().height()/2))

        self.find_music_to_list()
        self.list_songs.currentTextChanged.connect(self.loader)
        self.label.setPixmap(self.image)

        box = QtWidgets.QHBoxLayout()
        box_button = QtWidgets.QHBoxLayout()
        box_left_column = QtWidgets.QVBoxLayout()

        box_button.addWidget(self.btn_play)
        box_button.addWidget(self.btn_stop)
        box_button.addWidget(self.btn_pause)
        box_button.addWidget(self.btn_prev_song)
        box_button.addWidget(self.btn_next_song)
        box_button.addWidget(self.text_time_c)
        box_button.addWidget(self.slider)
        box_button.addWidget(self.text_time)
        box_button.addWidget(self.current_file)

        box_left_column.addWidget(self.label, 20)
        box_left_column.addStretch(3)
        box_left_column.addLayout(box_button, 1)

        box.addLayout(box_left_column, 20)
        box.addStretch(2)
        box.addWidget(self.list_songs)
        self.setLayout(box)

        if music is not None:
            self.music_file = music
            self.list_songs.addItem(os.path.split(music)[1])
            self.list_songs.hide()
            new_music_file = self.convert_kar_to_ogg(music, 'files_ogg')
            self.loader(new_music_file)
        else:
            self.music_file = None
        self.prev_song = None
        self.show()

    def change_backgrounds(self):
        if os.path.isfile(directory_image):
            self.image = directory_image
        elif os.path.isdir(directory_image):
            self.image = os.path.join(directory_image, self.take_picture())
        self.label.setPixmap(self.image)

    def closeEvent(self, e):
        mixer.music.stop()
        if self.music_file is not None and tempo != 1:
            p = self.music_file.split('.')
            prev_file_name = p[0] + 'tempo{}.'.format(tempo) + p[1]
            os.remove(prev_file_name)
        e.accept()

    def loader(self, file):
        self.queue_songs.append(self.list_songs.currentRow())
        self.flag_load = True
        self.flag_pause = False
        self.btn_pause.setText('Пауза')
        self.cur_time = 0
        if self.music_file is not None:
            self.prev_song = os.path.split(self.music_file)[-1]
        self.music_file = os.path.join(directory, file)
        self.text_song = pars.TextParser(self.music_file)
        if tempo != 1:
            if self.prev_song is not None:
                p = self.prev_song.split('.')
                prev_file_name = p[0] + 'tempo{}.'.format(tempo) + p[1]
                os.remove(os.path.join(directory, prev_file_name))
            p = self.music_file.split('.')
            filename = p[0] + 'tempo{}.'.format(tempo) + p[1]
            self.text_song.change_tempo(filename, tempo)
        else:
            filename = self.music_file
        mixer.music.load(filename)
        self.play()

    @staticmethod
    def convert_kar_to_ogg(kar_file_path, output_dir):
        audio = AudioSegment.from_file(kar_file_path)
        ogg_file_path = os.path.join(
            output_dir,
            os.path.splitext(os.path.basename(kar_file_path))[0] + '.ogg'
        )
        audio.export(ogg_file_path, format='ogg')
        return ogg_file_path

    def get_time_and_text(self):
        if self.flag_load:
            self.color()
            self.cur_time = mixer.music.get_pos() / 1000
            if self.cur_time < 0:
                self.text_time_c.setText('00:00')
            else:
                minutes, seconds = divmod(self.cur_time*tempo, 60)
                minutes = round(minutes)
                seconds = round(seconds)
                self.text_time_c.setText(
                    '{:02d}:{:02d}'.format(minutes, seconds))
            self.slider.setValue(round(self.cur_time*2))
            self.label.setText(self.text_write, self.rev_text)

            self.label.change_pos(self.text_write.count('<br>')*22)

    def color(self):
        self.text_write = ''
        for i in self.text:
            if self.cur_time >= int(i[1]):
                self.text_write = self.text_write + i[0].replace('\n', '<br>')
                self.rev_text = self.all_text[len(self.text_write):]

    def take_picture(self):
        return random.choice(self.images)

    def find_music_to_list(self):
        for file in pars.find(['.kar'], directory):
            self.list_songs.addItem(file)

    def play(self):
        if self.flag_load:
            self.text_write = ''
            self.all_text = ''
            self.label.setText('', '')
            self.update_current_music()
            if mixer.music.get_busy:
                self.btn_play.setText('Начать заново')
            else:
                self.btn_play.setText('Play')
            mixer.music.play()

    def update_current_music(self):
        self.text = self.text_song.parse()
        self.time = self.text_song.get_full_time(tempo)
        self.text_time.setText(self.time)
        self.current_file.setText(os.path.split(str(self.music_file))[1])
        self.text_time_c.setText('00:00')
        self.all_text = self.text_song.parse_only_text(self.text)
        self.slider.setRange(0, round(self.text_song.file.length * 2))

    def play_next(self):
        if self.list_songs.currentRow() >= 0:
            new_index = self.list_songs.currentRow() + 1
            if new_index < self.list_songs.count():
                self.list_songs.setCurrentRow(new_index)

    def play_previous(self):
        if self.prev_song is not None:
            self.list_songs.setCurrentRow(self.queue_songs[-2])
        elif self.list_songs.currentRow() > 0:
            new_index = self.list_songs.currentRow() - 1
            self.list_songs.setCurrentRow(new_index)

    def stop(self):
        if self.flag_load:
            mixer.music.stop()
            self.text_write = ''
            self.update()

    def pause(self):
        if self.flag_load and not self.flag_pause:
            mixer.music.pause()
            self.flag_pause = True
            self.btn_pause.setText('Продолжить')
        else:
            if self.flag_pause:
                mixer.music.unpause()
                self.flag_pause = False
                self.btn_pause.setText('Пауза')


def parse_args():
    parser = argparse.ArgumentParser(description='karaoke player')
    parser.add_argument('--path',
                        dest="directory",
                        default=os.path.join(os.getcwd(), 'music_kar'),
                        help='path to directory with files')
    parser.add_argument('--path_back',
                        dest="directory_image",
                        default=os.path.join(os.getcwd(), 'backgrounds'),
                        help='path to background directory')
    parser.add_argument('-c',
                        dest="is_background_const",
                        action="store_true",
                        help='if background is changing')
    parser.add_argument('--file',
                        dest="music",
                        help='file to open')
    parser.add_argument('--tempo',
                        type=float,
                        dest="tempo",
                        default=1,
                        help='playback speed')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    directory = args.directory
    directory_image = args.directory_image
    music = args.music
    is_background_const = args.is_background_const
    tempo = args.tempo
    mixer.init()
    mixer.music.set_volume(0.5)
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())
