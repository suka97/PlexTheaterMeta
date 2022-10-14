# yt-dlp -o "nombre (año).mp4" "url"

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# xml
from dict2xml import dict2xml
# command arguments
import sys

def initWebdriver(webdriver_path):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path=webdriver_path)
    return driver


def getTeatrixMeta(driver, url):
    driver.get(url)
    try:
        desc_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "app-play-detail-page-description"))
        )
    finally:
        # desc
        for i in range(2):
            desc_element = desc_element.find_element(By.TAG_NAME, 'div')
        desc = desc_element.find_elements(By.TAG_NAME, 'div')[1].text
        # title
        title_element = driver.find_element(By.TAG_NAME, 'app-play-hero-default')
        title = title_element.find_element(By.TAG_NAME, 'h2').text
        # year
        year_element = driver.find_element(By.XPATH, '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/app-play-hero/app-hero/section/div[2]/div/div/p/span[1]')
        year = year_element.text
        # actors
        actors_elements = driver.find_element(By.XPATH, '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/div/app-play-detail-page-cast/div/div/div[2]/div[2]').find_elements(By.TAG_NAME, 'li')
        actors = []
        for e in actors_elements:
            actors.append(e.text)
        # writer
        writer = driver.find_element(By.XPATH, '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/div/app-play-detail-page-cast/div/div/div[2]/div[1]/div[1]/ul/li').text
        # director
        director = driver.find_element(By.XPATH, '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/div/app-play-detail-page-cast/div/div/div[2]/div[1]/div[2]/ul/li').text

        return {
            'desc': desc,
            'title': title,
            'year': year,
            'actors': actors,
            'writer': writer,
            'director': director
        };


def avalonFormat(info, genre=''):
    salida = []
    salida.append({'title': info['title']})
    salida.append({'originaltitle': ''})
    salida.append({'sorttitle': ''})
    salida.append({'set': ''})
    salida.append({'rating': ''})
    salida.append({'releasedate': info['year']+'-01-01'})
    salida.append({'plot': info['desc']})
    salida.append({'tagline': ''})
    salida.append({'mpaa': ''})
    salida.append({'genre': genre})
    salida.append({'writer': info['writer']})
    salida.append({'studio': ''})
    salida.append({'director': info['director']})
    for a in info['actors']:
        salida.append({'actor':{
            'name': a,
            'role': '',
            'thumb': ''
        }})
    return salida    


def str_removeEmptyLines(string_with_empty_lines):
    lines = string_with_empty_lines.split("\n")
    non_empty_lines = [line for line in lines if line.strip() != ""]
    string_without_empty_lines = ""
    for line in non_empty_lines:
        string_without_empty_lines += line + "\n"
    return string_without_empty_lines


def formatXml(avalon):
    xml_str = dict2xml(avalon, indent="    ")
    xml_str = str_removeEmptyLines(xml_str)
    return "<movie>\n" + xml_str + '</movie>'



import argparse
from datetime import date
import os
parser = argparse.ArgumentParser(description='Crear metadata para plex compatible con avalon')
parser.add_argument('dest', nargs='+', help='path a la obra')
parser.add_argument('--url', dest='url', help='url de teatrix')
parser.add_argument('--year', type=int, dest='year', help='año', default=date.today().year)
parser.add_argument('--genre', dest='genre', help='año', default='')
parser.add_argument('--webdriver', dest='webdriver', help='webdriver path', default='webdriver.exe')
args = parser.parse_args()
dest = args.dest[0]
title = os.path.split(dest)[1]

print(args.genre)
info = {
    'desc': '',
    'title': title,
    'year': str(args.year),
    'actors': [],
    'writer': '',
    'director': '',
}
if ( args.url != None ):
    driver = initWebdriver(args.webdriver)
    info = getTeatrixMeta(driver, args.url)
    driver.quit()

dir_path = dest + ' (' + info['year'] + ')'
if ( not os.path.exists(dir_path) ):
    os.mkdir(dir_path)
avalon = avalonFormat(info, args.genre)
xml_path = dir_path + '/' + dest + ' (' + info['year'] + ').xml'
file = open(xml_path, "w")
file.write( formatXml(avalon) )
file.close()
