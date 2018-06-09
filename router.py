# -*- coding: utf-8 -*- 
import sys
import socket
import json
import time
import _thread as thread

#/router.py <ADDR> <PERIOD> [STARTUP]
# <PERIOD>: tempo para fazer o update

port = 55151
addr = sys.argv[1]
period = sys.argv[2]
# ESSE CAMPO É OPCIONAL
startup = sys.argv[3]

#Listas
roteadores = []
lista_vizinhos = []

#-------------------Trace--------------------------
#payload = mensagem trace
def criaMensagemData(ipDestino, ipOrigem, payload):
    print(json.dumps({'type': 'data', 'source': ipOrigem, 'destination': ipDestino, 'payload': payload}, indent=2))

#comando trace <ip>
def criaRota(lista_vizinhos, comando, ipOrigem):
    ipDestino = comando[1]
    hops = [ipOrigem]
    
    #cria JSON de trace
    msgTrace = json.dumps({'type': 'trace', 'source': ipOrigem, 'destination': ipDestino, 'hops': hops}, indent=2)
    print(msgTrace)
    #cria payload para usar em msgData
    payload = json.dumps({'type': 'trace', 'source': ipOrigem, 'destination': ipDestino, 'hops': hops})
    criaMensagemData(ipDestino, ipOrigem, payload)


#------------------Update--------------------------  
#A CADA PI(constante durante a execução do roteador - PERIOD) SEGUNDOS ELE DEVE MANDAR MSG DE UPDATE. 
#ai depois tem que ter um delay e volta a receber comandos
# time.sleep(period)#delay

#Mensagem: UPDATE
#esse daqui manda um "distances" e vai atualizar o peso, mas aparentemente a gente tem que cuidar de "Atualizações periodicas" e "Split Horizon"

#-----------------Thread e chamada de função--------
# thread.start_new_thread(função, (conexão,)) 


#--------------------Send/Recive--------------------
def connection(lista_vizinhos): 

    #isso daqui vai bindar o roteador com o IP referente a ele,  criado pelo script lá
    conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #****RECEBE MENSAGEM*****
    origem = (addr, port)
    conn_udp.bind(origem)
    while True:
        msg, vizinho = udp.recvfrom(1024)
        print(msg)
        print(vizinho)
    conn_udp.close()


    #****MANDA MENSAGEM******
    # Manda sua tabela para os vizinhos
    mensagem = []
    for item in lista_vizinhos:
        mensagem.append([item[0], item[1]])

    for item in lista_vizinhos: 
        ip_destino = item[0]
        destino = (ip_destino, port)
        conn_udp.sendto(mensagem, destino)
    conn_udp.close()

#--------------------Input usuario--------------------

#comando add <ip> <weight>
#periodo_tempo para excluir após 4pi
def adicionaRoteador(tabela, host, custo, salto, periodo_tempo):
    tabela.append([host, custo, salto, periodo_tempo])
  
#comando del <ip>
def deletaRoteador(lista_vizinhos, comando):
    ip_del = comando[1]
    for item in lista_vizinhos:
         if item[0] == ip_del:
             lista_vizinhos.remove(item)

while True:
    comando = input()
    comando = comando.split(' ')

    if (comando[0] == "add"):
        host = comando[1]
        custo = comando[2]
        salto = host
        periodo_tempo = 0
        adicionaRoteador(lista_vizinhos, host, custo, salto, periodo_tempo)
        print('vizinho adicionado. Estado da tabela:')
        print(lista_vizinhos)
        continue
    
    if (comando[0] == "del"):
        deletaRoteador(lista_vizinhos, comando)
        print('vizinho deletado. Estado da tabela: ')
        print(lista_vizinhos)
        continue
  
    if(comando[0] == "trace"):
        #criar funcao pra calcular trace
        criaRota(lista_vizinhos, comando, addr)
        print("trace")
        continue
    
    #só termina com Ctrl + c 
    else: 
        sys.exit() 


