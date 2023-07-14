from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import zipfile
import threading
import warnings
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
import PySimpleGUI as sg
from pytube import YouTube
from pygame import mixer
import subprocess

os.system('cls')
os.system(f"title Youtube to Speech")
warnings.simplefilter('ignore', category=DeprecationWarning)
LOGGER.setLevel(logging.WARNING)


def get_chromedriver():
    path = os.path.dirname(os.path.abspath(__file__))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option(
        'excludeSwitches', ['enable-logging'])
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(
        os.path.join(path, 'chromedriver'),
        chrome_options=chrome_options)
    return driver


def search(text):
    try:
        os.remove('output.wav')
    except:
        pass
    driver = get_chromedriver()
    driver.get("https://www.youtube.com/results?search_query="+text)
    videos = driver.find_elements(By.XPATH, '//*[@class="yt-simple-endpoint style-scope ytd-video-renderer"]')
    video_names = []
    urls = []
    for x in range(5):
        name_info = videos[x].get_attribute("aria-label").split("by")
        name = name_info[0]
        length = name_info[1].split(" ")[4] + ":" + name_info[1].split(" ")[6]
        full = name + " | " + length
        video_names.append(full)
        urls.append(videos[x].get_attribute("href"))
    return video_names, urls


def download(url):
    try:
        os.remove('output.wav')
    except:
        pass
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path="./")
    new_file = "output" + '.mp3'
    os.rename(out_file, new_file)
    subprocess.call(['ffmpeg', '-i', 'output.mp3',
                     'output.wav'])
    os.remove('output.mp3')


def play_audio():
    mixer.init(devicename='CABLE Input (VB-Audio Virtual Cable)')
    mixer.music.load("output.wav")
    mixer.music.play()
    while mixer.music.get_busy():
        pass


options = ['Option 1', 'Option 2', 'Option 3']

layout = [
    [sg.Text('Video Name:')],
    [sg.InputText(key='-OPTIONS-')],
    [sg.Text('Select an option:')],
    [sg.OptionMenu(values=["Waiting for search"], default_value=["Waiting for search"], key='-OPTIONMENU-')],
    [sg.Button('Search'), sg.Button('Speak'), sg.Button('Pause', key='pause'), sg.Button('Exit')],
    [sg.Slider(default_value=0, orientation="horizontal", key='timer', range=(1,400), disable_number_display=True)]
]

window = sg.Window('Youtube to Speech', layout)
searched = False
stopped = False
playing = False
urls = []
while True:
    event, values = window.read()
    if playing:
        sound = mixer.Sound("output.wav")
        sound_length = sound.get_length() * 1000
        print(sound_length)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Search':
        videos, urls = search(values['-OPTIONS-'])
        options = videos
        window['-OPTIONMENU-'].update(values=options, value=options[0])
        searched = True
    elif event == 'Speak':
        if not searched:
            sg.popup("You didn't search anything!", title='Error')
        else:
            selected_index = options.index(values['-OPTIONMENU-'])
            download(urls[selected_index])
            threading.Thread(target=play_audio).start()
            playing = True
    elif event == 'pause':
        if not playing:
            sg.popup("No audio loaded!", title='Error')
        else:
            if stopped:
                stopped = False
                mixer.music.unpause()
                button = window['pause']
                button.update(text='Pause')
            elif not stopped:
                stopped = True
                mixer.music.pause()
                button = window['pause']
                button.update(text='Resume')

window.close()
