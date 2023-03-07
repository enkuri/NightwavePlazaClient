import requests
import vlc
import time
from pypresence import Presence
from threading import Thread


class API:
    def __init__(self):
        self.url = 'https://api.plaza.one/'
        self.last_request = None
        self.last_data = {}
    
    def request(self, endpoint: str, params: dict = {}) -> dict | int:
        r = requests.request('GET', self.url + endpoint, params=params)
        if r.status_code != 200:
            return r.status_code
        else:
            return r.json()


class Player:
    instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
    player = instance.media_player_new()
    player.set_media(instance.media_new('http://radio.plaza.one/mp3'))

    @classmethod
    def play(cls) -> None:
        """Resume/start playing"""
        cls.player.play()
    
    @classmethod
    def pause(cls) -> None:
        """Pause player"""
        cls.player.pause()
    
    @classmethod
    def is_playing(cls) -> bool:
        """Check if anything is being played"""
        return bool(cls.player.is_playing())

    @classmethod
    def set_volume(cls, vol: int) -> None:
        """Set player's volume (0-100)"""
        cls.player.audio_set_volume(vol)
    
    @classmethod
    def stop(cls) -> None:
        """Stop player completely"""
        cls.player.stop()


class RPC:
    client = API()
    paused = None
    running = True
    start = time.time()

    rpc = Presence("981760124479733760")
    rpc.connect()

    @classmethod
    def update(cls) -> None:
        """Update presence"""
        if Player.is_playing():
            if cls.paused:
                cls.paused = None

            status = cls.client.request('status')

            cls.rpc.update(
                start=cls.start,
                details=status['song']['title'],
                state='{} - {}'.format(status['song']['artist'], status['song']['album']),
                large_image=status['song']['artwork_sm_src'],
                large_text='{} listeners'.format(status['listeners']),
                small_image='https://i.postimg.cc/vm4PsxNL/download-2.png',
                small_text='rpc by enkuri.justlian.com'
            )
        else:
            if not cls.paused:
                cls.paused = time.time()
            cls.rpc.update(
                start=cls.paused,
                details='Paused',
                large_image='https://i.postimg.cc/1RK7QSzt/avatar.png',
                large_text='https://plaza.one',
                small_image='https://i.postimg.cc/vm4PsxNL/download-2.png',
                small_text='rpc by enkuri.justlian.com'
            )
    
    @classmethod
    def start_thread(cls) -> None:
        """Create and start updating thread"""
        def thread(cls):
            while cls.running:
                cls.update()
                time.sleep(10)
        
        Thread(target=thread, args=(cls,)).start()

    @classmethod
    def stop(cls) -> None:
        """Clear presence and stop updating thread"""
        cls.running = False
        cls.rpc.clear()


__all__ = ["API", "Player", "RPC"]