#! /usr/bin/env python

# itunesPlaylistMigrator.py - Used in conjunction with itunestoND.py
# First run that script, then run this one while you have your Navidrome server running.
# It will parse the Itunes library XML file and use the Navidrome API to transfer your playlists.

from pathlib import Path
import sys, requests, urllib.parse, random, re, string, json, argparse, os
from bs4 import BeautifulSoup
import pyinputplus as pyip
from hashlib import md5

try:
    from IT_file_correlations import *
    print('File correlations between the databases successfully imported.')
except ModuleNotFoundError:
    print('You need to put the IT_file_correlations.py file in the same directory as this script.')
    sys.exit(1)

def send_api_request(endpoint, **kwargs):
    api_args = {'f': 'json', 'u': username, 'v': '1.16.1', 'c': 'python'}
    api_args.update(kwargs)

    pool = string.ascii_letters + string.digits
    salt = ''.join(random.choice(pool) for i in range(7))
    token = md5((password + salt).encode('utf-8')).hexdigest()

    api_args.update({'t': token, 's': salt})

    try:
        res = requests.get(server_url + endpoint, params=api_args)
        res.raise_for_status()

    except:
        print(f"Could not reach Navidrome Server. You entered {server_url.partition('rest/')[0]}")
        print('Make sure that address is correct.')
        print()
        if pyip.inputYesNo(prompt='Is the server running? ') == 'yes':
            print('Well you better go catch it!')
        else:
            print('Start the Navidrome server and try again.')
        return False

    try:
        res = json.loads(res.text)['subsonic-response']
        if res['status'] == 'ok':
            return res
        else:
            print('\nSomething went wrong with the Navidrome server.\n')
            print(f'Message: {res["error"]["message"]}. Code {res["error"]["code"]}.')
            return False
    except KeyError:
        print('Seems that the address you entered does not go to a navidrome server.')

def find_itunes_library():
    """Auto-detect iTunes library file"""
    search_paths = [
        Path.cwd(),
        Path.home() / 'Music' / 'iTunes',
        Path(os.path.expanduser('~/Music/iTunes')),
    ]
    
    patterns = ['*[Ll]ibrary.xml', 'iTunes Library.xml', 'library.xml']
    
    for search_path in search_paths:
        if search_path.exists():
            for pattern in patterns:
                files = list(search_path.glob(pattern))
                if files:
                    return files
    return []

def select_file(files, file_type):
    """Let user select from multiple found files"""
    if len(files) == 1:
        print(f'Found {file_type}: {files[0]}')
        return files[0]
    
    print(f'\nFound multiple {file_type} files:')
    for i, file in enumerate(files, 1):
        print(f'{i}. {file}')
    
    while True:
        try:
            choice = int(input(f'Select {file_type} (1-{len(files)}): '))
            if 1 <= choice <= len(files):
                return files[choice - 1]
            print(f'Please enter a number between 1 and {len(files)}')
        except ValueError:
            print('Please enter a valid number')

def get_playlist_processing_mode():
    """Ask user how they want to process playlists"""
    print('\nPlaylist processing options:')
    print('1. Review each playlist individually (default)')
    print('2. Accept all playlists automatically')
    print('3. Preview playlists without processing')
    
    while True:
        choice = input('Choose processing mode [1-3] (default: 1): ').strip()
        if choice == '' or choice == '1':
            return 'individual'
        elif choice == '2':
            return 'accept_all'
        elif choice == '3':
            return 'preview'
        else:
            print('Please enter 1, 2, or 3')

def setup_server_connection(server_url_arg=None, username_arg=None, password_arg=None):
    """Setup connection to Navidrome server"""
    global server_url, username, password
    
    login_successful = False
    while not login_successful:
        if not server_url_arg:
            server_url = input('Enter the address to your navidrome server: ')
        else:
            server_url = server_url_arg
            
        if not username_arg:
            username = input('Enter your Navidrome username: ')
        else:
            username = username_arg
            
        if not password_arg:
            password = pyip.inputPassword(prompt='Enter the password to your Navidrome account: ')
        else:
            password = password_arg

        if not server_url.startswith('http'):
            server_url = 'http://' + server_url
        if server_url.endswith('/'):
            server_url = server_url[:-1]
        server_url += '/rest/'
        
        login_successful = send_api_request('ping')
        if login_successful:
            print('\nConnection to server successful.')
            return True
        else:
            # Reset for retry if using args
            if server_url_arg or username_arg or password_arg:
                print('Connection failed with provided credentials.')
                return False
            server_url_arg = username_arg = password_arg = None

def get_library_file(library_path=None):
    """Get iTunes library file with auto-detection"""
    if library_path and library_path.is_file():
        print(f'Using provided library: {library_path}')
        return library_path
    
    # Try auto-detection
    files = find_itunes_library()
    if files:
        return select_file(files, 'iTunes library')
    
    # Fallback to manual entry
    it_db_path = Path.cwd() / 'Library.xml'
    while not it_db_path.is_file():
        print(f'I did not find a file at {it_db_path}')
        it_db_path = Path(input('Enter the absolute path to the iTunes library: '))
    
    print(f'Using {it_db_path} for the iTunes library.')
    return it_db_path

def main():
    parser = argparse.ArgumentParser(description='Migrate iTunes playlists to Navidrome')
    parser.add_argument('--library', type=Path, help='Path to iTunes Library.xml file')
    parser.add_argument('--server', help='Navidrome server URL')
    parser.add_argument('--username', help='Navidrome username')
    parser.add_argument('--password', help='Navidrome password')
    parser.add_argument('--batch', action='store_true', help='Accept all playlists without prompts')
    parser.add_argument('--preview', action='store_true', help='Preview playlists without processing')
    
    args = parser.parse_args()
    
    # Setup server connection
    if not setup_server_connection(args.server, args.username, args.password):
        sys.exit(1)
    
    # Get library file
    it_db_path = get_library_file(args.library)
    
    print('Loading iTunes playlists...')
    with open(it_db_path, 'r', encoding='utf-8') as f: 
        soup = BeautifulSoup(f, 'lxml-xml')
    playlists = soup.array.find_all('dict', recursive=False)
    print(f'Found {len(playlists)} playlists to process.')
    
    # Determine processing mode
    if args.preview:
        processing_mode = 'preview'
    elif args.batch:
        processing_mode = 'accept_all'
    else:
        processing_mode = get_playlist_processing_mode()
    
    # Process playlists
    process_playlists(playlists, processing_mode)

def process_playlists(playlists, processing_mode):
    """Process playlists based on selected mode"""
    playlists_to_skip = ('Library', 'Downloaded', 'Music', 'Movies', 'TV Shows', 'Podcasts', 'Audiobooks', 'Tagged', 'Genius')
    
    # Collect all missing tracks for summary
    all_missing_tracks = {}
    processed_playlists = []
    skipped_playlists = []
    
    # First pass: collect playlist info
    valid_playlists = []
    for plist in playlists:
        if plist.find('key', text='Distinguished Kind'): continue
        
        playlist_name = plist.find('key', text='Name').find_next('string').text
        if playlist_name in playlists_to_skip: continue
        if plist.find('key', text='Smart Info'): continue
        
        try:
            playlist_tracks = plist.array.find_all('dict')
            if playlist_tracks:
                valid_playlists.append((playlist_name, playlist_tracks))
        except AttributeError:
            continue
    
    if processing_mode == 'preview':
        print('\nPlaylist Preview:')
        for playlist_name, tracks in valid_playlists:
            print(f'  {playlist_name}: {len(tracks)} tracks')
        print(f'\nTotal: {len(valid_playlists)} playlists found')
        return
    
    # Process playlists
    for playlist_name, playlist_tracks in valid_playlists:
        if processing_mode == 'individual':
            print(f'\nPlaylist "{playlist_name}" contains {len(playlist_tracks)} tracks.')
            should_process = pyip.inputYesNo(prompt='Do you want to move it to Navidrome? ')
            if should_process == 'no':
                skipped_playlists.append(playlist_name)
                continue
        elif processing_mode == 'accept_all':
            print(f'Processing playlist "{playlist_name}" ({len(playlist_tracks)} tracks)...')
        
        # Create playlist
        create_playlist_reply = send_api_request('createPlaylist', name=playlist_name)
        if not create_playlist_reply:
            print(f'Failed to create playlist "{playlist_name}"')
            continue
        
        ND_playlist_id = create_playlist_reply['playlist']['id']
        it_track_ids = [int(track.integer.text) for track in playlist_tracks]
        
        # Build list of Navidrome track IDs
        ND_track_ids = []
        missing_tracks = []
        for it_id in it_track_ids:
            if it_id in itunes_correlations:
                ND_track_ids.append(itunes_correlations[it_id])
            else:
                missing_tracks.append(it_id)
        
        # Store missing tracks for summary
        if missing_tracks:
            all_missing_tracks[playlist_name] = missing_tracks
        
        if not ND_track_ids:
            print(f'No tracks from playlist "{playlist_name}" could be migrated. Skipping.')
            continue
        
        # Add tracks in batches
        batch_size = 100
        for i in range(0, len(ND_track_ids), batch_size):
            batch = ND_track_ids[i:i + batch_size]
            add_tracks_reply = send_api_request('updatePlaylist', playlistId=ND_playlist_id, songIdToAdd=batch)
            if not add_tracks_reply:
                print(f'Failed to add batch {i//batch_size + 1} to playlist "{playlist_name}"')
                break
        
        processed_playlists.append((playlist_name, len(ND_track_ids), len(missing_tracks)))
        print(f'Added {len(ND_track_ids)} tracks to "{playlist_name}"')
    
    # Print summary
    print_summary(processed_playlists, skipped_playlists, all_missing_tracks)

def print_summary(processed_playlists, skipped_playlists, all_missing_tracks):
    """Print migration summary"""
    print('\n' + '='*60)
    print('MIGRATION SUMMARY')
    print('='*60)
    
    if processed_playlists:
        print(f'\nProcessed {len(processed_playlists)} playlists:')
        total_tracks = sum(tracks for _, tracks, _ in processed_playlists)
        total_missing = sum(missing for _, _, missing in processed_playlists)
        
        for name, tracks, missing in processed_playlists:
            status = f'{tracks} tracks'
            if missing:
                status += f' ({missing} missing)'
            print(f'  ✓ {name}: {status}')
        
        print(f'\nTotal tracks migrated: {total_tracks}')
        if total_missing:
            print(f'Total tracks missing: {total_missing}')
    
    if skipped_playlists:
        print(f'\nSkipped {len(skipped_playlists)} playlists:')
        for name in skipped_playlists:
            print(f'  - {name}')
    
    if all_missing_tracks:
        print(f'\nMISSING TRACKS DETAILS:')
        for playlist_name, missing_ids in all_missing_tracks.items():
            print(f'\n  {playlist_name} ({len(missing_ids)} missing):')
            for track_id in missing_ids[:5]:  # Show first 5
                print(f'    iTunes ID: {track_id}')
            if len(missing_ids) > 5:
                print(f'    ... and {len(missing_ids) - 5} more')
        print('\nNote: Missing tracks were likely skipped during the initial migration.')
    
    print('\nMigration complete!')

if __name__ == '__main__':
    main()
# This code is now handled in the process_playlists function



# This works to create a playlist.
'''Here is what it returns:

>>> serverReply = send_api_request('createPlaylist', name='my test playlist')

{'status': 'ok',
 'version': '1.16.1',
 'type': 'navidrome',
 'serverVersion': '0.48.0 (af5c2b5a)',
 'playlist': {'id': '371d5395-8462-4453-afb7-cebd2013eaf1',
  'name': 'my test playlist',
  'songCount': 0,
  'duration': 0,
  'public': False,
  'owner': 'usernam',
  'created': '2022-12-23T23:48:34.936169089Z',
  'changed': '2022-12-23T23:48:34.936171839Z'}}
  '''

# This works to add multiple songs at one time. Note that you can put multiple song IDs in a list and it works OK:
'''

updatingReply = send_api_request('updatePlaylist', playlistId='91866b80-1cf6-4ca3-8e59-acec4fd29282', songIdToAdd=['9b4f1e2a7cb79adbef220deac179c
    ...: 254', '7465599c97cdc84d347123c96b43899d', '14ef255126037deab2ab5380e974b11f'])

returns: 
{'status': 'ok',
 'version': '1.16.1',
 'type': 'navidrome',
 'serverVersion': '0.48.0 (af5c2b5a)'}
'''
