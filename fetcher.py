import requests
import re
import os
import subprocess
import bs4
import lxml
import m3u8
from shutil import move
from mutagen.mp4 import MP4

if __name__ == "__main__":
    #clean screen
    if os.name == 'nt':
        subprocess.call("cls", shell=True) # windows
    else:
        subprocess.call("clear") # linux/mac
    
    ####
    title = """
         _    __  __       _          _                 _           _                              
        / \  |  \/  |     / \   _ __ (_)_ __ ___   __ _| |_ ___  __| |                             
       / _ \ | |\/| |    / _ \ | '_ \| | '_ ` _ \ / _` | __/ _ \/ _` |                             
      / ___ \| |  | |   / ___ \| | | | | | | | | | (_| | ||  __/ (_| |                             
     /_/   \_\_|  |_|  /_/   \_\_| |_|_|_| |_| |_|\__,_|\__\___|\__,_|                             
                        _         _                      _         __      _       _               
                       / \   _ __| |___      _____  _ __| | __    / _| ___| |_ ___| |__   ___ _ __ 
                      / _ \ | '__| __\ \ /\ / / _ \| '__| |/ /   | |_ / _ \ __/ __| '_ \ / _ \ '__|
                     / ___ \| |  | |_ \ V  V / (_) | |  |   <    |  _|  __/ || (__| | | |  __/ |   
                    /_/   \_\_|   \__| \_/\_/ \___/|_|  |_|\_\   |_|  \___|\__\___|_| |_|\___|_|   
                                                                                                   -- by bunny  
    """
    
    print(title)
    
    
    #regex crap
    regex="https://mvod.itunes.apple.com/itunes-assets/HLSMusic\d{3}/v4/\w{2}/\w{2}/\w{2}/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}/\w{10}_default.m3u8"
    m4a_regex = "https://audio-ssl.itunes.apple.com/itunes-assets/AudioPreview\w{3}/\w{2}/\w{2}/\w{2}/\w{2}/\w{8}-\w{4}-\w{4}-\w{4}-\w{12}/\w+.plus.aac.ep.m4a"
    
    #Takes link from user
    url = input("Enter the Album URL : ")
    rep = input("Number of times you want to loop the artwork (recommended = 2)  : ")
    aud = input("Do you also need the audio in the artwork? [y/n] : ")
    
    #extracting out the country and album ID
    country = re.search("/\D\D/",url).group().replace("/","")
    id_ = re.search("\d+",url).group()
    
    #get request to the album url
    response = requests.get(url)
    
    #making the soup :D
    soup = bs4.BeautifulSoup(response.text,"lxml")
    
    #extracting the master m3u8 from html using regular expression
    m3u8_ = re.search(regex,response.text).group()
    
    #using itunes unofficial API for getting album metadata
    metadata = requests.get(f"https://itunes.apple.com/lookup?id={id_}&country={country}&entity=album").json()
    
    
    #metadata crap
    meta = metadata["results"][0]
    
    album = meta["collectionName"]
    artist = meta["artistName"]
    album_url = meta["collectionViewUrl"]
    rating = meta["collectionExplicitness"]
    tracks = meta["trackCount"]
    copyright_ = meta["copyright"]
    release_date = meta["releaseDate"]
    genre = meta["primaryGenreName"]
    
    #showing general details
    metadata = f"""\n
    Album Name       : {album}
    Artist           : {artist}
    Rating           : {rating}
    Number of tracks : {tracks}
    Copyright        : {copyright_}
    Release date     : {release_date}
    Genre            : {genre}
    Album URL        : {album_url}
    """
    print(metadata)
    
    
    #file name
    fname = f"{artist} - {album} ({release_date[:4]}).mp4" 
    
    
    #getting the popular track m4a link
    popular = int(soup.find("button", {"aria-label": "Popular Track, Loved"}).parent.parent.parent['data-row'])
    m4a = re.findall(m4a_regex,response.text)[popular]
    
    
    #parsing the playlist and getting the max res hevc containing m3u8 file
    playlist = m3u8.load(m3u8_)
    m3u8_ = playlist.data["playlists"][-1]['uri']
    
    
    #downloading video in mp4 container
    print("\nDownloading the video...")
    subprocess.Popen(["ffmpeg","-y","-i",m3u8_,"-vcodec","copy","video.mp4"],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
    print("Video downloaded.")
    
    
    #making the new looped video
    subprocess.Popen(["ffmpeg","-y","-stream_loop",rep,"-i","video.mp4","-map_metadata","0","-fflags", "+bitexact" ,"-flags:v" ,"+bitexact","-flags:a", "+bitexact","-c","copy","fixed.mp4"],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
    
    
    if(aud=="Y" or aud =="y"):
        #downloading the popular m4a track
        print("\nDownloading the audio...")
        subprocess.Popen(["ffmpeg","-y","-i",m4a,"-acodec","copy","audio.m4a"],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
        print("Audio downloaded.")
    
        #multiplexing
        print("\nMultiplexing...")
        subprocess.Popen(["ffmpeg","-y","-i","fixed.mp4","-i","audio.m4a","-map_metadata","0" ,"-fflags", "+bitexact" ,"-flags:v" ,"+bitexact","-flags:a", "+bitexact","-c","copy","-shortest",fname],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
        print("Done.")
    
        os.remove("fixed.mp4")
        os.remove("audio.m4a")
    
    else:
        move("fixed.mp4", fname)
    
    
    #tagging
    
    print("\nTagging metadata..")
    video = MP4(fname)
    video["\xa9alb"] = album
    video["\xa9ART"] = artist
    video["----:TXXX:URL"] = bytes(album_url,'UTF-8')
    video["----:TXXX:Rating"] = bytes(rating,'UTF-8')
    video["----:TXXX:Total tracks"] = bytes(str(tracks),'UTF-8')
    video["cprt"] = copyright_
    video["----:TXXX:Release date"] = bytes(release_date,'UTF-8')
    video["\xa9gen"] = genre
    video.save()
    print("Done.")
    
    print (os.path.join(os.getcwd(),fname))
    
    #deleting temp files
    os.remove("video.mp4")

