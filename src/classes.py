import requests
import vlc
import time
from pypresence import Presence, DiscordNotFound
from threading import Thread


class API:
    url = 'https://api.plaza.one/'
    last_data = {}
    downloaded = False
    process = None
    
    @classmethod
    def request(cls, endpoint: str, params: dict = {}) -> dict | int:
        r = requests.request('GET', cls.url + endpoint, params=params)
        if r.status_code != 200:
            return r.status_code
        else:
            data = r.json()
            cls.last_data[endpoint] = data
            return data
    
    @classmethod
    def from_storage(cls, endpoint: str) -> dict | int:
        if endpoint in cls.last_data:
            return cls.last_data.get(endpoint)
        else:
            return cls.request(endpoint)
    
    @classmethod
    def downloading(cls, url, dest):
        # do not call this function. Use API.download
        data = requests.get(url).content
        with open(dest, 'wb') as h:
            h.write(data)

    @classmethod
    def download(cls, url: str, dest: str):
        cls.process = Thread(target=cls.downloading, args=(url, dest))
        cls.process.start()

    @classmethod
    def is_downloaded(cls):
        if cls.process is not None and not cls.process.is_alive():
            cls.process = None
            return True
        return False


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
    client = API
    paused = None
    running = True
    start = time.time()

    rpc = None

    @classmethod
    def update(cls) -> None:
        """Update presence"""
        if not cls.connect():
            return

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
        def thread():
            while cls.running:
                cls.update()
                time.sleep(10)
        
        if cls.connect():
            Thread(target=thread).start()
    
    @classmethod
    def connect(cls) -> bool:
        """
        Tries to connect Discord RPC
        If RPC is connected or connecting was establish,
        returns True. Othervise - False
        """
        if cls.rpc:
            return True
        try:
            cls.rpc = Presence("981760124479733760")
            cls.rpc.connect()
            return True
        except (DiscordNotFound, RuntimeError) as e:
            print('Discord not found ({})'.format(e))
            return False

    @classmethod
    def stop(cls) -> None:
        """Clear presence and stop updating thread"""
        cls.running = False
        if cls.rpc:
            cls.rpc.clear()


__all__ = ["API", "Player", "RPC"]