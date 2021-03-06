import requests, json, time, os, config

API = 'http://ws.audioscrobbler.com/2.0/'
API_KEY = config.API_KEY

def get_request(url):
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)\
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}
    response = requests.get(url,headers=headers)
    if response.status_code != 200:
        print("Failed with status_code %s" % response.status_code)
        return None
    return response.json()

def get_top_artists_list():
    """
    Get a list of top artists, represented by mbid
    API: http://www.last.fm/api/show/chart.getTopArtists
    """
    method = 'chart.gettopartists'
    url = '%s?method=%s&api_key=%s&format=json' % (API, method, API_KEY)
    artists = get_request(url)['artists']['artist']
    os.chdir('data')
    with open('top_artists_mbid.txt','w') as fo:
        for artist in artists:
            name = artist['name']
            mbid = artist['mbid']
            line = (name + ',' + mbid).encode('utf-8')
            fo.write(line + '\n')
    os.chdir('..')

def get_artists_info():
    """
    Use mbid_artist to get artist information
    API: http://www.last.fm/api/show/artist.getInfo
    """
    with open('data/top_artists_mbid.txt') as fo:
        lst = [x.split(',')[1].strip() for x in fo.readlines()] #artist mbid

    singers = []
    method = 'artist.getinfo'   
    for mbid in lst:
        url = '%s?method=%s&mbid=%s&api_key=%s&format=json' % (API, method, mbid, API_KEY)
        try:
            singer = {} # extract part of artist information
            artist = get_request(url)['artist']
            singer['name'] = artist['name']
            singer['mbid_artist'] = artist['mbid']
            singer['url'] = artist['url']
            singer['listeners'] = artist['stats']['listeners']
            singer['playcount'] = artist['stats']['playcount']
            singer['image'] = artist['image'][2]['#text']
            singer['summary'] = artist['bio']['summary']
            singers.append(singer)
            print("Processed singer %s" % singer['name'])
            time.sleep(1)
        except ValueError as ex:
            print("Exception: %s" % ex)

    with open('data/artists.json','w') as fp:
        json.dump(singers,fp)

def get_top_albums_list():
    """
    Get top albums by top artists
    API: http://www.last.fm/api/show/artist.getTopAlbums
    """
    with open('data/top_artists_mbid.txt') as fo:
        lst = [x.split(',')[0] for x in fo.readlines()] #artist name

    os.chdir('data')
    with open('top_albums_mbid.txt','w') as fo:
        method = 'artist.gettopalbums'
        for name in lst:
            name = name.replace(' ','+')
            url = '%s?method=%s&artist=%s&api_key=%s&format=json' % (API, method, name, API_KEY)
            albums = get_request(url)['topalbums']['album']
            num = min(7, len(albums)) # not all albums
            for album in albums[:num]:
                try:
                    line = (album['name'] + ',' + album['mbid']).decode('utf-8')
                    print("Processed album %s " % album['name'])
                except:
                    print("Failed parse one album")
                fo.write(line + '\n')
            time.sleep(1)
    os.chdir('..')

def get_albums_info():
    """
    Get album information by mbid
    API: http://www.last.fm/api/show/album.getInfo
    """
    with open('data/top_albums_mbid.txt') as fo:
        lst = [x.split(',')[1].strip() for x in fo.readlines()] # album mbid
        lst = filter(lambda x: '-' in x, lst) # filter unvalid mbid

    albums = []
    method='album.getinfo'
    for mbid in set(lst): # duplications found
        url = '%s?method=%s&mbid=%s&api_key=%s&format=json' % (API, method, mbid, API_KEY)
        try:
            album = {} #extract part of album information
            disk = get_request(url)['album']
            album['name'] = disk['name']
            album['artist'] = disk['artist']
            # one artist vs many albums
            album['mbid_artist'] = disk['tracks']['track'][0]['artist']['mbid']
            album['mbid_album'] = disk['mbid']
            album['image'] = disk['image'][2]['#text']
            album['listeners'] = disk['listeners']
            album['playcount'] = disk['playcount']
            album['tracks'] = [x['name'] for x in disk['tracks']['track']]
            album['published'] = disk['wiki']['published']
            album['summary'] = disk['wiki']['summary']
            albums.append(album)
            print("Processed album %s" % album['name'])
            time.sleep(1)
        except KeyError as ex:
            print("Exception: %s" % ex)
        except ValueError as ex:
            print("Exception: %s" % ex)
        except:
            print("Unknown error occurs")
    
    with open('data/albums.json','w') as fp:
        json.dump(albums,fp)

def get_tracks_list():
    """
    Extract track list from albums information
    Use track name and artist
    """
    with open('data/albums.json') as fp:
        albums = json.load(fp)
    with open('data/tracks_list.txt','w') as fo:
        for album in albums:
            artist = album['artist']
            for name in album['tracks']:
                line = (artist + ',' + name).encode('utf-8')
                fo.write(line + '\n')

def get_tracks_info():
    """
    Get track information base on track name and artists
    API: http://www.last.fm/api/show/track.getInfo
    """
    with open('data/tracks_list.txt','r') as fo:
        lst = [(x.split(',')[0], x.split(',')[1].strip()) for x in fo.readlines()]
    
    tracks = []
    method = 'track.getInfo'
    for (artist, track_name) in set(lst):
        artist = artist.replace(' ','+')
        track_name = track_name.replace(' ','+')
        url = '%s?method=%s&api_key=%s&artist=%s&track=%s&format=json' % (API, method, API_KEY, artist, track_name)
        try:
            track = {} # extract part of track information
            song = get_request(url)['track']
            track['name'] = song['name']
            track['mbid_track'] = song['mbid']
            track['url'] = song['url']
            track['duration'] = song['duration']
            track['listeners'] = song['listeners']
            track['playcount'] = song['playcount']
            track['artist'] = song['artist']['name']
            track['mbid_artist'] = song['artist']['mbid']
            track['album'] = song['album']['title']
            track['mbid_album'] = song['album']['mbid']
            track['tags'] = song['toptags']['tag']
            tracks.append(track)
            print("Processed track %s" % track['name'])
            time.sleep(0.7)
        except KeyError as ex:
            print("Exception: %s" % ex)
        except ValueError as ex:
            print("Exception: %s" % ex)
        except:
            print("Unknown error occurs")

    with open('data/tracks.json','w') as fp:
        json.dump(tracks,fp)

def get_tags_list():
    """
    Extract tags from tracks information
    Only perserve tag name and url
    """
    with open('data/tracks.json','r') as fp:
        tracks = json.load(fp)
    
    tags = set()
    for track in tracks:
        for record in track['tags']:
            tag = (record['name'], record['url'])
            tags.add(tag)

    with open('data/tags_list.txt','w') as fp:
        for (name, url) in tags:
            line = (name + ',' + url).encode('utf-8')
            fp.write(line + '\n')

if __name__ == '__main__':
    # get_top_artists_list()
    # get_artists_info()
    # get_top_albums_list()
    # get_albums_info()
    # get_tracks_list()
    # get_tracks_info()
    get_tags_list()
