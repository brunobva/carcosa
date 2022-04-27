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
url_get = 'https://localhost:9200/' + target + '-subdomain/_search'
auth = ('admin', 'Carcosa123')
ip_list = []

def ip():
    data = {"size": 10000}
    get_doc = requests.get(url_get, headers=headers, auth=auth, data=json.dumps(data), verify=False)
    parse_scan = json.loads(get_doc.text)
    for x in parse_scan['hits']['hits']:
        if (str(x['_source']['server.ip']) not in ip_list):
            ip_list.append(str(x['_source']['server.ip']))

def parallel():
    os.system('rm -rf ' + dir + '/../../docker/data/' + target + '/temp/parallel_nmap.log')
    for i in ip_list:
        with open(dir + '/../../docker/data/' + target + '/temp/parallel_nmap.log', 'a') as file:
            file.write('python3 ' + dir + '/../tools/scan_nmap.py ' + target + ' ' + i + '\n')
    print(f'{Fore.LIGHTYELLOW_EX}[+] STARTING NMAP \nThis may take a while...{Style.RESET_ALL}\n')
    try:
        telegramMsg('[+] STARTING NMAP')
    except:
        pass
    os.system('cat ' + dir + '/../../docker/data/' + target + '/temp/parallel_nmap.log | parallel -u')


def main():
    ip()
    parallel()

if __name__ == '__main__':
    main()