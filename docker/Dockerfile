FROM kalilinux/kali-rolling:latest

WORKDIR /scripts

WORKDIR /data

RUN apt -qq update

RUN apt -qq upgrade -y

RUN apt -qq dist-upgrade -y

RUN apt -qq install locate -y

RUN apt -qq install wget -y

RUN apt -qq install git -y

RUN apt -qq install vim -y

RUN apt -qq install golang -y

RUN apt -qq install python3 -y

RUN apt -qq install python3-pip -y

RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
RUN mv /root/go/bin/subfinder /usr/bin/

RUN apt -qq install feroxbuster -y

RUN apt -qq install sublist3r -y

RUN apt -qq install nmap -y

RUN apt -qq install nikto -y

RUN go install -v github.com/tomnomnom/assetfinder@latest
RUN mv /root/go/bin/assetfinder /usr/bin/

RUN go install -v github.com/openrdap/rdap/cmd/rdap@latest
RUN mv /root/go/bin/rdap /usr/bin/

RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
RUN mv /root/go/bin/httpx /usr/bin/

RUN go install -v github.com/tomnomnom/waybackurls@latest
RUN mv /root/go/bin/waybackurls /usr/bin/

RUN go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
RUN mv /root/go/bin/nuclei /usr/bin/
RUN nuclei -update-templates
