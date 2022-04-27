#!/usr/bin/env python3

import os
import sys
import uuid
import json
import subprocess
import urllib3
import requests
from time import strftime, sleep
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
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
auth = ('admin', 'Carcosa123')
time_now = strftime("%Y-%m-%dT%H:%M:%S%Z")
tool = 'nuclei'
web = {}
infra = {}
rand = str(uuid.uuid1())
container_name = target + '-' + 'feroxbuster' + rand
output = 'nuclei-' + rand + '.json'
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')

def exec_docker():
    command = 'nuclei -u ' + url + ' -t /root/nuclei-templates/ -o /data/' + output + ' -json -silent'
    subprocess.check_output(
        'docker run --rm --name ' + container_name + ' -v ' + dir + '/../../docker/data/' + target + '/temp:/data  kali-carcosa:1.0 ' + command + ' || true',
        shell=True)
    sleep(2)


def parse():
    with open(dir + '/../../docker/data/' + target + '/temp/' + output) as file:
        for l in file:
            jsonLine = l.rstrip('\n')
            jsonData = json.loads(jsonLine)
            for i in jsonData:
                if('http' in jsonData['matched-at'] or 'https' in jsonData['matched-at']):
                    url_post = 'https://localhost:9200/' + target + '-webvuln/_doc?refresh'
                    web['vulnerability.name'] = jsonData['info']['name']
                    web['vulnerability.severity'] = jsonData['info']['severity']
                    try:
                        web['vulnerability.description'] = jsonData['info']['description']
                    except:
                        web['vulnerability.description'] = jsonData['info']['name']
                    web['url.original'] = jsonData['host']
                    try:
                        web['vulnerability.description'] = web['vulnerability.description'] + ' ' + jsonData['matcher-name']
                    except:
                        pass
                    web['url.full'] = jsonData['matched-at']
                    try:
                        web['server.ip'] = jsonData['ip']
                    except:
                        web['server.ip'] = '0.0.0.0'
                    web['reference'] = jsonData['info']['reference']
                    web['network.protocol'] = jsonData['host'].split(':')[0]
                    web['server.address'] = sys.argv[3]
                    web['server.domain'] = web['server.address']
                    web['server.port'] = sys.argv[4]
                    web['url.path'] = sys.argv[5]
                    web['http.response.status_code'] = '200'

                    data = {
                        '@timestamp':time_now,
                        'server.address':web['server.address'],
                        'server.domain':web['server.domain'],
                        'server.ip':web['server.ip'],
                        'server.port':web['server.port'],
                        'network.protocol':web['network.protocol'],
                        'service.name':'N/A',
                        'url.path':web['url.path'],
                        'http.response.status_code':web['http.response.status_code'],
                        'vulnerability.description':web['vulnerability.description'],
                        'vulnerability.name':web['vulnerability.name'],
                        'vulnerability.severity':web['vulnerability.severity'],
                        'url.original':web['url.original'],
                        'url.full':web['url.full'],
                        'vulnerability.scanner.vendor': tool
                    }
                else:
                    url_post = 'https://localhost:9200/' + target + '-infravuln/_doc?refresh'
                    infra['server.address'] = sys.argv[3]
                    infra['vulnerability.name'] = jsonData['info']['name']
                    infra['vulnerability.severity'] = jsonData['info']['severity']
                    try:
                        infra['vulnerability.description'] = jsonData['info']['description']
                    except:
                        infra['vulnerability.description'] = jsonData['info']['name']
                    try:
                        infra['vulnerability.description'] = infra['vulnerability.description'] + ' ' + jsonData['matcher-name']
                    except:
                        pass
                    try:
                        infra['server.ip'] = jsonData['ip']
                    except:
                        infra['server.ip'] = '0.0.0.0'
                    try:
                        infra['server.port'] = jsonData['matched-at'].split(':')[1]
                    except:
                        infra['server.port'] = sys.argv[4]

                    with open(dir + '/../../docker/wordlists/services.txt') as services:
                        for serv in services:
                            serv = serv.rstrip('\n')
                            serv = json.loads(serv)
                            try:
                                infra['network.protocol'] = str(serv[infra['server.port']])
                            except:
                                infra['network.protocol'] = 'N/A'

                    data = {
                        '@timestamp': time_now,
                        'server.address': infra['server.address'],
                        'server.ip': infra['server.ip'],
                        'server.port': infra['server.port'],
                        'network.protocol': infra['network.protocol'],
                        'service.name': 'N/A',
                        'vulnerability.description': infra['vulnerability.description'],
                        'vulnerability.name': infra['vulnerability.name'],
                        'vulnerability.severity': infra['vulnerability.severity'],
                        'vulnerability.scanner.vendor': tool
                    }

            r = requests.post(url_post, headers=headers, auth=auth, data=json.dumps(data), verify=False)
            try:
                message = "Server address: " + web['server.address'] + " Vulnerebility: " + web['vulnerability.description'] + " Severity: " + web['vulnerability.severity'] + "."
            except:
                message = "Server address: " + infra['server.address'] + " Vulnerebility: " + infra['vulnerability.description'] + " Severity: " + infra['vulnerability.severity']
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
