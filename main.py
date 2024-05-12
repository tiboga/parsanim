try:
    import os
    import sys
    import time

    import translitname_of_file

    import requests
    from bs4 import BeautifulSoup
    import datetime
    max_len = 0
    url_sp = dict()
    ALL_DOWNLOADED = False
    EP_NEED_DOWNLOAD = None
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
    NAME_OF_CATALOG = '1'
    INDEX = 0
    TOTAL_LENGTH = 0
    len_of_number = 0
    pred_sez = ''
    counter_ep = 0

    class DirAlreadyMake(Exception):
        pass


    def get_length(url):
        global TOTAL_LENGTH
        res = requests.get(url.split('|||')[1], headers=HEADERS, stream=True)
        total_length = res.headers.get('content-length')
        TOTAL_LENGTH += int(total_length)


    def get_video(url, name):
        global pred_sez, counter_ep, Load_from_err_txt
        if not os.path.exists(NAME_OF_CATALOG):
            os.mkdir(NAME_OF_CATALOG)
        name_season, url = url.split('|||')
        if not os.path.exists(NAME_OF_CATALOG + '/' + name_season):
            os.mkdir(NAME_OF_CATALOG + '/' + name_season)
        if name_season == pred_sez:
            counter_ep += 1
        elif Load_from_err_txt:
            counter_ep = counter_ep
            Load_from_err_txt = False
        else:
            counter_ep = 1
        pred_sez = name_season
        print(name)
        print(str(counter_ep).rjust(len_of_number,'0'))
        name = str(counter_ep).rjust(len_of_number,'0') + '_' + name
        print("Downloading %s" % name)
        res = requests.get(url, headers=HEADERS, stream=True)
        total_length = res.headers.get('content-length')
        with open(f'{NAME_OF_CATALOG}/{name_season}/{name}.mp4', 'wb') as file:
            dl = 0
            len_downloaded = 0
            for elem in res.iter_content(chunk_size=1024 * 2):
                if elem:
                    len_downloaded += len(elem)
                    file.write(elem)
                    dl += len(elem)
                    done = int(50 * dl / int(total_length))
                    percents = str(round((dl / int(total_length)) * 100)) + '%'

                    sys.stdout.write("\r%s MB/%s MB %s [%s%s]" % (
                        str(round(len_downloaded / 1048576, 2)), str(round(int(total_length) / 1048576, 2)), percents,
                        '=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
        print()
        print("Downloaded! %s" % name)


    def get_url(url_of_episode):
        global NAME_OF_CATALOG, len_of_number
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
        len_of_number = len(str(current_ep))
        NAME_OF_CATALOG = ''.join(list(filter(lambda x: x.isalpha() or x.isdigit() or x ==' ', list(main.find('div', {'class': 'under_video_additional the_hildi'}).find('b').text))))
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
                    out[name_of_episode] = NAME_OF_CATALOG + k + '|||' + video_url[INDEX]
        return out


    Load_from_err_txt = False
    with open('err.txt', 'r') as file:
        NAME_OF_CATALOG = file.readline().rstrip('\n')
        if NAME_OF_CATALOG != '':
            if input("We found incomplete downloaded files. Download them? Y/N ") == 'Y':
                Load_from_err_txt = True
                OK = False
                url_sp = dict()
                counter_ep = int(file.readline().rstrip('\n'))
                print(counter_ep)
                lines = file.readlines()
                len_of_number = len(str(len(lines[1:])))
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
    for v in url_sp.values():
        get_length(v)
        print(f'\rGetting length: {round(TOTAL_LENGTH / 1048576, 1)} MB', end='')
    print()
    print(len_of_number)
    for k, v in url_sp.items():
        EP_NEED_DOWNLOAD = k
        get_video(v, k)
    ALL_DOWNLOADED = True
finally:
    if not ALL_DOWNLOADED:
        with open('err.txt', 'w') as file:
            write = False
            file.write(NAME_OF_CATALOG + '\n')
            file.write(str(counter_ep) + '\n')
            for elem in url_sp.keys():
                if elem == EP_NEED_DOWNLOAD:
                    write = True
                if write:
                    file.write(elem + '|||' + url_sp[elem] + '\n')
