import PySimpleGUI as sg
from classes import *


# initializing GUI
layout = [
    [sg.VPush()],
    [sg.Text('Nightwave Plaza')],
    [sg.Button('Play'), sg.Button('Pause')],
    [sg.Slider((0, 100), 50, orientation='horizontal', key='vol', enable_events=True)],
    [sg.VPush()]
]
window = sg.Window('Nightwave Plaza', layout, element_justification='c', icon='icon.ico')

Player.set_volume(50)
Player.play()
RPC.start_thread()

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break

    match event:
    
        case 'Play':
            RPC.update()
            Player.play()

        case 'Pause':
            RPC.update()
            Player.pause()
        
        case 'vol':
            Player.set_volume(round(values['vol']))


RPC.stop()
Player.stop()
window.close()