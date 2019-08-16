import glob
import os
from bs4 import BeautifulSoup
import re
import pandas as pd
import codecs
from tqdm import tqdm

# 自作クラスのインポート
from music_class import Note, Chord, Song


CHORD_PATTERN = r'[A-G]{1}[#,♭]?[m]?'


def getKeyInfo(soup):
    info = soup.find_all('font', size='3')
    song_info = None
    # key情報が曲ごとにまちまちなので、調べる
    for i in info:
        if 'Original' in i.text:
            song_info = i.text
    # key情報がなかったらスキップ
    if song_info is None:
        return None, None, True

    # transpose幅を求める
    if '半音' in song_info:
        transpose_step = -1
    else:
        try:
            transpose_step = int(re.sub(r'\D', '', song_info))
        except:
            return None, None, True
    # original keyを文字列で取得
    try:
        original_key_str = re.search(CHORD_PATTERN, song_info).group()
    except:
        return None, None, True

    return original_key_str, transpose_step, False


def main():
    # 全htmlファイルを取得
    html_files = [p for p in glob.glob('html/**', recursive=True) if os.path.isfile(p)]

    # 出力用df
    ans_df = pd.DataFrame()

    # ファイルごと処理
    for html in tqdm(html_files):

        # ファイル開く
        with codecs.open(html, 'r', 'shift-jis', 'ignore') as f:
            soup = BeautifulSoup(f, 'lxml')
            song_name = soup.find('title').text.split('/')[0] # 曲名取得

            # keyやcapoいくつか取得する
            original_key_str, transpose_step, continue_flg = getKeyInfo(soup)
            if continue_flg:
                print('{}　はデータに不備があり、教師データとして使用できません'.format(song_name))
                continue

            # 曲インスタンスを作成
            song = Song(song_name, Chord(original_key_str))

            # soupからコードを取得
            chord_block = soup.find('tt')
            chord_lst = chord_block.find_all('a')

            for c in chord_lst:
                # 文字列のコードからコードインスタンスを作成
                try:
                    chord_str = re.search(CHORD_PATTERN, c.text).group()
                except:
                    continue
                chord = Chord(chord_str)

                # 原曲キーへtransposeする
                chord.root = chord.root.transpose(transpose_step)
                song.append_chord(chord)
            # 出力
            song_df = song.to_DataFrame()
            ans_df = ans_df.append(song_df)

    ans_df.to_csv('train.csv', encoding='shift-jis', index=False)


main()