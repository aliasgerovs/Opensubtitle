# -*- coding: utf-8 -*-
"""Movie_Scrapper.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XtJHH_Tvtg4uKZV16st8L7jGzeXj1ffB
"""

cd /content/Movie-Subtitles-Crawler-from-OpenSubtitles.org

import base64
import gzip
import json
import platform

from opencc.opencc import OpenCC
from xmlrpc.client import ServerProxy

class Crawler(object):
    def __init__(self, url, account_info_path):
        self.proxy = ServerProxy(url)
        with open(account_info_path, 'r') as f:
            content = []
            for line in f.readlines():
                content.append(line.strip())
            self.username = content[0]
            self.password = content[1]

    def server_info(self):
        s = self.proxy.ServerInfo()
        info = json.dumps(s, indent=4)
        return info

    def login(self):
        content = self.proxy.LogIn(self.username, self.password, "en", "TemporaryUserAgent")
        #content = json.loads(s)
        if content['status'] == "200 OK":
            self.token = content['token']
            print("Log in successfully, and the token:", self.token)
        else:
            print("Log in failed.")

    def search_subtitles(self, movie_name):
        q = []
        target = {}
        target['query'] = movie_name
        target['sublanguageid'] = "eng"
        q.append(target)

        content = self.proxy.SearchSubtitles(self.token, q)

        # For now, I just choose the first returned result
        
        data = content['data'][0]
        IDSubtitleFile = data['IDSubtitleFile']
        encoding = data['SubEncoding']

        #content = json.dumps(content, indent=4)
        #print(content)
        return IDSubtitleFile, encoding

    def download_subtitles(self, movie_name, subtitleID, encoding):
        q = []
        q.append(subtitleID)

        content = self.proxy.DownloadSubtitles(self.token, q)
        if content['status'] == '200 OK':
            data_array = content['data']
            data = data_array[0]['data']
            with open(movie_name+".gz", 'wb') as f:
                f.write(base64.b64decode(data))

            with gzip.open(movie_name+".gz", 'rb') as f:
                s = f.read()

            with open(movie_name + '.txt', 'w') as f:
                f.write(s.decode(encoding))

class Parser(object):
    def __init__(self):
        print ("platform: ", platform.system())
        if platform.system() == "Windows":
            self.seperator = "\r\n"
        else:
            self.seperator = "\n"

    def parse_subtitles(self, text):
        arr = text.split(self.seperator*2)
        results = []
        for i in range(len(arr)):
            results.extend(arr[i].split(self.seperator)[2:])

        return results

class Converter(object):
    def __init__(self):
        self.s2t_converter = OpenCC('s2t')
        self.t2s_converter = OpenCC('t2s')

    def convert_s2t(self, str_list):
        return [self.s2t_converter.convert(s) for s in str_list]

    def convert_t2s(self, str_list):
        return [self.t2s_converter.convert(s) for s in str_list]

def main(sear_term):
    url = "http://api.opensubtitles.org/xml-rpc"
    movie_name = sear_term
    account_path = "./account.info"
    
    crawler = Crawler(url, account_path)
    crawler.login()
    subtitleID, encoding = crawler.search_subtitles(movie_name)
    crawler.download_subtitles(movie_name, subtitleID, encoding)

    parser = Parser()
    with open(movie_name + '.txt', 'r') as f:
        results = f.read()
        results = parser.parse_subtitles(results)
        print (results)

file = open( "/content/Names_Movie.txt", "r")
base = file.readlines()

for i in base:
  sear_term = i
  sear_term = sear_term.replace(" ","-") 
  try :
    main(sear_term)
  except Exception:
    pass

import glob, os, sys

os.chdir(os.getcwd())

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


out = open("input.txt",'w')

def cleanstr(inputstr):
    bad = ['<i>','</i>']
    for item in bad:
        if item in inputstr:
            inputstr = inputstr.replace(item,'')
    # inputstr = inputstr.upper()
    return inputstr

for filename in glob.glob("*.txt"):
    f = open(filename,'rt')
    for line in f:
        proc = line.strip()
        if not (RepresentsInt(proc) or "->" in proc):
            proc = cleanstr(proc)
            out.write("{}\n".format(proc))

