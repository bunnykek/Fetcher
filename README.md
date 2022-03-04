![fetcher](https://github.com/bunnykek/Apple-Music-Animated-Artwork-Fetcher/blob/main/assets/logo.svg "fetcher")
# Apple Music Animated Artwork Fetcher
## Features

- Downloads the animated artwork from Apple Music in Highest available HEVC quality.
- Can also multiplex the animated artwork with the track of your choice from that album.
- Will also tag the artwork with all the metadata of the album.






## How to use?

Make sure you have [python](https://www.python.org/ "python") installed in your system.

Download this repo and navigate into its directory or follow the below commands (install [git](https://git-scm.com/) first):

```
git clone https://github.com/bunnykek/Apple-Music-Animated-Artwork-Fetcher
cd Apple-Music-Animated-Artwork-Fetcher
```

Download the ffmpeg binary(.exe for Windows) for your OS from [here](https://ffbinaries.com/downloads) and put that binary inside ``Apple-Music-Animated-Artwork-Fetcher`` folder

use 'pip3' in the below command if 'pip' doesn't work for you. 
```
pip install -r requirements.txt
```
Use "py" or "python3" if  "python" doesn't  work for you.
```
python fetcher.py -h
```
```
usage: fetcher.py [-h] [-T TYPE] [-L LOOPS] [-A] url

Downloads animated cover artwork from Apple music.

positional arguments:
  url                   Album URL

options:
  -h, --help            show this help message and exit
  -T TYPE, --type TYPE  [tall,square] (square by default)
  -L LOOPS, --loops LOOPS
                        [int] Number of times you want to loop the artwork (2 by default)
  -A, --audio           Pass this flag if you also need the audio
```
Ex:
``` 
py fetcher.py -T tall -L 2 -A https://music.apple.com/us/album/planet-her-deluxe/1574004234
```

The video will be saved in the ``Animated artworks`` folder.


## Some animated album links:
```
https://music.apple.com/us/album/evermore-deluxe-version/1547315522
https://music.apple.com/us/album/positions-deluxe-edition/1553944254
https://music.apple.com/us/album/after-hours-deluxe-video-album/1551901062
https://music.apple.com/us/album/planet-her-deluxe/1574004234
https://music.apple.com/us/album/folklore-deluxe-version/1528112358
```
![cmd](https://i.imgur.com/V2EtMyC.png "cmd")
```
General
Complete name                            : Taylor Swift - evermore (deluxe version) (2021).mp4
Format                                   : MPEG-4
Format profile                           : Base Media
Codec ID                                 : isom (isom/iso2/mp41)
File size                                : 118 MiB
Duration                                 : 39 s 914 ms
Overall bit rate                         : 24.7 Mb/s
Album                                    : evermore (deluxe version)
Album/Performer                          : Taylor Swift
Genre                                    : Alternative
Copyright                                : ℗ 2021 Taylor Swift
Total tracks                             : 17
Content Advisory                         : explicit
Release date                             : 2021-01-07
Record label                             : Taylor Swift
UPC                                      : 00602435688749
URL                                      : https://music.apple.com/us/album/evermore-deluxe-version/1547315522
Editorial notes                          : Surprise-dropping a career-redefining album in the midst of a paralyzing global pandemic is an admirable flex; doing it again barely five months later is a display of confidence and concentration so audacious that you’re within your rights to feel personally chastised. Like folklore, evermore is a team-up with Aaron Dessner, Jack Antonoff, and Justin Vernon, making the most of cozy home-studio vibes for more bare-bones arrangements and bared-soul lyrics, casually intimate and narratively rich. / There is an expanded guest roster here—HAIM appears on “no body, no crime,” which seems to place Este Haim in the center of a small-town murder mystery, while Dessner’s bandmates in The National are on “coney island”—but they fit themselves into the mood rather than distract from it. (The percussive “long story short” sounds like it could have been on any National album in the past decade.) Elsewhere, “'tis the damn season” is the elegaic home-for-the-holidays ballad this busted year didn’t realize it needed. But while so much of folklore’s appeal involved marveling at how this setting seemed to have unlocked something in Swift, the only real shock here is the timing of the release itself. Beyond that, it’s an extension and confirmation of its predecessor’s promises and charms, less a novelty driven by unprecedented circumstances and instead simply a thing she happens to do and do well.

Video
ID                                       : 1
Format                                   : HEVC
Format/Info                              : High Efficiency Video Coding
Format profile                           : Main 10@L5@High
Codec ID                                 : hvc1
Codec ID/Info                            : High Efficiency Video Coding
Duration                                 : 39 s 900 ms
Bit rate                                 : 24.4 Mb/s
Width                                    : 2 048 pixels
Height                                   : 2 732 pixels
Display aspect ratio                     : 0.750
Frame rate mode                          : Constant
Frame rate                               : 30.000 FPS
Color space                              : YUV
Chroma subsampling                       : 4:2:0
Bit depth                                : 10 bits
Scan type                                : Progressive
Bits/(Pixel*Frame)                       : 0.146
Stream size                              : 116 MiB (99%)
Color range                              : Limited
Color primaries                          : BT.709
Transfer characteristics                 : BT.709
Matrix coefficients                      : BT.709
Codec configuration box                  : hvcC

Audio
ID                                       : 2
Format                                   : AAC LC
Format/Info                              : Advanced Audio Codec Low Complexity
Codec ID                                 : mp4a-40-2
Duration                                 : 39 s 914 ms
Source duration                          : 39 s 962 ms
Bit rate mode                            : Constant
Bit rate                                 : 265 kb/s
Channel(s)                               : 2 channels
Channel layout                           : L R
Sampling rate                            : 44.1 kHz
Frame rate                               : 43.066 FPS (1024 SPF)
Compression mode                         : Lossy
Stream size                              : 1.25 MiB (1%)
Source stream size                       : 1.25 MiB (1%)
Language                                 : English
Default                                  : Yes
Alternate group                          : 1
```
