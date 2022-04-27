#!/usr/bin/python3

import requests
import json
import urllib3
import os
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pd.options.display.max_colwidth = 50

class Export():
    def __init__(self, project):
        self.project = project
        self.url_get = 'https://localhost:9200/' #+ self.project + '-subdomain/_search'
        self.auth = ('admin', 'Carcosa123')
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        self.save_dir = '/tmp/' + self.project
        self.data = {"size":10000}

    def subdomains(self):
        os.system('mkdir -p ' + self.save_dir)
        get_doc = requests.get(self.url_get + self.project + '-subdomain/_search', headers=self.headers, auth=self.auth,
                               data=json.dumps(self.data), verify=False)
        js = json.loads(get_doc.text)
        n = 0
        for i in js['hits']['hits']:
            i = i["_source"]
            if n == 0:
                df = pd.DataFrame.from_records([i])
            else:
                df = pd.concat([df, pd.DataFrame.from_records([i])]).drop_duplicates()
            n += 1

        # print(f"\n\t{Fore.LIGHTGREEN_EX}[+] SUBDOMAINS COMPLETE\n{Fore.LIGHTYELLOW_EX}")
        # df = df.rename(columns={"@timestamp": "data.consulta"})
        # # df.to_csv(self.save_dir + '/subdomains-' + self.project + '.csv', index=False)
        # print(tabulate(df, headers='keys', tablefmt='psql'))

        print(f"\n\t{Fore.LIGHTGREEN_EX}[+] SUBDOMAINS SIMPLE\n{Fore.LIGHTYELLOW_EX}")
        df_simple = df[['server.domain', 'server.ip']].drop_duplicates()
        df_simple.to_csv(self.save_dir + '/subdomains_simple-' + self.project + '.csv', index=False, sep=";")
        print(tabulate(df_simple, headers='keys', tablefmt='psql'))
        print(f"{Fore.LIGHTGREEN_EX}[+] File saved on {self.save_dir + '/subdomains_simple-' + self.project + '.csv'}{Style.RESET_ALL}\n\n")

    def portscan(self):
        os.system('mkdir -p ' + self.save_dir)
        get_doc = requests.get(self.url_get + self.project + '-portscan/_search', headers=self.headers, auth=self.auth,
                               data=json.dumps(self.data), verify=False)
        js = json.loads(get_doc.text)
        n = 0
        for i in js['hits']['hits']:
            i = i["_source"]
            if n == 0:
                df = pd.DataFrame.from_records([i])
            else:
                df = pd.concat([df, pd.DataFrame.from_records([i])]).drop_duplicates()
            n += 1

        # print(f"\n\t{Fore.LIGHTYELLOW_EX}[+] PORTSCAN COMPLETE\n")
        # df = df.rename(columns={"@timestamp": "data.consulta"})
        # df = df[["data.consulta", "server.ip", "server.port", "network.protocol", "service.name",
        #          "service.state", "network.type", "application.version.number", "vulnerability.scanner.vendor"]]
        # df = df.sort_values(by=["server.ip", "server.port"])
        # # df.to_csv(self.save_dir + '/portscan-' + self.project + '.csv', index=False)
        # print(tabulate(df, headers='keys', tablefmt='psql'))

        print(f"\n\t{Fore.LIGHTGREEN_EX}[+] PORTSCAN SIMPLE (Limited Top 20){Fore.LIGHTYELLOW_EX}\n")
        df_simple = df[["server.ip", "server.port", "network.type", "network.protocol", "service.state", "service.name"]].drop_duplicates()
        df_simple = df_simple.sort_values(by=["server.ip", "server.port"])
        df_simple.to_csv(self.save_dir + '/portscan_simple-' + self.project + '.csv', index=False, sep=";")
        df_simple = df_simple.head(20)
        print(tabulate(df_simple, headers='keys', tablefmt='psql'))
        print(f"{Fore.LIGHTGREEN_EX}[+] File saved on {self.save_dir + '/portscan_simple-' + self.project + '.csv'}{Style.RESET_ALL}\n\n")

    def webEnum(self):
        os.system('mkdir -p ' + self.save_dir)
        get_doc = requests.get(self.url_get + self.project + '-webenum/_search', headers=self.headers, auth=self.auth,
                               data=json.dumps(self.data), verify=False)
        js = json.loads(get_doc.text)
        n = 0
        for i in js['hits']['hits']:
            i = i["_source"]
            if n == 0:
                df = pd.DataFrame.from_records([i])
            else:
                df = pd.concat([df, pd.DataFrame.from_records([i])]).drop_duplicates()
            n += 1

        print(f"\n\t{Fore.LIGHTGREEN_EX}[+] WEBENUM SIMPLE (Limited Top 20){Fore.LIGHTYELLOW_EX}\n")
        df_simple = df[["server.address", "network.protocol", "url.original", "url.full",
                        "http.response.status_code"]].drop_duplicates()
        df_simple = df_simple.sort_values(by=["server.address", "url.full"])
        df_simple.to_csv(self.save_dir + '/webenum_simple-' + self.project + '.csv', index=False, sep=";")
        df_simple = df_simple.head(20)
        print(tabulate(df_simple, headers='keys', tablefmt='psql', ))
        print(f"{Fore.LIGHTGREEN_EX}[+] File saved on {self.save_dir + '/webenum_simple-' + self.project + '.csv'}{Style.RESET_ALL}\n\n")

    def webVuln(self):
        os.system('mkdir -p ' + self.save_dir)
        get_doc = requests.get(self.url_get + self.project + '-webvuln/_search', headers=self.headers, auth=self.auth,
                               data=json.dumps(self.data), verify=False)
        js = json.loads(get_doc.text)
        n = 0
        for i in js['hits']['hits']:
            i = i["_source"]
            if n == 0:
                df = pd.DataFrame.from_records([i])
            else:
                df = pd.concat([df, pd.DataFrame.from_records([i])]).drop_duplicates()
            n += 1

        # print(f"\n\t{Fore.LIGHTYELLOW_EX}[+] WEBVULN COMPLETE\n")
        df = df.rename(columns={"@timestamp": "data.consulta"})
        df = df.sort_values(by=["server.address"])
        df.to_csv(self.save_dir + '/webvuln-' + self.project + '.csv', index=False, sep=";")

        print(f"\n\t{Fore.LIGHTGREEN_EX}[+] WEBVULN SIMPLE (Limited Top 20){Fore.LIGHTYELLOW_EX}\n")
        df_simple = df[["server.address", "server.port", "network.protocol", "service.name", "url.path",
                        "vulnerability.name", "vulnerability.severity"]].drop_duplicates()
        # df_simple = df_simple.sort_values(by=["server.ip", "server.port"])
        df_simple.to_csv(self.save_dir + '/webvuln_simple-' + self.project + '.csv', index=False, sep=";")
        df_simple = df_simple.head(20)
        print(tabulate(df_simple, headers='keys', tablefmt='psql'))
        print(f"{Fore.LIGHTGREEN_EX}[+] File saved on {self.save_dir + '/webvuln_simple-' + self.project + '.csv'}{Style.RESET_ALL}\n\n")

    def infraVuln(self):
        os.system('mkdir -p ' + self.save_dir)
        get_doc = requests.get(self.url_get + self.project + '-infravuln/_search', headers=self.headers, auth=self.auth,
                               data=json.dumps(self.data), verify=False)
        js = json.loads(get_doc.text)
        n = 0
        for i in js['hits']['hits']:
            i = i["_source"]
            if n == 0:
                df = pd.DataFrame.from_records([i])
            else:
                df = pd.concat([df, pd.DataFrame.from_records([i])]).drop_duplicates()
            n += 1

        # # print(f"\n\t{Fore.LIGHTYELLOW_EX}[+] WEBVULN COMPLETE\n")
        df = df.rename(columns={"@timestamp": "data.consulta"})
        df = df.sort_values(by=["server.address"])
        df.to_csv(self.save_dir + '/infravuln-' + self.project + '.csv', index=False, sep=";")

        print(f"\n\t{Fore.LIGHTGREEN_EX}[+] INFRAVULN SIMPLE (Limited Top 20){Fore.LIGHTYELLOW_EX}\n")
        df_simple = df[["server.address", "server.ip", "server.port", "network.protocol", "service.name",
                        "vulnerability.name", "vulnerability.severity"]].drop_duplicates()
        # df_simple = df_simple.sort_values(by=["server.ip", "server.port"])
        df_simple.to_csv(self.save_dir + '/infravuln_simple-' + self.project + '.csv', index=False, sep=";")
        df_simple = df_simple.head(20)
        print(tabulate(df_simple, headers='keys', tablefmt='psql'))
        print(f"{Fore.LIGHTGREEN_EX}[+] File saved on {self.save_dir + '/portscan_simple-' + self.project + '.csv'}{Style.RESET_ALL}\n\n")
