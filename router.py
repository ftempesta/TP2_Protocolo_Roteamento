# -*- coding: utf-8 -*- 
import sys
import socket
import json
import time
import threading as th
from random import *

#--------------------Input usuario--------------------

#comando add <ip> <weight>
#periodo_tempo para excluir após 4pi
def adicionaVizinho(vizinhos, comando, roteadores):
    endereco = comando[1]
    peso = int(comando[2])
    tamLista = range(len(vizinhos))
    for i in tamLista:
        # print(vizinhos[i])
        if(vizinhos[i][0] == endereco):
            if(vizinhos[i][1] > peso):
                vizinhos[i][1] = peso
            return
    vizinhos.append([endereco, peso, time.time()])
    #salto é o proprio endereço em roteadores
    roteadores.append([endereco, peso, endereco, time.time()])
    # print('roteadores', roteadores)
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
            adicionaVizinho(vizinhos, comando, roteadores)
            # print('vizinho adicionado', vizinhos)
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
            pacote = {'type': 'trace', 'source': addr, 'destination': ipDestino, 'hops': [addr]}
            print(pacote)
            if(pacote['source'] == pacote['destination']):# # #  é seu próprio endereço
                print('Destino é seu próprio endereço')
                # # print(pacote)
                continue
             
            procuraCaminho(pacote, ipDestino, roteadores, vizinhos)
            continue
        else:
            print('Comando inválido!')
            sys.exit()


#-------------------Trace--------------------------



#comando trace <ip>
def procuraCaminho(pacote, ipDestino, roteadores, vizinhos):
    # tamLista = range(len(vizinhos))
    # for i in tamLista:
    #     if(vizinhos[i][0] == ipDestino):
    #         print('existe endereco na tabela vizinhos')
    #         print(vizinhos[i][0])# # 
    #         print('pacote', pacote)
    #         enviaPacote(ipDestino, pacote)
    #         break 
    #     else:
    #         tamLista = range(len(roteadores))
    #         rotas = []
    #         for i in tamLista:
    #             if(roteadores[i][0] == ipDestino):
    #                 rotas.append(roteadores[i])
    #                 print('existe endereco na tabela roteadores,', roteadores[i][0])
    #                 enviaPacote(ipDestino, pacote)
    #                 break
    #             else:
    #                 print('não existe endereco na tabela de roteamento')
    # # valormin = min(vetor)
    tamLista = range(len(roteadores))
    rotas = []
    presente = False
    for i in tamLista:
        if(roteadores[i][0] == ipDestino):
            rotas.append(roteadores[i])
            presente = True
    if(presente == False):
        print('não existe endereco na tabela de roteamento')
            # print('existe endereco na tabela roteadores,', roteadores[i][0])
    menorPeso = 10000
    rotasMenoresPesos = []
    for rota in rotas:
        if(rota[1] < menorPeso):
            menorRota = rota[0]
            menorPeso = rota[1]
        if(rota[1] == menorPeso):
            rotasMenoresPesos.append(rota)
    #randomico 
    if(len(rotasMenoresPesos) >= 2):
        random = randint(0, len(rotasMenoresPesos)-1)
        print('random', random)
        # menorRota = min(rotas[1])
        print('menores roteas', rotasMenoresPesos)
        print('destino trace', rotasMenoresPesos[random[0]])
        enviaPacote(rotasMenoresPesos[random[0]], pacote)
 
#  add 127.0.1.
#  trace 127.0.1.2
#------------------Update--------------------------  
#A CADA PI(constante durante a execução do roteador - PERIOD) SEGUNDOS ELE DEVE MANDAR MSG DE UPDATE. 
#ai depois tem que ter um delay e volta a receber comandos
# time.sleep(period)#delay

#Mensagem: UPDATE

def excluiRotasInativas(vizinhos, roteadores, period):
     #limpar rotas de Vizinhos que expiraram
        for v in vizinhos:
            if (v[2]+4*period < time.time()):
                vizinhos.remove(v)
        #limpar rotas de roteadores que expiraram
        for r in roteadores:
            if (r[3]+4*period < time.time()):
                roteadores.remove(r)

#esse daqui manda um "distances" e vai atualizar o peso, mas aparentemente a gente tem que cuidar de "Atualizações periodicas" e "Split Horizon"
def update(vizinhos, roteadores, addr, period):
    while True:
        excluiRotasInativas(vizinhos, roteadores, period)
        #cria a mensagem de Update
        distance = []
        for v in vizinhos:
            destino = v[0]
            print('verifica prox destino', destino)
            for v1 in vizinhos:
                print('passa pelos vizinhos', v)
                if (v1[0] == destino):
                    continue
                else:
                    print('entrou', v1[0], destino)
                    # continue
                    distance.append([v1[0], v1[1]])
                print('distance', distance)
            #cria pacote update
            msgUpdate = {'type': 'update', 'source': addr, 'destination': destino, 'distances': json.dumps(distance)}
            #manda pacote update
            enviaPacote(destino, msgUpdate)
        # mandar mensagem de update para os vizinhos
        time.sleep(period)



#--------------------Send/Recive--------------------
def recebePacote(udp, pacotesRecebidos): 
    while True:
        msg, ip = udp.recvfrom(1024)
        # print("Recebendo pacote")
        if(msg != ""):
            msg = bytes.decode(msg)
            mensagem = json.loads(msg)
            pacotesRecebidos.append(mensagem)


    #****MANDA MENSAGEM******
def enviaPacote(ip_destino, pacote):
    # Manda sua tabela para os vizinhos
    print('pacote', pacote)
    msg = json.dumps(pacote)
    mensagem = bytes(msg, 'utf-8')
    # print('mensagem', mensagem)
    destino = (ip_destino, port)
    conn_udp.sendto(mensagem, destino)


#--------------------Main--------------------

def pacoteUpdateRecebido(pacote, addr, vizinhos, roteadores):
    # print("teste")
    #limpa lista de roteadores e vizinhos pra ver se expirou
    excluiRotasInativas(vizinhos, roteadores, period)

    #pega as distancias e endereço dos pacote recebidos
    distances = pacote['distances']
    if len(distances) == 0:
        # print('distances', distances)
        for ip, peso in distances.items():
            ipRecebido.append([ip, peso])
        
    # TODO INSERIR NOVAS ROTAS DE ACORDO COM OS UPDATES RECEBIDOS

    #vai pegar o IP desses "distances"
    #  
    #adiciona os pesos que a gente tem com os ips que a gente recebeu
        for ip in ipRecebido:
            for v in vizinhos:
                novoPeso = ip[1]
                if(ip[0] == v[0]):
                    novoPeso = novoPeso + r[1]
            #adciona na lista de roteadores propria
            roteadores.append([ip[0], novoPeso, pacote["source"], time.time()])


def pacoteDadosRecebido(pacote, addr, vizinhos, roteadores):
    print(pacote['payload'])
    if(pacote['destination'] == addr):
        return
    procuraCaminho(pacote, pacote['destination'], roteadores, vizinhos)
    

def pacoteTraceRecebido(pacote, addr, vizinhos, roteadores):
    if(pacote['destination'] == addr):
        print("cria resposta")
        resposta = {'type': 'data', 'source': addr, 'destination': pacote['source'], 'payload': json.dumps(pacote)}
        procuraCaminho(resposta, resposta['destination'], roteadores, vizinhos)
    else:
        procuraCaminho(pacote, pacote['destination'], roteadores, vizinhos)


def trataPacotesRecebidos(roteadores, vizinhos, pacotesRecebidos, addr, period):
    while True:
        if(len(pacotesRecebidos) != 0):
            pacote = pacotesRecebidos[0]
            if(pacote['type'] == "data"):
                print("data")
                pacoteDadosRecebido(pacote, addr, vizinhos, roteadores)
            if(pacote['type'] == "trace"):
                #adiciona ip na lista hops
                pacote['hops'].append(addr)
                pacoteTraceRecebido(pacote, addr, vizinhos, roteadores)
                print("trace")
            if(pacote['type'] == "update"):
                pacoteUpdateRecebido(pacote, addr, vizinhos, roteadores)
                print("update")
                
            pacotesRecebidos.remove(pacotesRecebidos[0])

        #verifica se o tamanho dA LISTA PACOTE, for

def arquivo_startup(startup, vizinhos, roteadores):
    file = open(startup, "r")
    while True:
        comandos = file.readline()
        if(comandos!= ""):
            comandos = comandos.split
            if(comandos[0] == "add"):
                adicionaVizinho(vizinhos, comando, roteadores)
            if(comandos[0] == "del"):
                deletaRoteador(vizinhos, comando)
    return


#/router.py <ADDR> <PERIOD> [STARTUP]
# <PERIOD>: tempo para fazer o update

port = 55151
addr = sys.argv[1]
period = int(sys.argv[2])
# ESSE CAMPO É OPCIONAL
startup = sys.argv[3]

if(startup != ""):
    arquivo_startup(startup, vizinhos, roteadores)

#Listas
roteadores = []
vizinhos = []
pacotesRecebidos = []


#isso daqui vai bindar o roteador com o IP referente a ele,  criado pelo script lá
conn_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
origem = (addr, port)
conn_udp.bind(origem)

#thread1
threadRecieve = th.Thread(target = recebePacote, args = (conn_udp, pacotesRecebidos))
#recebePacote(pacote)

#thread2
threadInput = th.Thread(target = leInput, args = (vizinhos, roteadores, addr, conn_udp))
#leInput(vizinhos, roteadores, conn_udp),

#thread3
threadPacotes = th.Thread(target = trataPacotesRecebidos, args = (roteadores, vizinhos, pacotesRecebidos, addr, period))

#thread4
threadUpdates = th.Thread(target = update, args = (vizinhos, roteadores, addr, period))

threadRecieve.start()
threadInput.start()
threadPacotes.start()
threadUpdates.start()

