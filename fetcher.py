# by bunny

import colorama
import requests
import re
import os
import m3u8
import sys
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
import ffmpeg
from colorama import Fore, Back
colorama.init(autoreset=True)

TOKEN = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ.eyJpc3MiOiJBTVBXZWJQbGF5IiwiaWF0IjoxNjQ0OTQ5MzI0LCJleHAiOjE2NjA1MDEzMjR9.3RUn173ddFRpam0ksOFS-vJFR-wCtJHzcSdGr7exxFQScWxzQxHGht4wyt6iJQqNcEOR4BRmv6O4-2B4jzrGsQ'
Regx = re.compile(r"apple\.com\/(\w\w)\/(playlist|album)\/.+\/(\d+|pl\..+)")

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


def get_auth_token():
    response = requests.get("https://k0ybdlmho9.execute-api.ap-northeast-1.amazonaws.com/prod/tokens/applemusic/generate")
    return response.json()['token']


def get_json(country, _id, token, kind):

    headers = {
        'origin': 'https://music.apple.com',
        'authorization': f'Bearer {token}'
    }

    album_params = (
        ('filter[equivalents]', f'{_id}'),
        ('extend', 'editorialVideo'),
    )

    playlist_params = {
        'extend': 'editorialVideo'
    }

    if kind == 'album':
        response = requests.get(
            f'https://amp-api.music.apple.com/v1/catalog/{country}/albums', headers=headers, params=album_params)
    elif kind == 'playlist':
        response = requests.get(
            f'https://amp-api.music.apple.com/v1/catalog/{country}/playlists/{_id}', headers=headers, params=playlist_params)
    return response.json()



def get_m3u8(json, atype):
    BASE = json['data'][0]['attributes']['editorialVideo']
    
    if atype == 'tall':
        return BASE['motionDetailTall']['video']
    elif atype == 'square':
        try:
            return BASE['motionDetailSquare']['video']
        except KeyError:
            return BASE['motionSquareVideo1x1']['video']



def listall(json):
    table = ColorTable(theme=Theme(default_color='90')) if _color else PrettyTable()
    table.field_names = ["Track No.", "Name"]
    table.align["Name"] = "l"
    totaltracks = int(json['data'][0]['attributes']['trackCount'])
    for i in range(totaltracks):
        if json['data'][0]['relationships']['tracks']['data'][i]['type'] == "songs":
            song = json['data'][0]['relationships']['tracks']['data'][i]['attributes']['name']
            table.add_row([i+1, song])
    print(table)


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def check_token(tkn=None):
    if tkn is None:
        tkn = TOKEN

    headers = {
        'authorization': f'Bearer {tkn}'
    }

    params = (
        ('filter[equivalents]', '1551901062'),
        ('extend', 'editorialVideo'),
    )

    response = requests.get(
        'https://amp-api.music.apple.com/v1/catalog/in/albums', headers=headers, params=params)

    if response.status_code != 200:
        return None
    return tkn


def print_table(json):
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


if __name__ == "__main__":

    # clean screen
    os.system('cls' if os.name == 'nt' else 'clear')

    print(Fore.GREEN + title)

    parser = argparse.ArgumentParser(
        description="Downloads animated cover artwork from Apple music.")
    parser.add_argument(
        '-T', '--type', help="[tall,square] (square by default)", default='square', type=str)
    parser.add_argument(
        '-L', '--loops', help="[int] Number of times you want to loop the artwork (No loops by default)", default=0, type=int)
    parser.add_argument(
        '-A', '--audio', help="Pass this flag if you also need the audio", action="store_true")
    parser.add_argument(
        'url', help="Album URL")

    args = parser.parse_args()

    print("Checking if the static token is still alive...")
    # checking if the token is still alive
    token = check_token(TOKEN)
    if token is None:
        print(Back.RED + "Regenerating a new token.")
        token = get_auth_token()
    print(Back.GREEN + "Token is valid!")

    url = args.url
    artwork_type = args.type
    rep = str(args.loops)
    aud = args.audio

    # extracting out the country and album ID
    result = Regx.search(url)
    if result is None:
        print(Fore.RED + "Invalid URL")
        sys.exit()
    country = result.group(1)
    kind = result.group(2)
    id_ = result.group(3)

    # getting the json response
    album_json = get_json(country, id_, token, kind)

    # extracting the master m3u8 from album_json
    m3u8_ = get_m3u8(album_json, artwork_type)

    # metadata crap
    meta = album_json['data'][0]['attributes']

    if kind == 'album':
        album = meta["name"]
        artist = meta["artistName"]
        album_url = meta["url"]
        tracks = meta["trackCount"]
        release_date = meta["releaseDate"]
        upc = meta['upc']
        copyright_ = meta.get("copyright")
        record_label = meta.get('recordLabel')
        try:
            genre = meta["genreNames"][0]
        except (KeyError, TypeError):
            genre = None
        rating = meta.get("contentRating")
        editorial_notes = meta.get('editorialNotes', {}).get('standard')


        # showing general details
        metadata = f"""
            Album Name       : {album}
            Artist           : {artist}
            Rating           : {rating}
            Number of tracks : {tracks}
            Copyright        : {copyright_}
            Release date     : {release_date}
            Genre            : {genre}
        """
        fname = sanitize_filename(f"{artist} - {album} ({release_date[:4]}).mp4")

    elif kind == 'playlist':
        metadata = f"""
            Playlist name    : {meta["name"]}
            Curator name     : {meta["curatorName"]}
            Modified date    : {meta["lastModifiedDate"]}
        """
        fname = sanitize_filename(f"{meta['name']} ({meta['lastModifiedDate'][:4]}).mp4")

    print(metadata)
    current_path = sys.path[0]

    ANIMATED_PATH = os.path.join(current_path, "Animated artworks")
    if not os.path.exists(ANIMATED_PATH):
        os.makedirs(ANIMATED_PATH)

    video_path = os.path.join(current_path, "Animated artworks", fname)

    playlist = m3u8.load(m3u8_)
    # print(playlist.data)
    print_table(playlist.data)
    playlist_id = int(input("Enter the ID: "))
    m3u8_ = playlist.data["playlists"][playlist_id]['uri']

    # downloading video in mp4 container
    print("\nDownloading the video...")

    stream = ffmpeg.input(m3u8_)
    stream = ffmpeg.output(stream, 'video.mp4', codec='copy').global_args(
        '-loglevel', 'quiet', '-y')
    ffmpeg.run(stream)
    del stream

    print("Video downloaded.")

    # making the new looped video
    stream = ffmpeg.input('video.mp4', stream_loop=rep)
    stream = ffmpeg.output(stream, 'fixed.mp4', codec='copy').global_args(
        '-loglevel', 'quiet', '-y')
    ffmpeg.run(stream)
    del stream

    if aud and kind == 'album':

        print("\nAudio tracks:")
        listall(album_json)
        index = int(input("\nSelect the audio track number : "))
        index = index - 1

        m4a = album_json['data'][0]['relationships']['tracks']['data'][index]['attributes']['previews'][0]['url']
        # downloading the selected m4a track using requests
        print("\nDownloading the audio...")
        r = requests.get(m4a, allow_redirects=True)
        open('audio.m4a', 'wb').write(r.content)

        print("Audio downloaded.")

        # multiplexing
        print("\nMultiplexing...")
        # multiplex audio and video using ffmpeg-python
        stream_video = ffmpeg.input('fixed.mp4')
        stream_audio = ffmpeg.input('audio.m4a')
        ffmpeg.output(stream_video, stream_audio, video_path, codec='copy',
                      shortest=None).global_args("-shortest", "-y", '-loglevel', 'quiet').run()
        print("Done.")

        os.remove("fixed.mp4")
        os.remove("audio.m4a")

    else:
        move("fixed.mp4", video_path)

    # tagging
    print("\nTagging metadata..")
    video = MP4(video_path)
    if kind == 'album':
        video["\xa9alb"] = album
        video["aART"] = artist
        video["----:TXXX:URL"] = bytes(album_url, 'UTF-8')
        video["----:TXXX:Total tracks"] = bytes(str(tracks), 'UTF-8')
        video["----:TXXX:Release date"] = bytes(release_date, 'UTF-8')
        video["----:TXXX:UPC"] = bytes(upc, 'UTF-8')
        video["----:TXXX:Content Advisory"] = bytes(
            'Explicit' if rating != '' else 'Clean', 'UTF-8')
        if copyright_ is not None:
            video["cprt"] = copyright_
        if record_label is not None:
            video["----:TXXX:Record label"] = bytes(record_label, 'UTF-8')
        if genre is not None:
            video["\xa9gen"] = genre
        if editorial_notes is not None:
            video["----:TXXX:Editorial notes"] = bytes(
                remove_html_tags(editorial_notes), 'UTF-8')

    elif kind == 'playlist':
        video["\xa9alb"] = meta["name"]
        video["aART"] = meta["curatorName"]
        video["----:TXXX:URL"] = bytes(meta["url"], 'UTF-8')
        video["----:TXXX:Release date"] = bytes(meta["lastModifiedDate"], 'UTF-8')
        if meta["editorialNotes"]['standard'] != '':
            video["----:TXXX:Editorial notes"] = bytes(
                remove_html_tags(meta["editorialNotes"]['standard']), 'UTF-8')
    video.pop("©too")
    video.save()
    print("Done.")

    print('\n'+video_path)

    # deleting temp files
    os.remove("video.mp4")
