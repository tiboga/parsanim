import sys
from pprint import pprint

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}


def get_video(url, name):
    print("Downloading %s" % name)
    res = requests.get(url, headers=HEADERS, stream=True)
    total_length = res.headers.get('content-length')
    with open(f'{name}.mp4', 'wb') as file:
        dl = 0
        for elem in res.iter_content(chunk_size=2048 * 2048):
            if elem:
                file.write(elem)
                dl += len(elem)
                file.write(elem)
                done = int(50 * dl / int(total_length))
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                sys.stdout.flush()


def get_url(url_of_episode):
    res = requests.get(url_of_episode, headers=HEADERS)
    main = BeautifulSoup(res.text, 'html.parser')
    div_parent = main.find('div', {'class': 'watch_l'})
    div_of_url = div_parent.findChildren('a', {'class': 'short-btn black video the_hildi'})
    return [str('https://jut.su' + elem['href']) for elem in div_of_url]


def get_url_on_video(urls):
    out = {}
    for elem in urls:
        res = requests.get(elem, headers=HEADERS)
        main = BeautifulSoup(res.text, 'html.parser')
        video = main.find('div', {'class': 'border_around_video is-no-top-left-border no-top-right-border'})
        print(str(len(out) + 1), 'episode')
        if video:
            video = video.find_all('source')
            video_url = [elem['src'] for elem in video]
            name_of_episode = main.find('div', {'class': 'video_plate_title'}).text
            out[name_of_episode] = video_url
    return out


i = input()
sp_of_url = get_url(i)
print('url on episodes got')
url_sp = get_url_on_video(sp_of_url[:-1])
print('url on video got')
for k, v in url_sp.items():
    get_video(v[0], k)
