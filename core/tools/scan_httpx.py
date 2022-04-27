#!/usr/bin/env python3

import os
import sys
import uuid
import json
import subprocess
import requests
import urllib3
from time import strftime
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
subdomain = sys.argv[2]
ip = sys.argv[3]
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url = 'https://localhost:9200/' + target + '-webenum/_doc?refresh'
auth = ('admin', 'Carcosa123')
time_now = strftime("%Y-%m-%dT%H:%M:%S%Z")
tool = 'httpx'
web = {}
rand = str(uuid.uuid1())
container_name = target + '-' + 'httpx' + rand
output = 'httpx-' + rand + '.txt'
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')

def exec_docker(url):
    command = "bash -c 'echo " + url + " | httpx --silent'"
    resp = subprocess.check_output(
        'docker run --rm --name ' + container_name + ' -v ' + dir + '/../../docker/data/' + target + '/temp:/data kali-carcosa:1.0 ' + command + ' || true',
        shell=True)
    return resp


def parse():
    sist = exec_docker(subdomain).decode('utf-8').rstrip('\n')
    if(sist != '' or sist != None):
        web['network.protocol'] = sist.split(':')[0]
        try:
            web['server.port'] = sist.split(':')[2].split('/')[0]
        except:
            if(web['network.protocol'] == 'http'):
                web['server.port'] = '80'
            else:
                web['server.port'] = '443'

        path = len(sist.split('/'))
        if(path == 3):
            web['url.path'] = '/'
            web['url.original'] = sist
        else:
            i = 3
            web['url.path'] = ''
            try:
                web['url.original'] = web['network.protocol'] + '://' + sist.split('/')[2]
            except:
                web['url.original'] = sist
            while i < path:
                web['url.path'] = web['url.path'] + '/' + sist.split('/')[1]

        data = {
            '@timestamp':time_now,
            'server.address':subdomain,
            'server.domain':subdomain,
            'server.ip':ip,
            'server.port':web['server.port'],
            'network.protocol':web['network.protocol'],
            'url.path':web['url.path'],
            'http.response.status_code':'200',
            'url.original':web['url.original'],
            'url.full': web['url.original'] + web['url.path'],
            'vulnerability.scanner.vendor': tool
        }

        r = requests.post(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
        message = "Server: " + subdomain + " Directory: " + web['url.original'] + web['url.path']
        try:
            telegramMsg(message)
        except:
            pass
        # print(r.text)
        # print(data)


def main():
    parse()


if __name__ == '__main__':
    main()
