#!/usr/bin/env python3

import os
import sys
import uuid
import json
import subprocess
import requests
import socket
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
domain = sys.argv[2]
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url = 'https://localhost:9200/' + target + '-subdomain/_doc?refresh'
auth = ('admin', 'Carcosa123')
time_now = strftime("%Y-%m-%dT%H:%M:%S%Z")
tool = 'subfinder'
subdomains = {}
rand = str(uuid.uuid1())
container_name = target + '-' + 'subfinder' + rand
output = 'subfinder-' + rand + '.txt'
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')


def ip_scan(ip):
    try:
        req = subprocess.check_output(
            'docker run --rm --name ' + container_name + ' -v ' + dir + '/../../docker/data/' + target + '/temp:/data kali-carcosa:1.0 /usr/bin/rdap ' + ip + ' --json || true',
            shell=True)
        json_ip = json.loads(req)
        ip_block = json_ip['handle']
        return ip_block
    except:
        return ""


def domain_scan(domain):
    nameserver = ""
    try:
        req = requests.get('https://rdap.registro,br/domain/' + domain)
        json_domain = json.loads(req.text)
        for ns in json_domain['nameservers']:
            nameserver = nameserver + ns['ldhName']
        return nameserver[:-1]
    except:
        return ""


def exec_docker():
    subprocess.check_output(
        'docker run --rm --name ' + container_name + ' -v ' + dir + '/../../docker/data/' + target + '/temp:/data kali-carcosa:1.0 subfinder -d ' + domain + ' -oJ -silent >> ' + dir + '/../../docker/data/' + target + '/temp/' + output + '  || true',
        shell=True)


def parse():
    with open(dir + '/../../docker/data/' + target + '/temp/' + output) as file:
        for l in file:
            json_line = l.rstrip('\n')
            json_data = json.loads(json_line)
            subdomains['timestamp'] = time_now
            subdomains['server.address'] = json_data['host']
            subdomains['server.domain'] = json_data['host']
            try:
                subdomains['server.ip'] = socket.gethostbyname(json_data['host'])
            except:
                subdomains['server.ip'] = '0.0.0.0'
            subdomains['vulnerability.scanner.vendor'] = tool
            subdomains['server.ipblock'] = ip_scan(subdomains['server.ip'])
            subdomains['server.nameserver'] = domain_scan(subdomains['server.domain'])

            data = {
                '@timestamp': subdomains['timestamp'],
                'server.address': subdomains['server.address'],
                'server.domain': subdomains['server.domain'],
                'server.ip': subdomains['server.ip'],
                'server.ipblock': subdomains['server.ipblock'],
                'server.nameserver': subdomains['server.nameserver'],
                'vulnerability.scanner.vendor': subdomains['vulnerability.scanner.vendor']
            }

            r = requests.post(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
            message = "Tool: " + subdomains['vulnerability.scanner.vendor'] + " Subdomain: " + subdomains['server.address'] + " IP: " + subdomains['server.ip']
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
