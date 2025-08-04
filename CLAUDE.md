# iTunes to Navidrome Migration Toolkit

## Project Overview
Python scripts to transfer iTunes library data (ratings, play counts, play dates, playlists) to Navidrome music server.

## Key Files
- `itunestoND.py` - Main migration script for song data
- `itunesPlaylistMigrator.py` - Playlist migration via Navidrome API
- `requirements.txt` - Python dependencies
- `data/` - Sample iTunes Library.xml and navidrome.db files

## Dependencies
Install with: `pip3 install -r requirements.txt`
- beautifulsoup4==4.11.1
- requests==2.28.1
- PyInputPlus==0.2.12
- lxml==4.9.2
- Other supporting libraries

## Usage
1. **Data Migration**: `python3 itunestoND.py`
   - Migrates ratings, play counts, last played dates
   - Direct SQLite database manipulation
   - Generates correlation file for playlists

2. **Playlist Migration**: `python3 itunesPlaylistMigrator.py`
   - Requires running Navidrome server
   - Uses Navidrome REST API
   - Interactive playlist selection

## Architecture
- XML parsing with BeautifulSoup/lxml
- SQLite database operations
- REST API integration with MD5 authentication
- File path correlation between systems

## Testing
No automated tests present. Manual verification required after migration.

## License
Public domain (Unlicense)