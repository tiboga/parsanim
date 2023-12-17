try:
    import os
    import sys
    import time

    import translitname_of_file

    import requests
    from bs4 import BeautifulSoup

    url_sp = dict()
    ALL_DOWNLOADED = False
    EP_NEED_DOWNLOAD = None
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    NAME_OF_CATALOG = ''
    INDEX = 0


    class DirAlreadyMake(Exception):
        pass


    def get_video(url, name):
        name_season, url = url.split('|||')
        try:
            os.mkdir(NAME_OF_CATALOG)
        except:
            DirAlreadyMake()
        try:
            os.mkdir(f'{NAME_OF_CATALOG}/{name_season}')
        except:
            DirAlreadyMake()
        print("Downloading %s" % name)
        res = requests.get(url, headers=HEADERS, stream=True)
        total_length = res.headers.get('content-length')
        with open(f'{NAME_OF_CATALOG}/{name_season}/{name}.mp4', 'wb') as file:
            dl = 0
            len_downloaded = 0
            for elem in res.iter_content(chunk_size=1024):
                if elem:
                    len_downloaded += 1024
                    file.write(elem)
                    dl += len(elem)
                    file.write(elem)
                    done = int(50 * dl / int(total_length))
                    percents = str(round((dl / int(total_length)) * 100)) + '%'
                    sys.stdout.write("\r%s MB\%s MB %s [%s%s]" % (
                        str(round(len_downloaded / 1048576, 2)), str(round(int(total_length) / 1048576, 2)), percents,
                        '=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        print()
        print("Downloaded! %s" % name)


    def get_url(url_of_episode):
        global NAME_OF_CATALOG
        res = requests.get(url_of_episode, headers=HEADERS)
        main = BeautifulSoup(res.text, 'html.parser')
        div_parent = main.find('div', {'class': 'sector_border center'}).findNext('div').findNext('div').findNext('div')
        div_of_url = dict()
        current_key = '1 sezon'
        current_ep = 0
        for elem in div_parent:
            if elem != '\n':
                if str(elem).split('<')[1][0] == 'h':
                    current_key = translitname_of_file.translit(elem.text)
                elif str(elem).split('<')[1][0] == 'a':
                    if current_key in div_of_url.keys():
                        div_of_url[current_key].append('https://jut.su' + elem['href'])
                    else:
                        div_of_url[current_key] = ['https://jut.su' + elem['href']]
                    current_ep += 1
        print(current_ep)
        NAME_OF_CATALOG = main.find('div', {'class': 'under_video_additional the_hildi'}).find('b').text
        return div_of_url


    def get_url_on_video(urls):
        out = {}
        for k, elem in urls.items():
            for e in elem:
                res = requests.get(e, headers=HEADERS)
                main = BeautifulSoup(res.text, 'html.parser')
                video = main.find_all('source')
                outed = str(str(len(out) + 1) + ' url on video got')
                sys.stdout.write("\r%s" % outed)
                sys.stdout.flush()
                if video:
                    video_url = [i['src'] for i in video]
                    name_of_episode = translitname_of_file.translit(
                        main.find('div', {'class': 'video_plate_title'}).text)
                    out[name_of_episode] = k + '|||' + video_url[INDEX]
        return out


    with open('err.txt', 'r') as file:
        NAME_OF_CATALOG = file.readline().rstrip('\n')
        if NAME_OF_CATALOG != '':
            if input("We found incomplete downloaded files. Download them? Y/N ") == 'Y':
                OK = False
                url_sp = dict()
                lines = file.readlines()
                for elem in lines:
                    k, v = elem.split('|||')[0], elem.split('|||')[1] + '|||' + elem.split('|||')[2]
                    url_sp[k.rstrip('\n')] = v.rstrip('\n')
                for k, v in url_sp.items():
                    EP_NEED_DOWNLOAD = k
                    get_video(v, k)
        OK = True
    if OK:
        with open('err.txt', 'w') as file:
            file.write('')
    i = input('url: ')

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
    print('Url on episodes got')
    url_sp = get_url_on_video(sp_of_url)
    sys.stdout.write("\r%s" % 'All url on video got\n')
    sys.stdout.flush()
    for k, v in url_sp.items():
        EP_NEED_DOWNLOAD = k
        get_video(v, k)
    ALL_DOWNLOADED = True
finally:
    if not ALL_DOWNLOADED:
        with open('err.txt', 'w') as file:
            write = False
            file.write(NAME_OF_CATALOG + '\n')
            for elem in url_sp.keys():
                if elem == EP_NEED_DOWNLOAD:
                    write = True
                if write:
                    file.write(elem + '|||' + url_sp[elem] + '\n')
