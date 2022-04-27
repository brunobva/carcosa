# CARCOSA

Carcosa é uma ferramenta para automatização da fase inicial do reconhecimento baseado em containers.

Contando com um fluxo de execução que se inicia a partir de um domínio, a ferramenta passa por **portscan**, **dirscan** e **vulnscan** salvando todas as informações em um banco de dados **Elastic**.

## Paralelismo

Carcosa utiliza a ferramenta **parallel** para paralelizar as rotinas aproveitando da melhor forma os recuros do seu host.

## Consumo de dados

Os dados gerados pelo Carcosa são salvos em um banco de dados Elastic e podem ser consultados a qualquer momento pelo menu da aplicação, além de serem extraídos no formato **CSV**.

## Alertas via Telegram

É necessário que um **bot** seja criado no Telegram e seu *Token* assim como o *id*  da conversa sejam cadastrados no arquivo `core/config/config.ini`.