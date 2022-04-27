#!/usr/bin/env python3

import sys
import os
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

target = sys.argv[1]
domain = sys.argv[2]
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')

def parallel():
    os.system('rm -rf ' + dir + '/../../docker/data/' + target + '/temp/parallel_subdomains.log')
    with open(dir + '/../../docker/data/' + target + '/temp/parallel_subdomains.log', 'a') as file:
        file.write('python3 ' + dir + '/../tools/scan_assetfinder.py ' + target + ' ' + domain + '\n')
        file.write('python3 ' + dir + '/../tools/scan_subfinder.py ' + target + ' ' + domain + '\n')
        file.write('python3 ' + dir + '/../tools/scan_sublist3r.py ' + target + ' ' + domain + '\n')
    print(f'\n{Fore.LIGHTYELLOW_EX}[+] STARTING SUBDOMAINS \nThis may take a while...{Style.RESET_ALL}\n')
    try:
        telegramMsg('[+] STARTING SUBDOMAINS ')
    except:
        pass
    os.system('cat ' + dir + '/../../docker/data/' + target + '/temp/parallel_subdomains.log | parallel -u')

def main():
    parallel()

if __name__ == '__main__':
    main()