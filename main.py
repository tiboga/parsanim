import os
import sys
import time

import translitname_of_file

import requests
from bs4 import BeautifulSoup


class DirAlreadyMake(Exception):
    pass


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
NAME_OF_CATALOG = ''
INDEX = 0


def get_video(url, name):
    try:
        os.mkdir(NAME_OF_CATALOG)
    except:
        DirAlreadyMake()
    print("Downloading %s" % name)
    res = requests.get(url, headers=HEADERS, stream=True)
    total_length = res.headers.get('content-length')
    with open(f'{NAME_OF_CATALOG}/{name}.mp4', 'wb') as file:
        dl = 0
        for elem in res.iter_content(chunk_size=1024):
            if elem:
                file.write(elem)
                dl += len(elem)
                file.write(elem)
                done = int(50 * dl / int(total_length))
                percents = str(round((dl / int(total_length)) * 100)) + '%'
                sys.stdout.write("\r%s [%s%s]" % (percents,'=' * done, ' ' * (100 - done)))
                sys.stdout.flush()
    print("Downloaded! %s" % name)


def get_url(url_of_episode):
    global NAME_OF_CATALOG
    res = requests.get(url_of_episode, headers=HEADERS)
    main = BeautifulSoup(res.text, 'html.parser')
    div_parent = main.find('div', {'class': 'watch_l'})
    div_of_url = div_parent.findChildren('a', {'class': 'short-btn black video the_hildi'})
    NAME_OF_CATALOG = main.find('div', {'class': 'under_video_additional the_hildi'}).find('b').text
    return [str('https://jut.su' + elem['href']) for elem in div_of_url]


def get_url_on_video(urls):
    out = {}
    for elem in urls:
        res = requests.get(elem, headers=HEADERS)
        main = BeautifulSoup(res.text, 'html.parser')
        video = main.find('div', {'class': 'border_around_video is-no-top-left-border no-top-right-border'})
        outed = str(str(len(out) + 1) + ' url on video got')
        sys.stdout.write("\r%s" % outed)
        sys.stdout.flush()
        if video:
            video = video.find_all('source')
            video_url = [elem['src'] for elem in video]
            name_of_episode = translitname_of_file.translit(main.find('div', {'class': 'video_plate_title'}).text)
            out[name_of_episode] = video_url[INDEX]
    return out


i = input()

while True:
    quality = input('Quality (1080, 720, 480, 360): ')
    if quality.isdigit():
        if int(quality) in [1080, 720, 480, 360]:
            if int(quality) == 1080:
                INDEX = 0
            elif int(quality) == 720:
                INDEX = 1
            elif int(quality) == 480:
                INDEX = 2
            elif int(quality) == 360:
                INDEX = 3
            break

sp_of_url = get_url(i)
print('url on episodes got')
url_sp = get_url_on_video(sp_of_url)
sys.stdout.write("\r%s" % 'All url on video got\n')
sys.stdout.flush()
for k, v in url_sp.items():
    get_video(v, k)
