#!/bin/bash

if [ "$EUID" -ne 0 ]
then
		echo "Run with sudo!"
		exit
fi

echo -e "Wich base distro?\n"
echo -e "\n[1] Arch\n[2] Debian Based\n"

read -p '> ' OS

dir=$(pwd)
dock_dir="$dir/docker/"

# CHECK OS
if [ $OS -eq 1 ]
then
		INSTALLER="pacman -S"
else
		INSTALLER="apt install"
fi

echo "[+] UPDATING SYSTEM"

# UPDATE
if [ $OS -eq 1 ]
then
		pacman -Sy
else
		apt update  
fi

echo "[+] CHECKING AND INSTALL DOCKER"

# CHECK/INSTALL DOCKER AND DEPENDENCES
if [ $OS -eq 1 ]
then
	dock=$(pacman -Q docker | grep docker | wc -l)
	dock_comp=$(pacman -Q docker-compose | grep docker | wc -l)
	paral=$(pacman -Q parallel | grep parallel | wx -l)
else
	dock=$(dpkg -l docker.io | grep Version | wc -l)
	dock_comp=$(dpkg -l docker-compose | grep Version | wc -l)
	paral=$(dpkg -l parallel | grep Version | wc -l)
fi

if [ $dock -eq 0 ]
then
		if [ $OS -eq 1 ]
		then
				echo y | $INSTALLER docker
		else
				echo y | $INSTALLER docker.io 
		fi
fi

if [ $dock_comp -eq 0 ]
then
		echo y | $INSTALLER docker-compose 
fi

if [ $paral -eq 0 ]
then
		echo y | $INSTALLER parallel 
fi

echo "[+] BUILDING CARCOSA CONTAINER"

# SETUP DOCKERS
cd $dock_dir
docker image build -t kali-carcosa:1.0 .

echo "[+] GENERATING ELASTIC CERTIFICATE"

# certs db
openssl genrsa -out certs/root-ca-key.pem 2048
openssl req -new -x509 -sha256 -key certs/root-ca-key.pem -out certs/root-ca.pem -days 10000 -subj "/C=US/ST=Carcosa/L=Carcosa/O=Carcosa Security/OU=IT/CN=carcosa.com"
openssl genrsa -out certs/admin-ca-key.pem 2048
openssl pkcs8 -inform PEM -outform PEM -in certs/admin-ca-key.pem -topk8 -nocrypt -v1 PBE-SHA1-3DES -out certs/admin-key.pem
openssl req -new -key certs/admin-key.pem -out certs/admin.csr -subj "/C=US/ST=Carcosa/L=Carcosa/O=Carcosa Security/OU=IT/CN=carcosa.com"
openssl x509 -req -in certs/admin.csr -CA certs/root-ca.pem -CAkey certs/root-ca-key.pem -CAcreateserial -sha256 -out certs/admin.pem -days 10000

chmod 777 -R certs/

docker-compose up -d
docker-compose down

echo "[+] INSTALLING PYTHON DEPENDECES"

cd $dir
pip install -r requirements.txt

echo "[+] INSTALATION COMPLETE"
