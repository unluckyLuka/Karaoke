import mido
import os


class TextParser:
    def __init__(self, file):
        if file:
            self.file = mido.MidiFile(file)
            self.charset = self.file.charset

    def parse(self):
        text_music = ''
        time = 0
        tempo = 500000
        text_music_by_time = []
        for message in self.file.tracks[0]:
            if message.type == 'set_tempo':
                tempo = message.tempo
        for message in self.file.tracks[2]:
            if message.type == "text":
                words = message.text.encode(self.charset).decode('cp1251')
                if '@' in words:
                    continue
                if '\\' in words:
                    words = '<br>' + words.replace('\\', '<br>')
                if '/' in words:
                    words = '<br>' + words.replace('/', '')
                time += message.time
                time_in_seconds = mido.tick2second(time,
                                                   self.file.ticks_per_beat,
                                                   tempo)
                text_music_by_time.append((words, time_in_seconds))
                text_music += words
        return text_music_by_time

    def change_tempo(self, filename, tempo):
        new_mid = mido.MidiFile()
        new_mid.ticks_per_beat = self.file.ticks_per_beat
        for track in self.file.tracks:
            new_track = mido.MidiTrack()
            new_mid.tracks.append(new_track)
            for msg in track:
                if msg.type == 'set_tempo':
                    if msg.tempo // tempo > 16777215:
                        msg.tempo = 16777215
                    else:
                        if tempo > 0:
                            msg.tempo = int(msg.tempo / tempo)
                        else:
                            msg.tempo = int(msg.tempo * tempo)
                new_track.append(msg)
        self.file = new_mid
        new_mid.save('{}'.format(filename))

    def get_full_time(self, tempo):
        minutes, seconds = divmod(self.file.length*tempo, 60)
        minutes = round(minutes)
        seconds = round(seconds)
        time_format_all = '{:02d}:{:02d}'.format(minutes, seconds)
        return time_format_all

    @staticmethod
    def parse_only_text(text):
        words = ''
        for word in text:
            words += word[0]
        return words


def find(exc, directory):
    list_files = []
    for files in os.walk(directory):
        for file in files[2]:
            if os.path.splitext(file)[1] in exc:
                list_files.append(file)
    return list_files
