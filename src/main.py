import PySimpleGUI as sg
from PIL import Image, ImageTk
import tempfile
from classes import *


# initializing GUI
col1 = [[sg.Image('src/logo.png', key='img')]]
col2 = [
    [sg.Text('Nightwave Plaza')],
    [sg.Button('Play'), sg.Button('Pause')],
    [sg.Slider((0, 100), 50, orientation='horizontal', key='vol', enable_events=True)]
]
layout = [
    [
        sg.Column(col1, vertical_alignment='center', element_justification='center'),
        sg.VSeparator(),
        sg.Column(col2, vertical_alignment='center', element_justification='center')
    ]
]
window = sg.Window('Nightwave Plaza', layout, element_justification='c', icon='icon.ico')

Player.set_volume(50)
Player.play()
RPC.start_thread()
last_song_id = 0

img = tempfile.gettempdir() + '/nightwave_plaza.jpg'
last_song_id = 0

import time
while True:
    event, values = window.read(timeout=300)

    d = API.from_storage('status')
    if last_song_id != d['song']['id']:
        last_song_id = d['song']['id']
        API.download(d['song']['artwork_sm_src'], img)
    
    if API.is_downloaded():
        window['img'].update(
            data=ImageTk.PhotoImage(Image.open(img).resize((192, 192)))
        )

    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break

    match event:
    
        case 'Play':
            Player.play()
            RPC.update()

        case 'Pause':
            Player.pause()
            RPC.update()
        
        case 'vol':
            Player.set_volume(round(values['vol']))


RPC.stop()
Player.stop()
window.close()