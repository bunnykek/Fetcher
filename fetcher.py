#by bunny

import requests, re, os, subprocess, m3u8, sys
from shutil import move
from mutagen.mp4 import MP4


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
    #response = requests.get("https://k0ybdlmho9.execute-api.ap-northeast-1.amazonaws.com/prod/tokens/applemusic/generate")
    #return(response.json()['token'])
    return('eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ.eyJpc3MiOiJBTVBXZWJQbGF5IiwiaWF0IjoxNjQ0OTQ5MzI0LCJleHAiOjE2NjA1MDEzMjR9.3RUn173ddFRpam0ksOFS-vJFR-wCtJHzcSdGr7exxFQScWxzQxHGht4wyt6iJQqNcEOR4BRmv6O4-2B4jzrGsQ')

def get_album_json(country, alb_id, token):
    
    headers = {
        'authorization': f'Bearer {token}'
    }

    params = (
        ('filter[equivalents]', f'{alb_id}'),
        ('extend', 'offers,editorialVideo'),
    )

    response = requests.get(f'https://amp-api.music.apple.com/v1/catalog/{country}/albums', headers=headers, params=params)
    return(response.json())

def get_m3u8(json, atype):
    if atype == 'T' or atype == 't':
      return(json['data'][0]['attributes']['editorialVideo']['motionDetailTall']['video'])
    elif atype == 'S' or atype == 's':
      return(json['data'][0]['attributes']['editorialVideo']['motionDetailSquare']['video'])

def listall(json):
    totaltracks = int(json['data'][0]['attributes']['trackCount'])
    for i in range(totaltracks):
        if json['data'][0]['relationships']['tracks']['data'][i]['type'] == "songs":
            song = json['data'][0]['relationships']['tracks']['data'][i]['attributes']['name']
            print(f"        {i+1}. {song}")

def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def check_token(tkn):
    headers = {
        'authorization': f'Bearer {tkn}'
    }

    params = (
        ('filter[equivalents]', '1551901062'),
        ('extend', 'editorialVideo'),
    )

    response = requests.get('https://amp-api.music.apple.com/v1/catalog/in/albums', headers=headers, params=params)

    if response.status_code != 200:
        raise ValueError(401)



if __name__ == "__main__":
    
    #clean screen
    if os.name == 'nt':
        subprocess.call("cls", shell=True) # windows
    else:
        subprocess.call("clear") # linux/mac
    
    print(title)

    token = get_auth_token()
    print("Checking if the token is still alive...")
    #checking if the token is still alive
    try:
        check_token(token)
    except Exception as e:
        print("Dead token :/")
        sys.exit()
    
    print("good!")

    #Taking input from the user
    url = input("Enter the Album URL : ")
    artwork_type = input("Do you need the (T)aller or (S)quarer one : ")
    rep = input("Number of times you want to loop the artwork (recommended = 2)  : ")
    aud = input("Do you also need the audio in the artwork? [y/n] : ")
    
    #extracting out the country and album ID
    country = re.search("/\D\D/",url).group().replace("/","")
    id_ = re.search("\d+",url).group()
    
    album_json = get_album_json(country, id_, token)
    

    #extracting the master m3u8 from album_json
    m3u8_ = get_m3u8(album_json, artwork_type)
    
    
    #metadata crap
    meta = album_json['data'][0]['attributes']
    
    album = meta["name"]
    artist = meta["artistName"]
    album_url = meta["url"]
    rating = meta["contentRating"]
    tracks = meta["trackCount"]
    copyright_ = meta["copyright"]
    release_date = meta["releaseDate"]
    genre = meta["genreNames"][0]
    upc = meta['upc']
    record_label = meta['recordLabel']
    editorial_notes = ''
    try:
        editorial_notes = meta['editorialNotes']['standard']
    except:
        pass
    #showing general details
    metadata = f"""\n
        Album Name       : {album}
        Artist           : {artist}
        Rating           : {rating}
        Number of tracks : {tracks}
        Copyright        : {copyright_}
        Release date     : {release_date}
        Genre            : {genre}
        URL              : {album_url}
    """
    print(metadata)
    
    
    #file name
    fname = f"{artist} - {album} ({release_date[:4]}).mp4" 
    current_path = sys.path[0]
    
    try:
        os.makedirs(os.path.join(current_path,"Animated artworks"))
    except:
         pass
        
    video_path = os.path.join(current_path,"Animated artworks",fname)
    
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

        print("All the audio tracks:\n")
        listall(album_json)
        index = int(input("\nSelect the audio track number : "))
        index = index - 1

        m4a = album_json['data'][0]['relationships']['tracks']['data'][index]['attributes']['previews'][0]['url']

        #downloading the selected m4a track
        print("\nDownloading the audio...")
        subprocess.Popen(["ffmpeg","-y","-i",m4a,"-acodec","copy","audio.m4a"],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
        print("Audio downloaded.")
    
        #multiplexing
        print("\nMultiplexing...")
        subprocess.Popen(["ffmpeg","-y","-i","fixed.mp4","-i","audio.m4a","-map_metadata","0" ,"-fflags", "+bitexact" ,"-flags:v" ,"+bitexact","-flags:a", "+bitexact","-c","copy","-shortest",video_path],stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).wait()
        print("Done.")
    
        os.remove("fixed.mp4")
        os.remove("audio.m4a")
    
    else:
        move("fixed.mp4", video_path)
    
    
    #tagging
    
    print("\nTagging metadata..")
    video = MP4(video_path)
    video["\xa9alb"] = album
    video["aART"] = artist
    video["----:TXXX:URL"] = bytes(album_url,'UTF-8')
    video["----:TXXX:Content Advisory"] = bytes(rating,'UTF-8')
    video["----:TXXX:Total tracks"] = bytes(str(tracks),'UTF-8')
    video["cprt"] = copyright_
    video["----:TXXX:Release date"] = bytes(release_date,'UTF-8')
    video["----:TXXX:UPC"] = bytes(upc,'UTF-8')
    video["----:TXXX:Record label"] = bytes(record_label,'UTF-8')
    video["\xa9gen"] = genre
    if editorial_notes != '':
        video["----:TXXX:Editorial notes"] = bytes(remove_html_tags(editorial_notes),'UTF-8')
    video.save()
    print("Done.")
    
    print ('\n'+video_path)
    
    #deleting temp files
    os.remove("video.mp4")

