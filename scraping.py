from bs4 import BeautifulSoup
import requests


url = 'https://music.j-total.net/data/028fu/044_flumpool/028.html'

# soup取得
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

# 原曲キーの取得
song_info = soup.find_all('font', size='3')[-1]
original_key = song_info.text.split(' ')[1].split('：')[-1]

# コードの取得
main_soup = soup.find('tt')
code_lst = main_soup.find_all('a')

for code_tag in code_lst:
    print(code_tag.text)