import requests
import re
import cloudscraper

scraper = cloudscraper.create_scraper()

site = "https://jut.su/cowboy-bebop/"
res = scraper.get(site).text
quality = "480"
pattern = r'<source src="(.*?)" type="video/mp4" lang="ru" label="' + quality

season_start = int(site[site.index("/season-")+8:site.index("/episode-")])
episode_start = int(site[site.index("/episode-")+9:site.index(".html")])

start = res.index('type="video/mp4" lang="ru" label="1080p" res="1080"')
hrefs = res[start-200:start+900]
print(re.search(pattern, hrefs).groups()[0])
video = requests.get(re.search(pattern, hrefs).groups()[0])
print(video.text)