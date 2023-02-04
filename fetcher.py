# by bunny

import subprocess
import requests
import re
import os
import m3u8
import argparse
from shutil import move
from mutagen.mp4 import MP4
try:
    from prettytable.colortable import ColorTable, Theme
    _color = True
except ImportError:
    _color = False
    from prettytable import PrettyTable
from sanitize_filename import sanitize as sanitize_filename

TOKEN = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ.eyJpc3MiOiJBTVBXZWJQbGF5IiwiaWF0IjoxNjc1MjAxMDY0LCJleHAiOjE2ODI0NTg2NjQsInJvb3RfaHR0cHNfb3JpZ2luIjpbImFwcGxlLmNvbSJdfQ.X6_jxCKuAndOhOL-hWPMPqwMiNJ6dWCau-FTP8AuXeHYCJLPueZDNSus_cdvqkKWPKyUD5FeTJwxwfvxezY0ow'
Regx = re.compile(
    r"apple\.com\/(\w\w)\/(playlist|album|artist)\/.+\/(\d+|pl\..+)")

title = """
             /$$$$$$$$          /$$               /$$                          
            | $$_____/         | $$              | $$                          
            | $$     /$$$$$$  /$$$$$$    /$$$$$$$| $$$$$$$   /$$$$$$   /$$$$$$ 
            | $$$$$ /$$__  $$|_  $$_/   /$$_____/| $$__  $$ /$$__  $$ /$$__  $$
            | $$__/| $$$$$$$$  | $$    | $$      | $$  \ $$| $$$$$$$$| $$  \__/
            | $$   | $$_____/  | $$ /$$| $$      | $$  | $$| $$_____/| $$      
            | $$   |  $$$$$$$  |  $$$$/|  $$$$$$$| $$  | $$|  $$$$$$$| $$      
            |__/    \_______/   \___/   \_______/|__/  |__/ \_______/|__/      
                    Apple-Music animated cover artwork downloader                      
                                                                -- by bunny  
    """


class Fetch:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            'authorization': f"Bearer {TOKEN}",
            'origin': 'https://music.apple.com'
        })
        print("Checking if the static token is still alive...")
        self.check_token()
        ANIMATED_PATH = os.path.join(os.getcwd(), "Animated artworks")
        if not os.path.exists(ANIMATED_PATH):
            os.makedirs(ANIMATED_PATH)

    def album(self, id_, country, artwork_type, rep, aud):
        album_json = self.get_json(id_, country, 'album')
        m3u8_ = self.get_m3u8(album_json, artwork_type)
        meta = album_json['data'][0]['attributes']

        try:
            genre = meta["genreNames"][0]
        except (KeyError, TypeError):
            genre = None

        album = meta["name"]
        artist = meta["artistName"]
        release_date = meta["releaseDate"]

        fname = sanitize_filename(
            f"{artist} - {album} ({release_date[:4]}).mp4")
        video_path = os.path.join(os.getcwd(), "Animated artworks", fname)

        self.processVideo(m3u8_, rep)

        if aud:
            self.processAudio(album_json, video_path)
            os.remove("fixed.mp4")
        else:
            move("fixed.mp4", video_path)

        self.tagger(
            video_path=video_path,
            album=meta["name"],
            artist=meta["artistName"],
            album_url=meta["url"],
            tracks=meta["trackCount"],
            release_date=meta["releaseDate"],
            upc=meta['upc'],
            rating=meta.get("contentRating"),
            copyright=meta.get("copyright"),
            record_label=meta.get('recordLabel'),
            genre=genre,
            editorial=meta.get('editorialNotes', {}).get('standard')
        )

        os.remove("video.mp4")

    def playlist(self, id_, country, artwork_type, rep):
        playlist_json = self.get_json(id_, country, 'playlist')
        meta = playlist_json['data'][0]['attributes']
        m3u8_ = self.get_m3u8(playlist_json, artwork_type)
        fname = sanitize_filename(
            f"{meta['name']} ({meta['lastModifiedDate'][:4]}).mp4")
        video_path = os.path.join(os.getcwd(), "Animated artworks", fname)

        self.processVideo(m3u8_, rep)
        move("fixed.mp4", video_path)
        self.tagger(
            video_path=video_path,
            album=meta["name"],
            artist=meta["curatorName"],
            album_url=meta["url"],
            release_date=meta["lastModifiedDate"],
            editorial=meta.get('editorialNotes', {}).get('standard')
        )
        os.remove("video.mp4")


    def artist(self, id_, country, artwork_type):
        artist_json = self.get_json(id_, country, 'artist')
        meta = artist_json['data'][0]['attributes']
        m3u8_ = self.get_m3u8(artist_json, artwork_type, 'artist')
        fname = sanitize_filename(f"{meta['name']}.mp4")
        video_path = os.path.join(os.getcwd(), "Animated artworks", fname)
        self.processVideo(m3u8_, 0)
        move("fixed.mp4", video_path)
        os.remove("video.mp4")

    def get_json(self, id_, country, kind):

        params = {
            'extend': 'editorialVideo'
        }

        if kind == 'album':
            response = self.session.get(
                f'https://amp-api.music.apple.com/v1/catalog/{country}/albums/{id_}', params=params)
        elif kind == 'playlist':
            response = self.session.get(
                f'https://amp-api.music.apple.com/v1/catalog/{country}/playlists/{id_}', params=params)
        elif kind == 'artist':
            response = self.session.get(
                f'https://amp-api.music.apple.com/v1/catalog/{country}/artists/{id_}', params=params)
        return response.json()

    def get_m3u8(self, json, atype, kind='album'):
        BASE = json['data'][0]['attributes']['editorialVideo']

        if atype == 'tall':
            if kind == 'artist':
                try:
                    return BASE['motionArtistFullscreen16x9']['video']
                except KeyError:
                    return BASE['motionArtistWide16x9']['video']
            return BASE['motionDetailTall']['video']

        elif atype == 'square':
            if kind == 'artist':
                return BASE['motionArtistSquare1x1']['video']
            try:
                return BASE['motionDetailSquare']['video']
            except KeyError:
                return BASE['motionSquareVideo1x1']['video']

    def processVideo(self, m3u8_, rep):
        playlist = m3u8.load(m3u8_)
        # print(playlist.data)
        self.print_table(playlist.data)
        playlist_id = int(input("Enter the ID: "))
        m3u8_ = playlist.data["playlists"][playlist_id]['uri']
        print("\nDownloading the video...")
        subprocess.Popen(['ffmpeg', '-loglevel', 'quiet',
                         '-y', '-i', m3u8_, '-c', 'copy', 'video.mp4']).wait()
        print("Video downloaded.")

        # making the new looped video
        subprocess.Popen(['ffmpeg', '-loglevel', 'quiet',
                         '-y', '-stream_loop', str(rep), '-i',
                          'video.mp4', '-c', 'copy', 'fixed.mp4']).wait()

    def listall(self, json):
        table = ColorTable(theme=Theme(default_color='90')
                           ) if _color else PrettyTable()
        table.field_names = ["Track No.", "Name"]
        table.align["Name"] = "l"
        totaltracks = int(json['data'][0]['attributes']['trackCount'])
        for i in range(totaltracks):
            if json['data'][0]['relationships']['tracks']['data'][i]['type'] == "songs":
                song = json['data'][0]['relationships']['tracks']['data'][i]['attributes']['name']
                table.add_row([i+1, song])
        print(table)

    def processAudio(self, album_json, video_path):
        print("\nAudio tracks:")
        self.listall(album_json)
        index = int(input("\nSelect the audio track number : "))
        index = index - 1

        m4a = album_json['data'][0]['relationships']['tracks']['data'][index]['attributes']['previews'][0]['url']

        # downloading the selected m4a track using requests
        print("\nDownloading the audio...")
        r = self.session.get(m4a, allow_redirects=True)
        open('audio.m4a', 'wb').write(r.content)

        print("Audio downloaded.")

        # multiplexing
        print("\nMultiplexing...")
        # multiplex audio and video using ffmpeg-python
        subprocess.Popen(['ffmpeg', '-loglevel', 'quiet', '-y', '-i', 'fixed.mp4',
                         '-i', 'audio.m4a', '-c', 'copy', "-shortest", video_path]).wait()
        print("Done.")
        os.remove("audio.m4a")

    def print_table(self, json):
        tmp = Theme(default_color='90') if _color else None
        table = ColorTable(theme=tmp) if _color else PrettyTable()
        table.field_names = ["ID", "Resolution", "Bitrate", "Codec", "FPS"]
        for i in range(len(json['playlists'])):
            if i == len(json['playlists'])-1:
                pass
            elif json['playlists'][i]['stream_info']['resolution'] == json['playlists'][i+1]['stream_info']['resolution']:
                continue
            table.add_row([i, json['playlists'][i]['stream_info']['resolution'], str(round((int(json['playlists'][i]['stream_info']['bandwidth']) /
                                                                                            1000000), 2)) + " Mb/s", json['playlists'][i]['stream_info']['codecs'][0:4], json['playlists'][i]['stream_info']['frame_rate']])
        print(table)

    def tagger(self,
               video_path,
               album=None,
               artist=None,
               album_url=None,
               tracks=None,
               release_date=None,
               upc=None,
               rating=None,
               copyright=None,
               record_label=None,
               genre=None,
               editorial=None,
               ):

        # tagging
        print("\nTagging metadata...")
        video = MP4(video_path)

        if album:
            video["\xa9alb"] = album
        if artist:
            video["aART"] = artist
        if album_url:
            video["----:TXXX:URL"] = bytes(album_url, 'UTF-8')
        if tracks:
            video["----:TXXX:Total tracks"] = bytes(str(tracks), 'UTF-8')
        if release_date:
            video["----:TXXX:Release date"] = bytes(release_date, 'UTF-8')
        if upc:
            video["----:TXXX:UPC"] = bytes(upc, 'UTF-8')
        if rating:
            video["----:TXXX:Content Advisory"] = bytes(
                'Explicit' if rating != '' else 'Clean', 'UTF-8')
        if copyright:
            video["cprt"] = copyright
        if record_label:
            video["----:TXXX:Record label"] = bytes(record_label, 'UTF-8')
        if genre:
            video["\xa9gen"] = genre
        if editorial:
            video["----:TXXX:Editorial notes"] = bytes(
                self.remove_html_tags(editorial), 'UTF-8')
        video.pop("©too")
        video.save()
        print("Done.")
        print(video_path)

    def remove_html_tags(self, text):
        """Remove html tags from a string"""
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    def check_token(self) -> None:

        response = self.session.get(
            'https://amp-api.music.apple.com/v1/catalog/in/albums/1551901062')

        if response.status_code != 200:
            print("Token expired!\nUpdating the token...")
            response = self.session.get(
                "https://music.apple.com/assets/index.919fe17f.js")
            result = re.search("\"(eyJ.+?)\"", response.text).group(1)
            self.session.headers.update({'authorization': f"Bearer {result}"})
            print("Token updated!")
        else:
            print("Token is valid!")


if __name__ == "__main__":
    print(title)

    parser = argparse.ArgumentParser(
        description="Downloads animated cover artwork from Apple music.")
    parser.add_argument(
        '-T', '--type', help="[tall,square] (tall/rectangle by default)", default='tall', type=str)
    parser.add_argument(
        '-L', '--loops', help="[int] Number of times you want to loop the artwork (No loops by default)", default=0, type=str)
    parser.add_argument(
        '-A', '--audio', help="Pass this flag if you also need the audio", action="store_true")
    parser.add_argument(
        'url', help="Album/Playlist/Artist URL")

    args = parser.parse_args()

    url = args.url
    artwork_type = args.type
    rep = args.loops
    aud = args.audio

    # extracting out the country and album ID
    result = Regx.search(url)
    if result is None:
        raise Exception("Invalid URL!")
    country = result.group(1)
    kind = result.group(2)
    id_ = result.group(3)

    fetch = Fetch()

    if kind == "album":
        fetch.album(id_, country, artwork_type, rep, aud)
    elif kind == "playlist":
        fetch.playlist(id_, country, artwork_type, rep)
    else:
        fetch.artist(id_, country, artwork_type)
