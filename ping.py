
import os
import smtplib
import subprocess
import datetime
import threading
import time
import configparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from configparser import ConfigParser


config = configparser.ConfigParser(allow_no_value=True)
config.read('/home/manoj/ping/config.ini')
value = config.get('time','check_interval')
value1 = config.get('email','send_interval')
print(config)
print(value)


check_interval =int(config['time']['check_interval'])
send_interval = int(config['email']['send_interval'])



def is_online(ip):
        try:
            # Use the ping command to check if the camera is up
            subprocess.check_output("ping -c 1 -w 2 " + ip, shell=True)
            print(ip, "is online")
            return True
        except:
            print(ip, "is offline")
            
            return False

def send_emails(sender_email,password,receiver_email_list,filecontent): # to send mails this function is used 
    server = smtplib.SMTP("mail.duranc.com", 587)
    server.starttls()
    server.login(sender_email, password)


    for receiver_email in receiver_email_list:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] =   receiver_email
        msg["Subject"] = "camera status" # subj
        msg.attach(MIMEText("  Please find the camera status of attachment")) #body
        part = MIMEBase("text","plain ;name=camera_status.txt")
        part.add_header(
            "Content-Decomposition",
            "attachment",
            filename= "camera_status.txt"

        )
        part.add_header("Content-Id", 't')
        part.set_payload((filecontent.encode('utf-8')))
        encoders.encode_base64(part)
        msg.attach(part)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("sending email",receiver_email)
    server.quit() 

    
def run_cameras_status_check(camera_ips_list):# to run_cameras status and write files 
    file_name   = datetime.datetime.now().strftime("%m-%d-%Y_%H.%M.%S.%f.txt")
    folder_path = "/home/manoj/ping/emails_to_send"
    file_path   =  os.path.join(folder_path,file_name)    
    current_day_time = datetime.datetime.now()
    current_day_time.strftime('%m-%d-%Y,%H.%M.%S.%f.txt')  

    down_cameras_ips_list = []
    for ip in camera_ips_list:
        if not is_online(ip):
            down_cameras_ips_list.append(ip)
        down_count = len(down_cameras_ips_list)
    total_cameras_count = len(camera_ips_list)

    if down_count > 0 :
        filecontent =  f'The total cameras are {total_cameras_count} in that {down_cameras_ips_list}are down'
    else:
        filecontent = f'all {total_cameras_count} are up'

    with open(file_path ,'w') as file:
        file.write(filecontent)

def read_all_files(sender_email,password,receiver_email_list):# it will read all files into list and send the mail  
    folder_path = "/home/manoj/ping/emails_to_send"
    list_of_files =os.listdir(folder_path)
    list_of_files.sort()
    list_of_contents =[]
    for file_name in list_of_files:
        file_path   =  os.path.join(folder_path,file_name)
        with open(file_path ,'r') as file:
            content= file.read()
            date = file_name.replace('.txt','')
            content=f'{date} {content}'
            list_of_contents.append(content)
    filecontent = '\n'.join(list_of_contents)
    send_emails(sender_email,password,receiver_email_list,filecontent)
    for file_name in list_of_files:
        file_path   =  os.path.join(folder_path,file_name)
        os.remove(file_path)
    
                                                  

def wait_for(seconds):  # it is used to run the function in seonds
    current_time_in_seconds = int(time.time())

    wait_to_next = seconds-current_time_in_seconds%60 # seconds unitl next email
    time.sleep(wait_to_next)



def thread1():
   
    while True :
        print('waiting for camera status check  in  seconds \n')
        wait_for(60)
        file_path = '/home/manoj/ping/cameras_list.txt'
        with open(file_path,'r') as file:
            ips_list = file.readlines()
            ips_list =[ip.replace('\n','') for ip in ips_list]
            for ip in ips_list:
                print(ip)
            run_cameras_status_check( camera_ips_list = ips_list)
def thread2():
    
     while True :
        print('waiting for email to check in for  seconds \n ')
        wait_for(180)
        receiver_path = '/home/manoj/ping/receiver_list.txt'
        with open(receiver_path, 'r') as file:
            content = file.readlines()
        read_all_files(sender_email = "manojphani.v@duranc.com",
        password = "Vitta06@manoj",
        receiver_email_list=['manojphani.v@duranc.com'])

t1 = threading.Thread(target =  thread1)
t2 = threading.Thread(target =  thread2)
t1.start()
t2.start()

t1.join()
t2.join()



        



