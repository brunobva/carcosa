#!/usr/bin/env python3

import sys
import os
import requests
import json
import urllib3
from colorama import Fore, Style
import telegram
import configparser

basedir = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(f'{basedir}/../config/config.ini')
telegram_token = config['TELEGRAM']['token']
chat_id = config['TELEGRAM']['chat']

def telegramMsg(msg):
    bot = telegram.Bot(token=telegram_token)
    bot.send_message(text=msg, chat_id=chat_id)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

target = sys.argv[1]
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url_get = 'https://localhost:9200/' + target + '-webenum/_search'
auth = ('admin', 'Carcosa123')
sist = {}

def endpoints():
    data = {"size": 10000}
    get_doc = requests.get(url_get, headers=headers, auth=auth, data=json.dumps(data), verify=False)
    parse_scan = json.loads(get_doc.text)
    for x in parse_scan['hits']['hits']:
        if str(x['_source']['url.original']) not in sist and str(x['_source']['url.original']) != '' and str(x['_source']['url.original']) != None:
            sist[x['_source']['url.original']] = [x['_source']['server.domain'],x['_source']['server.ip']]


def parallel():
    os.system('rm -rf ' + dir + '/../../docker/data/' + target + '/temp/parallel_feroxbuster.log')
    with open(dir + '/../../docker/data/' + target + '/temp/parallel_feroxbuster.log', 'a') as file:
        for s in sist:
            file.write('python3 ' + dir + '/../tools/scan_feroxbuster.py ' + target + ' ' + s + ' ' + sist[s][0] + ' ' + sist[s][1] + '\n')
    print(f'{Fore.LIGHTYELLOW_EX}[+] STARTING FEROXBUSTER \nThis may take a while...{Style.RESET_ALL}\n')
    try:
        telegramMsg('[+] STARTING FEROXBUSTER')
    except:
        pass
    with open(dir + '/../../docker/data/' + target + '/temp/parallel_feroxbuster.log') as file:
        for i in file:
            i = i.rstrip('\n')
            os.system(i)


def main():
    endpoints()
    parallel()

if __name__ == '__main__':
    main()