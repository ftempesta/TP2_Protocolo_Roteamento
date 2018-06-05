# -*- coding: utf-8 -*- 
# NÃO SEI USAR SOCKET UDP
# é quase a mesma coisa que tcp, tipo identico.
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#initalising socket and UDP connection
#   Message = str(json_string)
#   print 'Message sent:= ', Message
#   sock.sendto(Message,(UDP_IP, PORT))

#----------------DISCUSSÕES------------------------

# pra que serve esse script lo-addresses.sh???
# ip addr add 127.0.1.1/32 dev lo <--- ele faz isso daqui aparentemente
# ele só cria na sua rede local os endereços que vao ser utilziados pelos roteadores que a gente vai criar
# ex: Roteador A vai ficar no ip 127... /1
#   roteador B vai ficar no ip 127.../ 2
  
# ENTÃO, MAS TIPO, A GENTE QUE PRECISA LIDAR COM ESSE SCRIPT OU ELE VAI CRIAR ESSES IPS? E O NOSSO CÓDIGO JÁ PODE PARTIR DIRETO PARA A PRÓXIMA ETAPA????  
# eu acho que ele cria virtualmente, mas o negocio que a gente tem que atribuir o nosso router.py a cada endereço que ele cria
# NOSSA, COMO QUE FAZ ISSO?
# acho que cada terminal vai ser um ip diferente por causa do script, aí só rodar o programa nesse terminal???nsei
# TÁ, MAS DEPOIS A GENTE PENSA MAIS SOBRE ISSO. POR ENQUANTO PODEMOS ADMITIR QUE OS ENDEREÇOS JÁ ESTÃO CRIADOS E LIDAR COM ISSO. SE FOR O CASO A GENTE MUDA DEPOIS
# ok
  
  
# pelo que entendi primeiro temos que adicionar os endereços à uma determinada interface loopback. Que, pelo que entendi seria adicionar os endereços que vamos usar
# E depois fazer o link entre eles determinando o custo (ou serja, a tabela). FAZ SENTIDO ISSO?


# AQUI, ANTES DA GENTE COMEÇAR A ESCREVER CÓDIGO, VAMOS ESCREVER EM PORTUGUÊS TUDO QUE O ALGORITMO PRECISA TER E EM QUE ORDEM E SÓ DEPOIS A GENTE PASSA PRA PYTHON?
# ok

# VAI FICAR MAIS FÁCIL MODELAR TODO O PROBLEMA SEM SE PERDER E NEM ESQUER DE NENHUM DETALHE

# EU JÁ COMECEI AQUI EM BAIXO. VAI DANDO UMA OLHADA


#------------------FIM DISCUSSÕES-----------------


#--------------------INICIO----------------------
import sys
import socket
import json
import time

#-----------comando add <ip> <weight>----------------
def adicionaRoteador(vizinhos, comando, roteadores):
    ip = comando[1]
    peso = comando[2]
  
  #Um add pode ser de um roteador já existente, a gente tem que verificar pra mudar o peso dele
  #for i in range(len(roteadores)):
  #  if(roteadores[i][0] == ip)
  
  #se nao for um roteador existente na lista
    roteadores.append([ip, peso])

  
#--------------comando del <ip>--------------------
def deletaRoteador(vizinhos, comando):
    ip = comando[1]
#     for i in range(len(vizinhos)):
#         if(vizinhos[i][0] == ip)
#             vizinhos.delete(vizinhos[i])



#---------------mensagem de dados-------------------
#payload = mensagem trace
def criaMensagemData(ipDestino, ipOrigem, payload):
    print(json.dumps({'type': 'data', 'source': ipOrigem, 'destination': ipDestino, 'payload': payload}, indent=2))

#--------------comando trace <ip>------------------
def ratreaRoteador(vizinhos, comando, ipOrigem):
    ipDestino = comando[1]
    hops = [ipOrigem]
    
    #cria JSON de trace
    msgTrace = json.dumps({'type': 'trace', 'source': ipOrigem, 'destination': ipDestino, 'hops': hops}, indent=2)
    print(msgTrace)
    #cria payload para usar em msgData
    payload = json.dumps({'type': 'trace', 'source': ipOrigem, 'destination': ipDestino, 'hops': hops})
    criaMensagemData(ipDestino, ipOrigem, payload)

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

#isso daqui vai bindar o roteador com o IP referente a ele,  criado pelo script lá
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((addr, port))


while True:
    comando = input()
    comando = comando.split(' ')

    if (comando[0] == "add"):
        adicionaRoteador(vizinhos, comando, roteadores)
        print("add")
        continue
    
    if (comando[0] == "del"):
        deletaRoteador(vizinhos, comando)
        print("del")
        continue
  
    if(comando[0] == "trace"):
        #criar funcao pra calcular trace
        ratreaRoteador(vizinhos, comando, addr)
        print("trace")
        continue
    
    #só termina com Ctrl + c 
    else: 
        sys.exit() 
    
    
  #deve mandar um update toda hora, nao sei se eu entendi
  #A CADA PI(constante durante a execução do roteador - PERIOD) SEGUNDOS ELE DEVE MANDAR MSG DE UPDATE. 
  #ai depois tem que ter um delay e volta a receber comandos
    # time.sleep(period)#delay







# -------------------- PRIMEIRA COISA DE CODIGO A SE FAZER: criar a tabela ADD para todos os roteadores, com o nome de destino e o peso--------------------

#   CRIAR TOPOLOGIA
#   1. ADICIONAR ENLACE
#           ---add <ip> <peso>---
#           ---exemplo: para o endereço 127.0.1.5:---
#           ---add 127.0.1.1 10---
#           ***adicionar um enlace entre o roteador corrente e o roteador passado por parametro***

#           Para cada um dos endereços
#           Enquanto ainda tiver endereços para serem lidos
#                   Le endereço pelo comando add, endereço e peso
#                   cria uma tabela de roteamento para esse endereço


# -------------------nao sei aonde que a gente vai usar isso, vou ver n os exemplos ---------------------------------
#   2. DELETAR ENLACE
#           ***Comando DEL <ip>: remove o enlace entre o roteador corrente e o roteador passado por parametro***
#       

#---------------------Depois de todo mundo já ter a tabela, criar um JSON object, ou seja, uma struct com os seguintes campos:
#source—Especifica o endereço IP do programa que originou a mensagem.
#destination—Especifica o endereço IP do programa destinatário da mensagem.
#type—Especifica o tipo da mensagem, sua semântica, e quaisquer campos adicionais. Nestetrabalho implementaremos três tipos de mensagem:data(seção 3.1),update(seção 4.1)etrace(seção 5)
# EX DE COMO DEVE FICAR::
#{
#  "type": "data",
#  "source": "127.0.1.2",
#  "destination: "127.0.1.1",
#} 


#---------------------- DEPOIS DE CRIAR O OBJECT JSON, TEMOS QUE PREOCUPAR EM FAZER OS 3 TIPOS DE MENSAGENS---------------------------------------------




#--------------------Mensagem: DATA -------------------------------
#com um campo "payload" a mais no OBJECT, com uma mensagem qualquer que vai ser transmitida do source para o destination

#--------------------Mensagem: UPDATE --------------------------------------
#esse daqui manda um "distances" e vai atualizar o peso, mas aparentemente a gente tem que cuidar de "Atualizações periodicas" e "Split Horizon"

#--------------------Mensagem: TRACE --------------------------------------
#medir a rota utilizada entre dois roteadores 
#campos:
#           type
#           source
#           destination
#           "hops": armazena lista de roteadores por onde a msg de trace já passou

#quando receber essa mensagem de trace, roteador deve add seu ip ao final da lista no campo "hop" da mensagem. 
#se roteador FOR o destino do trace
#       enviar msg "data" para roteador que originou o "trace" - "payload" = string com json correspondente à msg de trace 
#senão
#       encaminhar a msg por um dos caminhos mair curtos que conhece até o destino
#       **MSG DE TRACE ESTÃO SUJEITAS A BALANCEAMENTO DE CARGA (DIVIDIR CARGA EM CASO DE EMPATE DE CAMINHO MAIS CURTO)
#
# --trace <ip>: roteador cria uma msg de rastreamento para o roteador com endereço <ip>

#******CALCULAR A ROTA MAIS CURTA*********
# o roteador deve armazenar informações sobre TODAS as rotas conhecidas em uma tabela de roteamento. 
# calcular rota mais curta - algoritmo de Dijkstra
# Emcaminhar dados através da rota mais curta   






