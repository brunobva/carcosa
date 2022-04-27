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
url = sys.argv[2]
subdomain = sys.argv[3]
ip = sys.argv[4]
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url_post = 'https://localhost:9200/' + target + '-webenum/_doc?refresh'
auth = ('admin', 'Carcosa123')
time_now = strftime("%Y-%m-%dT%H:%M:%S%Z")
tool = 'feroxbuster'
web = {}
rand = str(uuid.uuid1())
container_name = target + '-' + 'feroxbuster' + rand
output = 'feroxbuster-' + rand + '.json'
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')


def exec_docker():
    command = 'feroxbuster --url ' + url + ' -w /wordlists/big.txt --insecure -r --silent --json -o ' + output
    subprocess.check_output(
        'docker run --rm --name ' + container_name + ' -v ' + dir + '/../../docker/data/' + target + '/temp:/data -v ' + dir + '/../../docker/wordlists:/wordlists kali-carcosa:1.0 ' + command + ' || true',
        shell=True)


def parse():
    with open(dir + '/../../docker/data/' + target + '/temp/' + output) as file:
        for l in file:
            json_line = l.rstrip('\n')
            json_data = json.loads(json_line)
            if str(json_data['type']) == 'response':
                web['network.protocol'] = json_data['url'].split(':')[0]
                try:
                    web['server.port'] = json_data['url'].split(':')[2].split('/')[0]
                except:
                    if web['network.protocol'] == 'http':
                        web['server.port'] = '80'
                    else:
                        web['server.port'] = '443'
                web['url.path'] = json_data['path']
                web['url.original'] = json_data['original_url']
                try:
                    web['http.response.status_code'] = str(json_data['status'])
                except:
                    web['http.response.status_code'] = '404'
                web['url.full'] = json_data['url']

            data = {
                '@timestamp': time_now,
                'server.address': subdomain,
                'server.domain': subdomain,
                'server.ip': ip,
                'server.port': web['server.port'],
                'network.protocol': web['network.protocol'],
                'url.path': web['url.path'],
                'http.response.status_code': web['http.response.status_code'],
                'url.original': web['url.original'],
                'url.full': web['url.full'],
                'vulnerability.scanner.vendor': tool
            }

            r = requests.post(url_post, headers=headers, auth=auth, data=json.dumps(data), verify=False)
            try:
                message = "Server: " + subdomain + " Directory: " + web['url.full'] + " Status: " + web['http.response.status_code']
            except:
                message = "Server: " + subdomain + " Directory: " + web['url.full']
            try:
                telegramMsg(message)
            except:
                pass
            # print(r.text)
            # print(data)


def main():
    exec_docker()
    try:
        parse()
    except:
        pass


if __name__ == '__main__':
    main()
