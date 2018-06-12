# -*- coding: utf-8 -*- 
import sys
import socket
import json
import time
import threading as th

#--------------------Input usuario--------------------

#comando add <ip> <weight>
#periodo_tempo para excluir após 4pi
def adicionaRoteador(vizinhos, comando, roteadores):
    endereco = comando[1]
    peso = int(comando[2])
    tamLista = range(len(vizinhos))
    for i in tamLista:
        print(vizinhos[i])
        if(vizinhos[i][0] == endereco):
            if(vizinhos[i][1] > peso):
                vizinhos[i][1] = peso
            return
    vizinhos.append([endereco, peso])
    
    roteadores = vizinhos
    print('roteadores', roteadores)
    # tamLista = range(len(roteadores))
    # for i in tamLista:
    #     print(roteadores[i])
    #     if(roteadores[i][0] == endereco):
    #         if(roteadores[i][1] > peso):
    #             roteadores[i][1] = peso
    #             # roteadores[i][2].append([endereco])
    #         if(roteadores[i][1] == peso):
    #             roteadores[i][2].append([endereco])
    #         return
    # roteadores.append([endereco, peso, [endereco]])
    
#comando del <ip>
def deletaRoteador(vizinhos, comando):
    ip_del = comando[1]
    for item in vizinhos:
         if item[0] == ip_del:
             vizinhos.remove(item)

def leInput(vizinhos, roteadores, addr, conn_udp):
    while True:
        comando = input()
        comando = comando.split(' ')

        if (comando[0] == "add"):
            adicionaRoteador(vizinhos, comando, roteadores)
            print('vizinho adicionado. Estado da tabela:')
            print(vizinhos)
            # print(roteadores)
            continue
        
        if (comando[0] == "del"):
            deletaRoteador(vizinhos, comando)
            print('vizinho deletado. Estado da tabela: ')
            print(vizinhos)
            continue
      
        if(comando[0] == "trace"):
            #criar funcao pra calcular trace
            ipDestino = comando[1]
            pacote = json.dumps({'type': 'trace', 'source': addr, 'destination': ipDestino, 'hops': [addr]})
            if(pacote["source"] == pacote["destination"]):
                print(pacote)
                continue
            
            procuraCaminho(pacote, ipDestino, roteadores, vizinhos)
            continue
        
        #só termina com Ctrl + c 
        else: 
            sys.exit() 


#-------------------Trace--------------------------




def caminhoDireto(ipDestino, roteadores):
    tamLista = range(len(roteadores))
    for i in tamLista:
        if(roteadores[i][0] == ipDestino):
            print("oi")


#comando trace <ip>
def procuraCaminho(pacote, ipDestino, roteadores, vizinhos):
    #faz uma procura com os roteadores ligados DIRETAMENTE ao host
    caminho = caminhoDireto(ipDestino, roteadores)
    if(caminho[0] == True):
        enviaPacote(caminho[1], pacote)

    #faz uma procura com os roteadores ligados INDIRETAMENTE ao host
    caminho = caminhoIndireto(ipDestino, vizinhos)
    if(caminho[0] == True):
        enviaPacote(caminho[1], pacote)

    if(caminho[0] == False):
        return



#------------------Update--------------------------  
#A CADA PI(constante durante a execução do roteador - PERIOD) SEGUNDOS ELE DEVE MANDAR MSG DE UPDATE. 
#ai depois tem que ter um delay e volta a receber comandos
# time.sleep(period)#delay

#Mensagem: UPDATE
#esse daqui manda um "distances" e vai atualizar o peso, mas aparentemente a gente tem que cuidar de "Atualizações periodicas" e "Split Horizon"


#--------------------Send/Recive--------------------
def recebePacote(udp, pacote): 
    while True:
        ip, msg = udp.recvfrom(1024)
        print(msg)
        print(ip)
        if(msg != ""):
            msg = bytes.decode(msg)
            mensagem = json.loads(msg)
            pacote.append(mensagem)


    #****MANDA MENSAGEM******
def enviaPacote(ip_destino, pacote):
    # Manda sua tabela para os vizinhos
    msg = json.dumps(pacote)
    mensagem = bytes(msg, 'utf-8')
    destino = (ip_destino, port)
    conn_udp.sendto(mensagem, destino)


#--------------------Main--------------------

#/router.py <ADDR> <PERIOD> [STARTUP]
# <PERIOD>: tempo para fazer o update

port = 55151
addr = sys.argv[1]
period = sys.argv[2]
# ESSE CAMPO É OPCIONAL
startup = sys.argv[3]

#Listas
roteadores = []
vizinhos = []
pacote = []


#isso daqui vai bindar o roteador com o IP referente a ele,  criado pelo script lá
conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
origem = (addr, port)
conn_udp.bind(origem)

#thread1
threadRecieve = th.Thread(target = recebePacote, args = (conn_udp, pacote))
#recebePacote(pacote)

#thread2
threadInput = th.Thread(target = leInput, args = (vizinhos, roteadores, addr, conn_udp))
#leInput(vizinhos, roteadores, conn_udp)

threadRecieve.start()
threadInput.start()

