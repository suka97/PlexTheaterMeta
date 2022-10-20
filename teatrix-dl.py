# yt-dlp -o "nombre (año).mp4" "url"
# find -name *.png -exec convert '"'{}'"' -resize 600x900! '"'{}'.new.png''"' \;
# find -name *.png | xargs -I {} echo  '"'{}'"' -resize 600x900! '"'{}'.new.png''"'
# convert src -resize 600x900! dest

TEATRIX_XPATH_YEAR = '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/app-play-hero/app-hero/section/div[2]/div/div/p/span[1]'
TEATRIX_XPATH_ACTORS = '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/div/app-play-detail-page-cast/div/div/div[2]/div[2]'
TEATRIX_XPATH_WRITER = '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/div/app-play-detail-page-cast/div/div/div[2]/div[1]/div[1]/ul/li'
TEATRIX_XPATH_DIRECTOR = '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/div/app-play-detail-page-cast/div/div/div[2]/div[1]/div[2]/ul/li'
TEATRIX_XPATH_GENRES = '/html/body/app-root/app-default-template/div[2]/div[2]/app-play-detail-page/app-request-handler-page/app-play-hero/app-hero/section/div[2]/div/div/app-play-hero-default/div[3]/p[1]/span'
TEATRIX_XPATH_SEARCH_BOX = '/html/body/app-root/app-default-template/div[2]/div[1]/app-navbar/nav/div/ul/li[1]/span/app-play-searchbar/div/div[1]/div/input'
TEATRIX_XPATH_SEARCH_BTN = '/html/body/app-root/app-default-template/div[2]/div[1]/app-navbar/nav/div/ul/li[1]/span/app-play-searchbar/div/button'


# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
# xml
from dict2xml import dict2xml
import time, unidecode, requests


def download_file(url, dest):
    response = requests.get(url)
    file = open(dest, "wb")
    file.write(response.content)
    file.close()


def initWebdriver(webdriver_path, user_data_dir):
    options = Options()
    if user_data_dir != None: options.add_argument("user-data-dir="+user_data_dir) 
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path=webdriver_path, service_log_path='NUL')
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
        year_element = driver.find_element(By.XPATH, TEATRIX_XPATH_YEAR)
        year = year_element.text
        # actors
        actors_elements = driver.find_element(By.XPATH, TEATRIX_XPATH_ACTORS).find_elements(By.TAG_NAME, 'li')
        actors = []
        for e in actors_elements:
            actors.append(e.text)
        # writer
        writer = driver.find_element(By.XPATH, TEATRIX_XPATH_WRITER).text
        # director
        director = driver.find_element(By.XPATH, TEATRIX_XPATH_DIRECTOR).text
        # genre
        genres_str = driver.find_element(By.XPATH, TEATRIX_XPATH_GENRES).text
        genres = genres_str.split(',')
        for i in range(len(genres)): genres[i] = genres[i].lstrip()
        genres.remove('')

        return {
            'desc': desc,
            'title': unidecode.unidecode(title),
            'original_title': title,
            'year': year,
            'actors': actors,
            'writer': writer,
            'director': director,
            'genres': genres
        };


def avalonFormat(info):
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
    for genre in info['genres']: salida.append({'genre': genre})
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


def getNetworkRequests(driver):
    JS_get_network_requests = "var performance = window.performance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; return network;"
    network_requests = driver.execute_script(JS_get_network_requests)
    return network_requests


def getTeatrixVideo(driver, url, load=True):
    if load: driver.get(url)
    try:
        play_btn = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "app-button-play"))
        )
    finally:
        play_btn = play_btn.find_element(By.TAG_NAME, "button")
        ActionChains(driver).move_to_element(play_btn).click(play_btn).perform()
        time.sleep(10)
    network_requests = getNetworkRequests(driver)
    salida = {}
    for n in network_requests:
        if salida.__contains__('video') and salida.__contains__('sub'): break
        if n["name"].lower().endswith('.m3u8'): salida['video'] = n['name']
        if n["name"].lower().endswith('.vtt'): salida['sub'] = n['name']
    return salida


def getTeatrixPosterURL(driver, url, load=True):
    if load: driver.get(url)
    try:
        title_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, 'app-play-hero-default'))
        )
    finally:
        title = title_element.find_element(By.TAG_NAME, 'h2').text
        searchbtn_el = driver.find_element(By.XPATH, TEATRIX_XPATH_SEARCH_BTN)
        ActionChains(driver).move_to_element(searchbtn_el).click(searchbtn_el).perform()
        searchbox_el = driver.find_element(By.XPATH, TEATRIX_XPATH_SEARCH_BOX)
        searchbox_el.send_keys(title)
    try:
        poster_el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "app-play-box-cover"))
        )
    finally:
        cover_url = poster_el.find_element(By.TAG_NAME, 'img').get_attribute('src')
    return cover_url


import subprocess
def _execute_(cmd):
    print(cmd)
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)
def execute(cmd):
    for path in _execute_(cmd): print(path, end="")


import argparse
from datetime import date
import os
parser = argparse.ArgumentParser(description='Crear metadata para plex compatible con avalon')
parser.add_argument('--url_file', dest='url_file', help='file with multiple urls')
parser.add_argument('--url', dest='url', help='url de teatrix')
parser.add_argument('--user_data_dir', dest='user_data_dir', help='chrome user_data_dir', required=True)
parser.add_argument('--yt_dlp', dest='yt_dlp', help='yt-dlp executable path', default='yt-dlp.exe')
parser.add_argument('--webdriver', dest='webdriver', help='webdriver path', default='webdriver.exe')
parser.add_argument('--dest_dir', dest='dest_dir', help='destination directory', default='.')
parser.add_argument('--skip_video', dest='skip_video', help='Skip video files', action='store_true')
args = parser.parse_args()

# magick
try:
    execute('magick')
except Exception as e:
    print('magick needed'); exit()
# ffmpeg
try:
    execute('ffmpeg')
except Exception as e:
    print('ffmpeg needed'); exit()
# url / url_file
if (args.url == None) and (args.url_file == None): 
    print('URL or URL_File needed'); exit()


if args.url_file == None: 
    urls = [args.url]
else:
    with open(args.url_file, 'r') as fp: urls = fp.readlines()

for url in urls:
    driver = initWebdriver(args.webdriver, args.user_data_dir)
    info = getTeatrixMeta(driver, url)
    poster = getTeatrixPosterURL(driver, url, False)
    if not args.skip_video:
        video_files = getTeatrixVideo(driver, url, False)
        print(video_files)
    driver.quit()

    basename = info['title'] + ' (' + str(info['year']) + ')'
    dir_path = args.dest_dir + '/' + basename
    if ( not os.path.exists(dir_path) ):
        os.mkdir(dir_path)
    avalon = avalonFormat(info)
    xml_path = dir_path + '/' + basename + '.xml'
    file = open(xml_path, "w")
    file.write( formatXml(avalon) )
    file.close()

    download_file(poster, dir_path+'/'+'poster.original.png')
    execute('magick ' + '"'+dir_path+'/'+'poster.original.png'+'"' + ' -resize 600x900! ' + '"'+dir_path+'/'+'poster.png'+'"')

    if not args.skip_video:
        if video_files.__contains__('sub'): 
            vtt_path = dir_path + '/' + basename + 'es.vtt'
            download_file(video_files['sub'], vtt_path)
            execute('python3 vtt2srt.py "' + vtt_path + '"')
        video_path = dir_path + '/' + basename + '.mp4'
        execute(args.yt_dlp + ' -o "' + video_path + '" "' + video_files['video'] + '"')
