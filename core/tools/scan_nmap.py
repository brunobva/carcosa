#!/usr/bin/env python3

import os
import sys
import uuid
import json
import subprocess
import requests
import urllib3
import xml.etree.ElementTree as ET
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
ip = sys.argv[2]
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
url = 'https://localhost:9200/' + target + '-portscan/_doc?refresh'
url_get = 'https://localhost:9200/' + target + '-subdomain/_search'
auth = ('admin', 'Carcosa123')
time_now = strftime("%Y-%m-%dT%H:%M:%S%Z")
tool = 'nmap'
ports = {}
rand = str(uuid.uuid1())
container_name = target + '-' + 'nmap' + rand
output = 'nmap-' + rand + '.txt'
dir = os.path.dirname(__file__)
os.system('mkdir -p ' + dir + '/../../docker/data/' + target + '/temp/')


def ipBlock(ip):
    data = {"size":10000}
    get_doc = requests.get(url_get, headers=headers, auth=auth, data=json.dumps(data), verify=False)
    parse_scan = json.loads(get_doc.text)
    for x in parse_scan['hits']['hits']:
        if(str(x['_source']['server.ip']) == str(ip)):
            return str(x['_source']['server.ipblock'])


def exec_docker():
    subprocess.check_output(
        'docker run --rm --name ' + container_name + ' -v ' + dir + '/../../docker/data/' + target + '/temp:/data kali-carcosa:1.0 nmap -sSV -Pn ' + ip + ' -oX /data/' + output + ' || true',
        shell=True)


def parse():
    tree = ET.parse(dir + '/../../docker/data/' + target + '/temp/' + output)
    root = tree.getroot()
    for i in root.iter('nmaprun'):
        for nmaprun in i:
            if(nmaprun.tag == 'host'):
                for host in nmaprun:
                    if(host.tag == 'address'):
                        if(':' not in host.attrib['addr']):
                            ports['ip_v4'] = host.attrib['addr']
                            ports['network.type'] = host.attrib['addrtype']
                    if(host.tag == 'ports'):
                        for port in host:
                            if(port.tag == 'port'):
                                ports['network.transport'] = port.attrib['protocol']
                                ports['server.port'] = port.attrib['portid']
                                for itens in port:
                                    if(itens.tag == 'state'):
                                        ports['service.state'] = itens.attrib['state']
                                    if(itens.tag == 'service'):
                                        try:
                                            ports['network.protocol'] = itens.attrib['name']
                                        except:
                                            ports['network.protocol'] = ''
                                        try:
                                            ports['application.version.number'] = itens.attrib['version']
                                        except:
                                            ports['application.version.number'] = ''

                                        try:
                                            ports['service.name'] = itens.attrib['product']
                                        except:
                                            with open(dir + '/../../docker/wordlists/services.txt') as services:
                                                for serv in services:
                                                    serv = serv.rstrip('\n')
                                                    serv = json.loads(serv)
                                                    try:
                                                        ports['service.name'] = str(serv[ports['server.port'].strip()])
                                                    except:
                                                        ports['service.name'] = ''
                                        ports['server.ipblock'] = ipBlock(ip)

                                        data = {
                                            '@timestamp':time_now,
                                            'server.address':ip,
                                            'network.protocol':ports['network.protocol'],
                                            'server.ip':ip,
                                            'server.port':ports['server.port'],
                                            'server.ipblock':ports['server.ipblock'],
                                            'service.name':ports['service.name'],
                                            'service.state':ports['service.state'],
                                            'network.transport':ports['network.transport'],
                                            'network.type':ports['network.type'],
                                            'application.version.number':ports['application.version.number'],
                                            'vulnerability.scanner.vendor':tool
                                        }

                                        r = requests.post(url, headers=headers, auth=auth, data=json.dumps(data), verify=False)
                                        message = "IP: " + ip + " Port: " + ports['server.port'] + ' Service: ' + ports['service.name']
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
