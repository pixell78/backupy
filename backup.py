#!/usr/bin/env python3
# -*- coding: utf-8 -*-

############################ ABOUT ######################################
##                     BACKUP SCRIPT VERSION: 2.0                       #
###        THIS SCRIPT USING - VIDE DOCS OF LIBS                      ###
#                 SCHEDULE LIB                                          # 
#                 EMAIL LIB                                             #
#                 SMTPLIB                                               #
#                 SUBPROCESS LIB                                        #
# ######################### FEATURES ####################################
#          THIS SCRIPT USE RSYNC FOR SINC BKPS IN:                      #         
#                 LOCAL DISKS FOR MIRROR DATA                           #
#                 LOCAL NETWORK FOR LAN-NAS                             #
#                 OVER VPN IN REMOTE LAN                                #
#                 IN CLOUD                                              #
########################## LICENSE ######################################
###       GNU General Public License                                  ###
#########################################################################



import smtplib
import mimetypes
import email.mime.application
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import schedule
import subprocess
import time
import socket
import os
#######################################################################################################################################
def check_smtp_connection(host, port):
    try:
        socket.create_connection((host, port), timeout=10)
        return True
    except (socket.timeout, socket.gaierror, socket.error) as e:
        print(f"Erro ao conectar ao servidor SMTP: {e}")
        return False

def send_emaill(pathlog):
    smtp_host = 'smtp.hostinger.com.br'
    smtp_port = 587
    if not check_smtp_connection(smtp_host, smtp_port):
        print(f"Erro: Não foi possível conectar ao servidor SMTP {smtp_host} na porta {smtp_port}.")
        return False

    try:
        sender_email = 'conta@tcompany.net'
        sender_password = 'xxxxxxxxx'

        recipients = [
            {'name': 'user1', 'email': 'user1@company.com'},
            {'name': 'user2', 'email': 'user2@tcomapany.net.br'},
            {'name': 'Admin', 'email': 'admin@company.net'}
        ]

        # Lendo o conteúdo do log
        with open(pathlog, 'r') as file:
            log_content = file.read()

        for recipient in recipients:
            message = MIMEMultipart('alternative')
            message['From'] = sender_email
            message['To'] = recipient['email']
            message['Subject'] = 'Logs de Backup COMPANY'

            body_text = f"Olá {recipient['name']},\n\nSeguem os logs de backup PDC-COMPANY!\n\n"
            body_html = f"""
            <html>
                <body>
                    <p>Olá {recipient['name']},</p>
                    <p>Seguem os logs de backup PDC-COMPANY!</p>
                    <pre>{log_content}</pre>
                </body>
            </html>
            """

            part1 = MIMEText(body_text, 'plain')
            part2 = MIMEText(body_html, 'html')

            message.attach(part1)
            message.attach(part2)

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()
        print("\nEmails enviados com sucesso")
        return True
    except Exception as e:
        print(f"\nErro ao enviar email: {e}")
        return False


# Funções para criar os logs com diferentes sufixos
def geralog(suffix):

    date = time.strftime("%Y-%m-%d")
    logfile = f'{date}-backup-{suffix}.txt'
    pathlog = f'/var/log/backup/{logfile}'
    # Cria o diretório de logs caso não exista
    os.makedirs(os.path.dirname(logfile), exist_ok=True)
    return pathlog

# Limpa a lixeira antes do backup
def limpa_lixo():
    limpeza = 'rm -rf /dados/lixeira/*'
    subprocess.call(limpeza, shell=True)
    print("\nLixeira limpa com sucesso...")

# Gera um banner com a hora inicial do Backup
def inicio(horaInicio):
    inicio = '''
 ===========================================================================
||  ____          _____ _  ___    _ _____    _____   _____                   ||
|| |  _ \   /\   / ____| |/ / |  | |  __ \  |  __ \ / ____|                  ||
|| | |_) | /  \ | |    | ' /| |  | | |__) | | |__) | (___  _   _ _ __   ___  ||
|| |  _ < / /\ \| |    |  < | |  | |  ___/  |  _  / \___ \| | | | '_ \ / __| ||
|| | |_) / ____ \ |____| . \| |__| | |      | | \ \ ____) | |_| | | | | (__  ||
|| |____/_/    \_\_____|_|\_ \____/|_|      |_|  \_\_____/ \__, |_| |_|\___| ||
||                                                          __/ |            ||
||                                                         |___/             ||
||                    BACKUP DIFERENCIAL DO FILESERVER                       ||
  ===========================================================================
  ===========================================================================
                BACKUP DIFERENCIAL DO FILESERVER INICIADO ÀS %s

''' % horaInicio
    return inicio

# Termino e cálculos
def termino(diaInicio, horaInicio, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home, pathlog, backup, backup1):
    hoje = (time.strftime("%d-%m-%Y"))
    horaFinal = time.strftime('%H:%M:%S')
    backup = backup.replace('rsync -Cravzp', '')
    backup1 = backup1.replace('rsync -Cravzp', '')
    final = '''
  ==========================================================================================================
                            BACKUP DIFF ATUALIZADO
                HORA INICIAL:    %s  -  %s
                HORA FINAL  :    %s  -  %s
                LOG FILE    :    %s
                BAK FILE VPN:    %s
                BAK FILE VPN:    %s
                BAK FILE LAN:    %s
                BAK FILE LAN:    %s
                BAK FILE LOCAL : %s
                BAK FILE LOCAL : %s
  ==========================================================================================================
    ''' % (diaInicio, horaInicio, hoje, horaFinal, pathlog, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_local_dados, pathdestino_local_home)
    return final

# Gera os comandos de backup
def gerabackup():
    date = (time.strftime("%Y-%m-%d"))
    opts = 'Cravzp'
    exclude = '*.log, *.tmp, .recycle,'
    pathdestino_remoto_vpn_dados = '/media/xterm/29E7D9504B64265C/dados/'
    pathdestino_remoto_vpn_home = '/media/xterm/29E7D9504B64265C/home/'
    pathdestino_remoto_lan_dados = '/backup/dados/'
    pathdestino_remoto_lan_home = '/backup/home/'
    pathdestino_local_dados = '/backup/'
    pathdestino_local_home = '/backup/home/'
    pathorigem = '/dados/'
    pathorigem1 = '/home/'

    backup_nas = f'rsync -{opts} --exclude={{ {exclude} }} --progress {pathorigem} -e ssh root@10.215.86.1:{pathdestino_remoto_vpn_dados} '
    backup_nas1 = f'rsync -{opts} --exclude={{ {exclude} }} --progress {pathorigem1} -e ssh root@10.215.86.1:{pathdestino_remoto_vpn_home} '
    backup = f'rsync -{opts} --exclude={{ {exclude} }} --progress {pathorigem} -e ssh root@172.16.8.1:{pathdestino_remoto_lan_dados} '
    backup1 = f'rsync -{opts} --exclude={{ {exclude} }} --progress {pathorigem1} -e ssh root@172.16.8.1:{pathdestino_remoto_lan_home} '
    backup_local = f'rsync -{opts} --exclude={{ {exclude} }} --progress {pathorigem} {pathdestino_local_dados} --delete '
    backup1_local = f'rsync -{opts} --exclude={{ {exclude} }} --progress {pathorigem1} {pathdestino_local_home} --delete '
    return backup_nas, backup_nas1, backup_local, backup1_local, backup, backup1, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home


#CHECK VPN TUNEL LAN2LAN PACO
def check_lan():
##################################### CHECK TUNNEL #################################################
   ip_tunel = '172.16.8.1' #Ip LAN-NAS
   try:
     check = 'ping -c 5 %s' %ip_tunel 
     subprocess.call(check,shell=True)
     print("Conexão Ok, host responde...")
     return True
   except:
     print("Conexão FAIL...")
     return False
    # break
#####################################################################################################


# Abre conexão com a VPN
def vpn_conect():
    pathovpnfile = '/home/user/vpn.conf '
    conect = f'openvpn --config {pathovpnfile} &'
    ip_tunel = '172.16.8.1'
    try:
        subprocess.call(conect, shell=True)
        check = f'ping -c 5 {ip_tunel}'
        subprocess.call(check, shell=True)
        print("Conexão Ok, host responde...")
        return True
    except:
        print("Conexão FAIL...")
        return False

# Sincroniza backup no NAS local
def backup_nas_local():
### CHECA CONEXAO COM NAS LAN ###
    check_lan()
##################################### 
    horaInicio = time.strftime('%H:%M:%S')
    pathlog = geralog("local-diff")
    backup_nas, backup_nas1, backup_local, backup1_local, backup, backup1, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home = gerabackup()
    log = f' >> {pathlog}'
    start = inicio(horaInicio)
    
    with open(pathlog, 'w') as x:
        x.write(start)

    subprocess.call(backup + log, shell=True)
    subprocess.call(backup1 + log, shell=True)

    diaInicio = time.strftime("%d-%m-%Y")
    final = termino(diaInicio, horaInicio, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home, pathlog, backup, backup1)
    with open(pathlog, 'a') as r:
        r.write(final)

    send_emaill(pathlog)

# Funções específicas para diferentes tipos de backup
def backup_nas_vpn():
    vpn_conect()
    
    horaInicio = time.strftime('%H:%M:%S')
    pathlog = geralog("vpn-full")
    backup_nas, backup_nas1, backup_local, backup1_local, backup, backup1, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home = gerabackup()
    log = f' >> {pathlog}'
    start = inicio(horaInicio)
      
    with open(pathlog, 'w') as x:
        x.write(start)

    subprocess.call(backup_nas + log ,shell=True)
    subprocess.call(backup_nas1 + log ,shell=True)

    diaInicio = time.strftime("%d-%m-%Y")
    final = termino(diaInicio, horaInicio, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home, pathlog, backup_nas, backup_nas1)
    with open(pathlog, 'a') as r:
        r.write(final)

    send_emaill(pathlog)
    end_tunel = 'pkill openvpn'
    subprocess.call(end_tunel, shell=True)

def backup_hd_espelho():
    horaInicio = time.strftime('%H:%M:%S')
    pathlog = geralog("espelho-diff")
    backup_nas, backup_nas1, backup_local, backup1_local, backup, backup1, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home = gerabackup()
    log = f' >> {pathlog}'
    start = inicio(horaInicio)
    
    with open(pathlog, 'w') as x:
        x.write(start)

    subprocess.call(backup_local + log, shell=True)
    subprocess.call(backup1_local + log, shell=True)

    diaInicio = time.strftime("%d-%m-%Y")
    final = termino(diaInicio, horaInicio, pathdestino_remoto_vpn_dados, pathdestino_remoto_vpn_home, pathdestino_remoto_lan_dados, pathdestino_remoto_lan_home, pathdestino_local_dados, pathdestino_local_home, pathlog, backup_local, backup1_local)
    with open(pathlog, 'a') as r:
        r.write(final)

    send_emaill(pathlog)

def define_hora_backup():
    print("\nRodando tarefa de backup diário...")
    #backup_nas_vpn()
    limpa_lixo()
    backup_nas_local()

#####################################################PROGRAMA PRINCIPAL#############################################################################

# Agendar a execução do backup
schedule.every().day.at("20:00").do(define_hora_backup)

# Loop para manter o agendador rodando
while True:
    schedule.run_pending()
    time.sleep(1)
