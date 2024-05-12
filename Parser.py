import os
import sys

import requests
from bs4 import BeautifulSoup
import translitname_of_file

class Parser:
    def __init__(self, url, quality, headers=None):

        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                              ' Chrome/119.0.0.0 Safari/537.36'}
        translate_quality_dict = {1080: 0,
                                  720: 1,
                                  480: 2,
                                  360: 3}
        self.headers = headers
        self.url = url
        self.quality = translate_quality_dict[quality]
        self.TOTAL_LENGTH = 0
        self.len_of_tile = 1
        self.NAME_OF_CATALOG = ''
        self.dict_of_url_on_eps = dict()
        self.path_and_url_dict = dict()

    async def get_url(self):
        res = requests.get(self.url, headers=self.headers)  # getting html of page
        main = BeautifulSoup(res.text, 'html.parser')  # initializing of parser
        div_parent = main.find('div', {'class': 'sector_border center'}).findNext('div').findNext('div').findNext(
            'div')  # div with eps
        dict_of_url = dict()
        current_name_of_season = '1 season'
        current_ep_num = 0
        for elem in div_parent:
            if elem != '\n':
                if str(elem).split('<')[1][0] == 'h':
                    current_name_of_season = translitname_of_file.translit(
                        elem.text)  # translated name of season if h is in div
                elif str(elem).split('<')[1][0] == 'a':
                    if current_name_of_season in dict_of_url.keys():
                        dict_of_url[current_name_of_season].append(
                            'https://jut.su' + elem['href'])  # url from a appended in dict_of_url
                    else:
                        dict_of_url[current_name_of_season] = ['https://jut.su' + elem['href']]
                    current_ep_num += 1
        # saving result
        self.len_of_tile = len(str(current_ep_num))  # variable for good display of number ep
        self.NAME_OF_CATALOG = ''.join(list(filter(lambda x: x.isalpha() or x.isdigit() or x == ' ', list(
            main.find('div', {'class': 'under_video_additional the_hildi'}).find('b').text))))
        self.dict_of_url_on_eps = dict_of_url

    async def get_url_on_video(self):
        for k, elem in self.dict_of_url_on_eps.items():  # k - name of season, elem - sp of url
            for e in elem:  # e - url
                res = requests.get(e, headers=self.headers)
                main = BeautifulSoup(res.text, 'html.parser')
                video = main.find_all('source')
                if video:
                    video_url = [i['src'] for i in video]  # getting all url on video in page
                    name_of_episode = translitname_of_file.translit(
                        main.find('div', {'class': 'video_plate_title'}).text)  # translit of title
                    if k not in self.path_and_url_dict.keys():
                        self.path_and_url_dict[k] = [{'path': self.NAME_OF_CATALOG + '/' + k, 'name_of_ep': name_of_episode,
                                                      'url': video_url[
                                                          self.quality]}]  # url on video in necessary quality
                    else:
                        self.path_and_url_dict[k].append(
                            {'path': self.NAME_OF_CATALOG + k, 'name_of_ep': name_of_episode,
                             'url': video_url[
                                 self.quality]})

                outed = str(str(sum([len(elem) for elem in self.path_and_url_dict.values()])) + ' url on video got')
                sys.stdout.write("\r%s" % outed)
                sys.stdout.flush()
        print()

    async def get_length(self):
        for v in self.path_and_url_dict.values():
            for elem in v:
                res = requests.get(elem['url'], headers=self.headers, stream=True)
                total_length = res.headers.get('content-length')
                self.TOTAL_LENGTH += int(total_length)

    async def get_video(self):
        # global pred_sez, counter_ep, Load_from_err_txt
        counter_ep = 0
        for name_season, sp_of_eps in self.path_and_url_dict.items():
            first_downloaded_video = True
            for dict_of_ep in sp_of_eps:
                if not os.path.exists(self.NAME_OF_CATALOG):
                    os.mkdir(self.NAME_OF_CATALOG)
                if not os.path.exists(self.NAME_OF_CATALOG + "_" + dict_of_ep['path']):
                    os.mkdir(dict_of_ep['path'])
                if first_downloaded_video:
                    counter_ep = 1
                else:
                    counter_ep += 1
                pred_sez = name_season
                name = str(counter_ep).rjust(self.len_of_tile, '0') + '_' + dict_of_ep['name_of_ep']
                print("Downloading %s" % name)
                res = requests.get(dict_of_ep['url'], headers=self.headers, stream=True)
                total_length = res.headers.get('content-length')
                with open(f'{self.NAME_OF_CATALOG}/{name_season}/{name}.mp4', 'wb') as file:
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
                                str(round(len_downloaded / 1048576, 2)), str(round(int(total_length) / 1048576, 2)),
                                percents,
                                '=' * done, ' ' * (50 - done)))
                            sys.stdout.flush()
                print()
                print("Downloaded! %s" % name)
