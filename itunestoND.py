#!/usr/bin/env python

# itunestoND.py - Transfers song ratings, playcounts and play dates from I-Tunes library
# to the Navidrome database

import sys, sqlite3, datetime, re, pprint, unicodedata
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
from lxml import etree

def get_db_path(dbID):
    while True:
        path = Path(input('Enter the path to the %s: ' % dbID))
        if not path.is_file():
            print(str(path) + ' is not a file. Try again.')
        else: break
    return path

def determine_userID(nd_p):
    conn = sqlite3.connect(nd_p)
    cur = conn.cursor()
    cur.execute('SELECT id, user_name FROM user')
    users = cur.fetchall()
    if len(users) == 1:
        print(f'Changes will be applied to the {users[0][1]} Navidrome account.')
    else:
        raise Exception('There needs to be exactly one user account set up with Navidrome. You either have 0, or more than 1 user account.')
    conn.close()
    return users[0][0]

def update_playstats(d1, id, playcount, playdate, rating=0):
    d1.setdefault(id, {})
    d1[id].setdefault('play count', 0)
    d1[id].setdefault('play date', datetime.datetime.fromordinal(1))
    d1[id]['play count'] += playcount
    d1[id]['rating'] = rating

    if playdate > d1[id]['play date']: d1[id].update({'play date': playdate})

def write_to_annotation(dictionary_with_stats, entry_type, conn, cur):
    annotation_entries = []
    for item_id in dictionary_with_stats:
        this_entry = dictionary_with_stats[item_id]
        
        play_count = this_entry['play count']
        play_date = this_entry['play date'].strftime('%Y-%m-%d %H:%M:%S')
        rating = this_entry['rating']

        annotation_entries.append((userID, item_id, entry_type, play_count, play_date, rating, 0, None))

    if annotation_entries:
        cur.executemany('INSERT INTO annotation VALUES (?, ?, ?, ?, ?, ?, ?, ?)', annotation_entries)
        conn.commit()
        # cur.executemany('INSERT INTO consumers VALUES (?,?,?,?)', purchases)
        # cur.execute("INSERT INTO consumers VALUES (1,'John Doe','john.doe@xyz.com','A')")

_ = None
while _ != 'proceed':
    print()
    print('This script will migrate certain data from your ITunes library to your Navidrome database.', 
        "Back up all your data in case it doesn't work properly on your setup. NO WARRANTIES. NO PROMISES.", 
        "The script will DELETE existing data you have in your Navidrome database so it can start \"fresh\".", sep='\n')
    print()

    _ = input('Type PROCEED to continue, or Q to quit: ').lower()

    if _ == 'q': print('Good bye.'); sys.exit(0)

nddb_path = get_db_path('Navidrome database')
itdb_path = get_db_path('Itunes database')
def parse_itunes_xml_streaming(xml_path):
    """Generator that yields song entries without loading entire XML into memory"""
    context = etree.iterparse(xml_path, events=('start', 'end'))
    
    # First pass: get music folder path and count songs
    print('\nAnalyzing iTunes library structure...')
    with open(xml_path, 'r', encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'lxml-xml')
        it_root_music_path = unquote(soup.find('key', text='Music Folder').next_sibling.text)
        songs = soup.dict.dict.find_all('dict')
        song_count = len(songs)
        del(soup)
    
    print(f'Found {song_count:,} files in iTunes database to process.')
    print('Starting optimized streaming parse...')
    return it_root_music_path, songs, song_count

it_root_music_path, songs, song_count = parse_itunes_xml_streaming(itdb_path)

userID = determine_userID(nddb_path)
songID_correlation = {} # we'll save this for later use to transfer Itunes playlists to ND (another script)
artists = {}            # artists and albums will keep count of plays and play dates for each
albums = {}
files = {}


status_interval = max(1, song_count // 8)
counter = 0

conn = sqlite3.connect(nddb_path)
cur = conn.cursor()
cur.execute('DELETE FROM annotation')
conn.commit()

# Pre-load all media file paths for faster lookup
print('Loading Navidrome media file index...')
cur.execute('SELECT id, path, artist_id, album_id FROM media_file')
media_lookup = {row[1]: (row[0], row[2], row[3]) for row in cur.fetchall()}
print(f'Loaded {len(media_lookup):,} media files from Navidrome database.')

for it_song_entry in songs:
    counter += 1    # progress tracking feedback
    if counter % status_interval == 0:
        print(f'{counter:,} files parsed so far of {song_count:,} total songs.')

    # Skip entries without location data
    location_key = it_song_entry.find('key', string='Location')
    if location_key is None: 
        continue

    song_path = unquote(location_key.next_sibling.text)
    if not song_path.startswith(it_root_music_path):  # excludes non-local content
        continue   

    song_path = re.sub(it_root_music_path, '', song_path)
    # Normalize Unicode from decomposed (NFD) to composed (NFC) form for database matching
    song_path = unicodedata.normalize('NFC', song_path)

    # Fast lookup using pre-loaded media index
    matching_files = [info for path, info in media_lookup.items() if song_path in path]
    if not matching_files:
        print(f"Error while parsing {song_path}. Navidrome does not acknowledge that file's existence.")
        print("Maybe Navidrome doesn't like the extension? Skipping.")
        continue
    elif len(matching_files) > 1:
        # If multiple matches, find exact match or best match
        exact_match = next((info for path, info in media_lookup.items() if path.endswith(song_path)), None)
        if exact_match:
            song_id, artist_id, album_id = exact_match
        else:
            song_id, artist_id, album_id = matching_files[0]
    else:
        song_id, artist_id, album_id = matching_files[0]


    # correlate Itunes ID with Navidrome ID (for use in a future script)
    it_song_ID = int(it_song_entry.find('key', string='Track ID').next_sibling.text)
    songID_correlation.update({it_song_ID: song_id})
    
    try:    # get rating, play count & date from Itunes
        song_rating = int(it_song_entry.find('key', string='Rating').next_sibling.text)
        song_rating = int(song_rating / 20)
    except AttributeError: song_rating = 0 # rating = 0 (unrated) if it's not rated in itunes
        
    try:
        play_count = int(it_song_entry.find('key', string='Play Count').next_sibling.text)
        last_played = it_song_entry.find('key', string='Play Date UTC').next_sibling.text[:-1] # slice off the trailing 'Z'
        last_played = datetime.datetime.strptime(last_played, '%Y-%m-%dT%H:%M:%S') # convert from string to datetime object. Example string: '2020-01-19T02:24:14Z'
    except AttributeError: continue

    update_playstats(artists, artist_id, play_count, last_played)
    update_playstats(albums, album_id, play_count, last_played)
    update_playstats(files, song_id, play_count, last_played, rating=song_rating)

    

print('Writing changes to database:')
write_to_annotation(artists, 'artist', conn, cur)
print('Done writing artist records to database.')
write_to_annotation(files, 'media_file', conn, cur)
print('Done writing music file records to database.')
write_to_annotation(albums, 'album', conn, cur)
print('Album records saved to database.')

conn.close()

with open('IT_file_correlations.py', 'w') as f:
    f.write('# Following python dictionary correlates the itunes integer ID to the Navidrome file ID for each song.\n')
    f.write('# {ITUNES ID: ND ID} is the format. \n\n')
    f.write('itunes_correlations = ')
    f.write(pprint.pformat(songID_correlation))

print('Navidrome database updated.')
print(f"File correlation index saved to {str(Path.cwd() / 'IT_file_correlations.py')}\n")
print('You can delete it if you want, but I will use it later in a script to transfer playlists from Itunes to Navidrome.')
