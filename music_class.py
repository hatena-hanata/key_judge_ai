import pandas as pd


# 音階のクラス
class Note:
    name_lst = ['C', 'C#/D♭', 'D', 'D#/E♭', 'E', 'F', 'F#/G♭', 'G', 'G#/A♭', 'A', 'A#/B♭', 'B']

    def __init__(self, s):
        if len(s) == 1:
            self.name = s
        else:
            for index, c in enumerate(Note.name_lst):
                if len(c) != 1:
                    c_split = c.split('/')
                    if s in c_split:
                        self.name = c

    def __str__(self):
        return self.name


class Chord:
    # s = 'Dm7' など受け取る
    def __init__(self, s):
        # コードのルート音
        if len(s) == 1:
            self.root = Note(s)
        else:
            if s[1] == '#' or s[1] == '♭':
                self.root = Note(s[0:2])
            else:
                self.root = Note(s[0])

        # コードがメジャーかマイナーか
        if 'm' in s:
            self.is_major = False
        else:
            self.is_major = True

    def __str__(self):
        if self.is_major:
            return '{}_Major'.format(self.root.name)
        else:
            return '{}_minor'.format(self.root.name)


class Song:
    def __init__(self, name, key):
        """
        コンストラクタ
        :param name: str
        :param key: Noteのインスタンス
        """
        # 曲名
        self.name = name
        self.chord_count_dict = {
            'name': name,
            'key' : key,
            'C_Major': 0,
            'C_minor': 0,
            'C#/D♭_Major': 0,
            'C#/D♭_minor': 0,
            'D_Major': 0,
            'D_minor': 0,
            'D#/E♭_Major': 0,
            'D#/E♭_minor': 0,
            'E_Major': 0,
            'E_minor': 0,
            'F_Major': 0,
            'F_minor': 0,
            'F#/G♭_Major': 0,
            'F#/G♭_minor': 0,
            'G_Major': 0,
            'G_minor': 0,
            'G#/A♭_Major': 0,
            'G#/A♭_minor': 0,
            'A_Major': 0,
            'A_minor': 0,
            'A#/B♭_Major': 0,
            'A#/B♭_minor': 0,
            'B_Major': 0,
            'B_minor': 0,
        }
        self.original_key = key

    def append_chord(self, c):
        self.chord_count_dict[str(c)] += 1

    def to_DataFrame(self):
        return pd.DataFrame.from_dict(self.chord_count_dict, orient='index').T
