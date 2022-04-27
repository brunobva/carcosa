#!/usr/bin/python3

import configparser
import os
import sys
import telegram
import requests
import json
import urllib3
from core.tools.carcosaExport import Export
from index.indexes import CreateIndex, DeleteIndex
from colorama import Fore, Style
from time import sleep

basedir = os.path.dirname(os.path.realpath(__file__))

config = configparser.ConfigParser()
config.read(f'{basedir}/core/config/config.ini')
telegram_token = config['TELEGRAM']['token']
chat_id = config['TELEGRAM']['chat']

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
url = 'https://localhost:9200/_cat/indices/'
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
auth = ('admin', 'Carcosa123')

def telegramMsg(msg):
    bot = telegram.Bot(token=telegram_token)
    bot.send_message(text=msg, chat_id=chat_id)

def banner():
    print(f"""{Fore.LIGHTYELLOW_EX}
.s5SSSs.  .s5SSSs.  .s5SSSs.  .s5SSSs.  .s5SSSs.  .s5SSSs.  .s5SSSs.  
      SS.       SS.       SS.       SS.       SS.       SS.       SS. 
sS    `:; sS    S%S sS    S%S sS    `:; sS    S%S sS    `:; sS    S%S 
SS        SS    S%S SS    S%S SS        SS    S%S SS        SS    S%S 
SS        SSSs. S%S SS .sS;:' SS        SS    S%S `:;;;;.   SSSs. S%S 
SS        SS    S%S SS    ;,  SS        SS    S%S       ;;. SS    S%S 
SS        SS    `:; SS    `:; SS        SS    `:;       `:; SS    `:; 
SS    ;,. SS    ;,. SS    ;,. SS    ;,. SS    ;,. .,;   ;,. SS    ;,. 
`:;;;;;:' :;    ;:' `:    ;:' `:;;;;;:' `:;;;;;:' `:;;;;;:' :;    ;:' 

Developed by: H41stur
______________________________________________ 
{Style.RESET_ALL}""")

def checkRoot():
    user = os.getenv("SUDO_USER")
    if user is None:
        print(f"\n[{Fore.RED}-{Style.RESET_ALL}] Carcosa precisa ser executado com sudo!\n")
        sys.exit()

def startDb():
    os.system('systemctl restart docker')
    os.system('sysctl -w vm.max_map_count=262144')
    os.system('docker-compose -f ' + basedir + '/docker/docker-compose.yml up -d')
    print(f"{Fore.LIGHTYELLOW_EX}\n\t[+] STARTING DATABASE SERVICE...")

    while True:
        try:
            r = requests.get(url=url, headers=headers, auth=auth, verify=False)
            break
        except:
            sleep(1)

def menu():
    print(f"""{Fore.LIGHTGREEN_EX}
        What do you want to do??\n\n
    {Fore.LIGHTGREEN_EX}\t[1] {Fore.LIGHTYELLOW_EX}Create a project
    {Fore.LIGHTGREEN_EX}\t[2] {Fore.LIGHTYELLOW_EX}List projects
    {Fore.LIGHTGREEN_EX}\t[3] {Fore.LIGHTYELLOW_EX}View and extract report
    {Fore.LIGHTGREEN_EX}\t[4] {Fore.LIGHTYELLOW_EX}Rebuild a project
    {Fore.LIGHTGREEN_EX}\t[5] {Fore.LIGHTYELLOW_EX}Delete a project
    {Fore.LIGHTGREEN_EX}\t[6] {Fore.LIGHTYELLOW_EX}Exit
""")
    option = input(f"> {Style.RESET_ALL}")
    return option

def createProject():
    print(f"{Fore.LIGHTYELLOW_EX}\nName the project (without spaces):")
    proj = input(f"> {Style.RESET_ALL}")
    proj = proj.lower()
    indexes = []
    if " " in proj:
        createProject()
    r = requests.get(url=url, headers=headers, auth=auth, verify=False)
    resp = json.loads(r.text)
    for i in resp:
        project = i['index']
        if "webenum" in project:
            project = project.replace("-webenum", "")
            if project not in indexes:
                indexes.append(project)

    for i in indexes:
        if proj == i:
            print(f"\n[{Fore.RED}-{Style.RESET_ALL}] Project {proj} already exists!")
            menuChoice(menu())

    os.system('mkdir -p ' + basedir + '/docker/data/' + proj)
    print(f"{Fore.LIGHTYELLOW_EX}\n\n\t[+]CREATING DATABASES[+]\n\n")

    crt = CreateIndex(proj)
    crt.createSubdomain()
    crt.createPortScan()
    crt.createWebEnum()
    crt.createWebVuln()
    crt.createInfraVuln()

    print(f"\nInform the Domain or Domains separated by a comma:")
    domain = input(f"{Fore.LIGHTYELLOW_EX}> {Style.RESET_ALL}")
    domains = domain.split(',')
    telegramMsg('[+]STARTING SCAN[+]')
    for i in domains:
        i = i.strip()
        os.system('python3 ' + basedir + '/core/automate/parallel_subdomains.py ' + proj + ' ' + i)
    os.system('python3 ' + basedir + '/core/automate/parallel_nmap.py ' + proj)
    os.system('python3 ' + basedir + '/core/automate/parallel_httpx.py ' + proj)
    os.system('python3 ' + basedir + '/core/automate/parallel_wayback.py ' + proj)
    os.system('python3 ' + basedir + '/core/automate/parallel_feroxbuster.py ' + proj)
    os.system('python3 ' + basedir + '/core/automate/parallel_nuclei.py ' + proj)

    os.system('rm -rf ' + basedir + '/docker/data/' + proj)

    print(f"{Fore.LIGHTGREEN_EX}[+]{Style.RESET_ALL} End of scan {proj}!")

    print(f"{Fore.LIGHTYELLOW_EX}\n--------------------------------------------------------------\n{Style.RESET_ALL}")

def listProjects():
    indexes = []
    r = requests.get(url=url, headers=headers, auth=auth, verify=False)
    resp = json.loads(r.text)
    for i in resp:
        project = i['index']
        if "webenum" in project:
            project = project.replace("-webenum", "")
            if project not in indexes:
                indexes.append(project)

    print(f'\n\t{Fore.LIGHTGREEN_EX}PROJECTS:\n')
    n = 1
    for i in indexes:
        print(f"{Fore.LIGHTGREEN_EX}\t[{n}] {Fore.LIGHTYELLOW_EX} {i} ")
        n += 1

    print(f"{Fore.LIGHTYELLOW_EX}\n--------------------------------------------------------------\n{Style.RESET_ALL}")

def rebuildProject():
    indexes = []
    dictProj = {}
    r = requests.get(url=url, headers=headers, auth=auth, verify=False)
    resp = json.loads(r.text)
    for i in resp:
        project = i['index']
        if "webenum" in project:
            project = project.replace("-webenum", "")
            if project not in indexes:
                indexes.append(project)

    print(f'\n\t{Fore.LIGHTGREEN_EX}WHICH PROJECT TO REBUILD?\n')
    n = 1
    for i in indexes:
        dictProj[str(n)] = i
        print(f"{Fore.LIGHTGREEN_EX}\t[{n}] {Fore.LIGHTYELLOW_EX} {i} ")
        n += 1

    proj = input(f"\n> {Style.RESET_ALL}")
    try:
        print(f"\n\t{Fore.LIGHTYELLOW_EX} DO YOU REALLY WANNA REBUILD ALL THE PROJECT {dictProj[proj].upper()}?[y/n]")
    except:
        print(f"[-] INVALID OPTION")
        rebuildProject()

    opt = input(f"> {Style.RESET_ALL}")
    print(f"{Fore.LIGHTYELLOW_EX}\n")
    if opt == "y" or opt == "Y":

        delete = DeleteIndex(dictProj[proj])
        delete.deleteSubdomain()
        delete.deletePortScan()
        delete.deleteWebEnum()
        delete.deleteWebVuln()
        delete.deleteInfraVuln()

        print(f"\n\t{Fore.LIGHTYELLOW_EX} Project {dictProj[proj]} excluded!{Style.RESET_ALL}")
        createProject()
    elif opt == "n" or opt == "N":
        menuChoice(menu())
    else:
        print(f"[-] INVALID OPTION")
        menuChoice(menu())

def deleteProject():
    indexes = []
    dictProj = {}
    r = requests.get(url=url, headers=headers, auth=auth, verify=False)
    resp = json.loads(r.text)
    for i in resp:
        project = i['index']
        if "webenum" in project:
            project = project.replace("-webenum", "")
            if project not in indexes:
                indexes.append(project)

    print(f'\n\t{Fore.LIGHTGREEN_EX}WHICH PROJECT TO DELETE?\n')
    n = 1
    for i in indexes:
        dictProj[str(n)] = i
        print(f"{Fore.LIGHTGREEN_EX}\t[{n}] {Fore.LIGHTYELLOW_EX} {i} ")
        n += 1

    proj = input(f"\n> {Style.RESET_ALL}")
    try:
        print(f"\n\t{Fore.LIGHTYELLOW_EX} DO YOU REALLY WANNA DELETE THE PROJECT {dictProj[proj].upper()}?[y/n]")
    except:
        print(f"[-] INVALID OPTION")
        rebuildProject()

    opt = input(f"> {Style.RESET_ALL}")
    print(f"{Fore.LIGHTYELLOW_EX}\n")
    if opt == "y" or opt == "Y":

        delete = DeleteIndex(dictProj[proj])
        delete.deleteSubdomain()
        delete.deletePortScan()
        delete.deleteWebEnum()
        delete.deleteWebVuln()
        delete.deleteInfraVuln()

        print(f"\n\t{Fore.LIGHTYELLOW_EX} Project {dictProj[proj]} excluded!{Style.RESET_ALL}")
        print(f"{Fore.LIGHTYELLOW_EX}\n--------------------------------------------------------------\n{Style.RESET_ALL}")
        menuChoice(menu())
    elif opt == "n" or opt == "N":
        menuChoice(menu())
    else:
        print(f"[-] INVALID OPTION")
        menuChoice(menu())

def extractReport():
    indexes = []
    dictProj = {}
    r = requests.get(url=url, headers=headers, auth=auth, verify=False)
    resp = json.loads(r.text)
    for i in resp:
        project = i['index']
        if "webenum" in project:
            project = project.replace("-webenum", "")
            if project not in indexes:
                indexes.append(project)

    print(f'\n\t{Fore.LIGHTGREEN_EX}WHICH PROJECT TO EXTRACT?\n')
    n = 1
    for i in indexes:
        dictProj[str(n)] = i
        print(f"{Fore.LIGHTGREEN_EX}\t[{n}] {Fore.LIGHTYELLOW_EX} {i} ")
        n += 1

    proj = input(f"\n> {Style.RESET_ALL}")
    try:
        test = dictProj[proj]
    except:
        print(f"[-] INVALID OPTION")
        extractReport()

    print(f"{Fore.LIGHTGREEN_EX}\n\t[+] ALL THE FILES WILL BE SAVED ON /tmp/{dictProj[proj]}/")
    print(f"\t[+] EXTRACTING...")
    sleep(2)

    try:
        extract = Export(dictProj[proj])
        extract.subdomains()
        extract.portscan()
        extract.webEnum()
        extract.webVuln()
        extract.infraVuln()
    except:
        print(f"{Fore.LIGHTGREEN_EX}\n\t[+] THERE IS NO DATA ON THE PROJECT {dictProj[proj].upper()}")
        menuChoice(menu())

    print(f"{Fore.LIGHTYELLOW_EX}\n--------------------------------------------------------------\n{Style.RESET_ALL}")




def exitCarcosa():
    os.system('docker-compose -f ' + basedir + '/docker/docker-compose.yml down')

def menuChoice(choice):
    try:
        choice = int(choice)
    except:
        menuChoice(menu())

    if choice == 1:
        createProject()
        menuChoice(menu())
    elif choice == 2:
        listProjects()
        menuChoice(menu())
    elif choice == 3:
        extractReport()
        menuChoice(menu())
    elif choice == 4:
        rebuildProject()
        menuChoice(menu())
    elif choice == 5:
        deleteProject()
        menuChoice(menu())
    elif choice == 6:
        print(f'\n{Fore.LIGHTYELLOW_EX}\x1B[3m"Strange is the night where black stars rise, and strange moons circle through the skies. But stranger still is lost Carcosa.”\x1B[0m\n{Style.RESET_ALL}')
        exitCarcosa()
        sys.exit()
    else:
        print(f"\n[+] INVALID OPtION")
        menuChoice(menu())


def main():
    try:
        banner()
        checkRoot()
        startDb()
        menuChoice(menu())
    except KeyboardInterrupt:
        print(f'\n{Fore.LIGHTYELLOW_EX}\x1B[3m"Strange is the night where black stars rise, and strange moons circle through the skies. But stranger still is lost Carcosa.”\x1B[0m\n{Style.RESET_ALL}')
        exitCarcosa()
        sys.exit()


if __name__ == '__main__':
    main()
