import requests
import json
import urllib3
from colorama import Fore, Style

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CreateIndex():
    def __init__(self, project):
        self.project = project
        self.url = 'https://localhost:9200/'
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.auth = ('admin', 'Carcosa123')

    def createSubdomain(self):
        data = {
            "mappings":{
                "properties":{
                    "@timestamp":{"type":"date"},
                    "server.address": {"type":"keyword"},
                    "server.domain": {"type":"keyword"},
                    "server.nameserver": {"type":"keyword"},
                    "server.ip": {"type":"ip"},
                    "server.ipblock": {"type":"keyword"},
                    "vulnerability.scanner.vendor": {"type":"keyword"}
                    }
                }
            }

        print(f"{Fore.LIGHTGREEN_EX}[+] CREATING SUBDOMAIN INDEX{Style.RESET_ALL}")
        r = requests.put(url=self.url + self.project + "-subdomain", headers=self.headers, auth=self.auth,
                         data=json.dumps(data), verify=False)

    def createPortScan(self):
        data = {
            "mappings":{
                "properties":{
                    "@timestamp":{"type":"date"},
                    "server.address": {"type":"keyword"},
                    "network.protocol": {"type":"keyword"},
                    "server.ip": {"type":"ip"},
                    "server.port": {"type":"long"},
                    "server.ipblock": {"type":"keyword"},
                    "service.name": {"type":"keyword"},
                    "service.state": {"type":"keyword"},
                    "application.version.number": { "type":"keyword"},
                    "network.transport": {"type":"keyword"},
                    "network.type": {"type":"keyword"},
                    "vulnerability.scanner.vendor": {"type":"keyword"}
                    }
                }
            }

        print(f"{Fore.LIGHTGREEN_EX}[+] CREATING PORTSCAN INDEX{Style.RESET_ALL}")
        r = requests.put(url=self.url + self.project + "-portscan", headers=self.headers, auth=self.auth,
                         data=json.dumps(data), verify=False)

    def createWebEnum(self):
        data = {
            "mappings":{
                "properties":{
                    "@timestamp":{"type":"date"},
                    "server.address": {"type":"keyword"},
                    "server.domain": {"type":"keyword"},
                    "server.ip": {"type":"ip"},
                    "server.port": {"type":"long"},
                    "network.protocol": {"type":"keyword"},
                    "url.path": {"type":"keyword"},
                    "http.response.status_code": {"type":"long"},
                    "url.original": {"type":"keyword"},
                    "url.full": {"type":"keyword"},
                    "vulnerability.scanner.vendor": {"type":"keyword"}
                    }
                }
            }

        print(f"{Fore.LIGHTGREEN_EX}[+] CREATING WEB ENUM INDEX{Style.RESET_ALL}")
        r = requests.put(url=self.url + self.project + "-webenum", headers=self.headers, auth=self.auth,
                         data=json.dumps(data), verify=False)

    def createWebVuln(self):
        data = {
            "mappings":{
                "properties":{
                    "@timestamp":{"type":"date"},
                    "server.address": {"type":"keyword"},
                    "server.domain": {"type":"keyword"},
                    "server.ip": {"type":"ip"},
                    "server.port": {"type":"long"},
                    "network.protocol": {"type":"keyword"},
                    "service.name": {"type":"keyword"},
                    "url.path": {"type":"keyword"},
                    "http.response.status_code": {"type":"long"},
                    "vulnerability.description": {"type":"keyword"},
                    "vulnerability.name": {"type":"keyword"},
                    "vulnerability.severity": {"type":"keyword"},
                    "url.original": {"type":"keyword"},
                    "url.full": {"type":"keyword"},
                    "vulnerability.scanner.vendor": {"type":"keyword"}
                    }
                }
            }

        print(f"{Fore.LIGHTGREEN_EX}[+] CREATING WEB VULN INDEX{Style.RESET_ALL}")
        r = requests.put(url=self.url + self.project + "-webvuln", headers=self.headers, auth=self.auth,
                         data=json.dumps(data), verify=False)

    def createInfraVuln(self):
        data = {
            "mappings":{
                "properties":{
                    "@timestamp":{"type":"date"},
                    "server.address": {"type":"keyword"},
                    "server.ip": {"type":"ip"},
                    "server.port": {"type":"long"},
                    "network.protocol": {"type":"keyword"},
                    "service.name": {"type":"keyword"},
                    "vulnerability.description": {"type":"keyword"},
                    "vulnerability.name": {"type":"keyword"},
                    "vulnerability.severity": {"type":"keyword"},
                    "vulnerability.scanner.vendor": {"type":"keyword"}
                    }
                }
            }

        print(f"{Fore.LIGHTGREEN_EX}[+] CREATING INFRA VULN INDEX{Style.RESET_ALL}")
        r = requests.put(url=self.url + self.project + "-infravuln", headers=self.headers, auth=self.auth,
                         data=json.dumps(data), verify=False)


class DeleteIndex():
    def __init__(self, project):
        self.project = project
        self.url = 'https://localhost:9200/'
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.auth = ('admin', 'Carcosa123')

    def deleteSubdomain(self):
        print(f"{Fore.LIGHTGREEN_EX}[-] DELETING SUBDOMAIN INDEX{Style.RESET_ALL}")
        r = requests.delete(url=self.url + self.project + "-subdomain", auth=self.auth, verify=False)

    def deletePortScan(self):
        print(f"{Fore.LIGHTGREEN_EX}[-] DELETING PORTSCAN INDEX{Style.RESET_ALL}")
        r = requests.delete(url=self.url + self.project + "-portscan", auth=self.auth, verify=False)

    def deleteWebEnum(self):
        print(f"{Fore.LIGHTGREEN_EX}[-] DELETING WEB ENUM INDEX{Style.RESET_ALL}")
        r = requests.delete(url=self.url + self.project + "-webenum", auth=self.auth, verify=False)

    def deleteWebVuln(self):
        print(f"{Fore.LIGHTGREEN_EX}[-] DELETING WEB VULN INDEX{Style.RESET_ALL}")
        r = requests.delete(url=self.url + self.project + "-webvuln", auth=self.auth, verify=False)

    def deleteInfraVuln(self):
        print(f"{Fore.LIGHTGREEN_EX}[-] DELETING INFRA VULN INDEX{Style.RESET_ALL}")
        r = requests.delete(url=self.url + self.project + "-infravuln", auth=self.auth, verify=False)

