import os
from bs4 import BeautifulSoup
import requests
import urllib.request
from tqdm import tqdm
import math
import time
import re


WAITING_TIME = 60


def main():
    save_dir = './html2/'
    os.makedirs(save_dir, exist_ok=True)

    # アーティスト検索ページ
    url = 'https://music.j-total.net/a_search/'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    r.encoding = r.apparent_encoding

    # 各五十音のリンクを取得
    moji_links = []
    gojyuon = soup.find_all('select')
    for g in gojyuon:
        moji_lst = g.find_all('option')[1:] # 最初の要素はリンクが含まれていない
        for moji in moji_lst:
            moji_links.append(moji.get('value'))

    # 頭文字ごと処理
    for moji_link in tqdm(moji_links):
        moji_url = url + moji_link

        try:
            r_moji = requests.get(moji_url, timeout=WAITING_TIME)
        except:
            print('{} skipされた'.format(moji_url))
            continue

        soup_moji = BeautifulSoup(r_moji.content, 'html.parser')
        artist_links = soup_moji.find_all('a', href=re.compile("^//music.j-total.net/db/search.cgi"))
        artist_link_dict = {}
        for link in artist_links:
            name = link.text.replace('\n', '').replace(' ', '')
            if len(name) == 0:
                continue
            artist_link_dict[name] = 'http:' + link.get('href')

        # # 歌手ごと処理
        # if '/yu.html' in moji_url:
        #     flg = True
        # else:
        #     flg = False

        # flg = True
        for artist in artist_link_dict:
            song_cnt = 0

            # # 中断してしまったので途中から
            # if artist == 'ゆいこ':
            #     flg = False
            # if flg:
            #     continue

            artist_dir = save_dir + artist
            os.makedirs(artist_dir, exist_ok=True)
            ar_url = artist_link_dict[artist]
            try:
                r_ar = requests.get(ar_url, timeout=WAITING_TIME)
            except:
                print('{} skipされた'.format(artist))
                continue

            soup_ar = BeautifulSoup(r_ar.content, 'html.parser')
            # 歌手の総曲数を求める
            pg = soup_ar.find_all('font', size='3')[-1]
            pg_string = pg.text.split(' ')
            total_num_index = pg_string.index('件中') - 1
            total_num = int(pg_string[total_num_index])

            # 総曲数からページ数を求める
            max_page = math.ceil(total_num / 20)

            # ページごと処理
            for p in range(1, max_page+1):
                page_url = ar_url + '&page={}'.format(p)
                try:
                    r_song_lst = requests.get(page_url, timeout=WAITING_TIME)
                except:
                    print('{} {} skipされた'.format(artist, p))
                    continue
                soup_song_lst = BeautifulSoup(r_song_lst.content, 'html.parser')

                song_links = soup_song_lst.find_all('a', href=re.compile("^//music.j-total.net/db/rank.cgi\?mode"), target='')

                # form = soup_song_lst.find_all('form', action='search.cgi')[-1]
                # song_links = form.find_all('a')
                # song_links = song_links[:len(song_links) - 8]  # 末尾8こはいらない
                # song_link_set = set()  # 重複をなくす
                for s_link in song_links:
                    s_url = 'http:' + s_link.get('href')
                    song_name = s_link.find('b').text
                    try:
                        data = urllib.request.urlopen(s_url, timeout=WAITING_TIME).read()
                        try:
                            with open(artist_dir + '/{}.html'.format(song_name), mode='wb') as ht:
                                ht.write(data)
                        except:
                            with open(artist_dir + '/{}.html'.format(song_cnt), mode='wb') as ht:
                                ht.write(data)
                    except:
                        print('{} {} {} skipされた'.format(artist, p, s_url))

                    #     urllib.request.urlretrieve(s_link, artist_dir + '/{}.html'.format(song_cnt))
                    # except TimeoutError:
                    #     print('{} {} {} skipされた'.format(artist, p, s_link))
                    song_cnt += 1
                    time.sleep(1)

            print('{} ok'.format(artist))

main()
