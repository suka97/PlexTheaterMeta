# yt-dlp -o "nombre (año).mp4" "url"
# find -name *.png -exec convert '"'{}'"' -resize 600x900! '"'{}'.new.png''"' \;
# find -name *.png | xargs -I {} echo  '"'{}'"' -resize 600x900! '"'{}'.new.png''"'
# convert src -resize 600x900! dest

# xml
from dict2xml import dict2xml
import time, unidecode


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


import argparse
from datetime import date
import os
parser = argparse.ArgumentParser(description='Crear metadata para plex compatible con avalon')
parser.add_argument('dest', nargs='+', help='path a la obra')
parser.add_argument('--year', type=int, dest='year', help='año', default=date.today().year)
parser.add_argument('--genres', dest='genres', help='comma separeted genres')
args = parser.parse_args()
dir_path = args.dest[0] + ' ('+str(args.year)+')'
title = os.path.split(args.dest[0])[1]


info = {
    'desc': '',
    'title': title,
    'year': str(args.year),
    'actors': [],
    'writer': '',
    'director': '',
    'genres': []
}

if args.genres != None: 
    info['genres'] = args.genres.split(',')

basename = info['title'] + ' (' + str(info['year']) + ')'
print(basename)
if ( not os.path.exists(dir_path) ):
    os.mkdir(dir_path)
avalon = avalonFormat(info)
xml_path = dir_path + '/' + basename + '.xml'
file = open(xml_path, "w")
file.write( formatXml(avalon) )
file.close()
