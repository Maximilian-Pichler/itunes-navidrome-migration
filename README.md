# iTunes to Navidrome Migration Toolkit

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Unlicense-green.svg)](LICENSE)

A Python toolkit for migrating iTunes library data (ratings, play counts, play dates, and playlists) to Navidrome music server.

## Features

- 🎵 **Complete Data Migration**: Transfer ratings, play counts, last played dates, and playlists
- 🔍 **Auto-Detection**: Automatically finds iTunes Library.xml and Navidrome database files
- ⚡ **Batch Processing**: Process all playlists at once or review individually
- 🖥️ **CLI Support**: Full command-line interface for automation
- 📊 **Detailed Reporting**: Comprehensive migration summaries with missing track details
- 🛡️ **Safe Operation**: Confirmation prompts and backup recommendations

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-repo/itunes-navidrome-migration.git
cd itunes-navidrome-migration

# Install dependencies
pip install -r requirements.txt

# Migrate ratings and play counts (auto-detects files)
python3 itunestoND.py

# Migrate playlists in batch mode
python3 itunesPlaylistMigrator.py --batch
```

## Installation

### Requirements

- Python 3.7+
- iTunes Library.xml file
- Navidrome server and database

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

## Usage

### Data Migration

Migrate song ratings, play counts, and last played dates:

```bash
# Basic usage with auto-detection
python3 itunestoND.py

# Skip confirmation prompt
python3 itunestoND.py --yes

# Specify file paths
python3 itunestoND.py --library ~/Music/iTunes/Library.xml --database ./navidrome.db

# View all options
python3 itunestoND.py --help
```

### Playlist Migration

Migrate iTunes playlists to Navidrome:

```bash
# Interactive mode (review each playlist)
python3 itunesPlaylistMigrator.py

# Preview playlists without processing
python3 itunesPlaylistMigrator.py --preview

# Batch mode (accept all playlists)
python3 itunesPlaylistMigrator.py --batch

# Full automation
python3 itunesPlaylistMigrator.py --batch \
  --server http://localhost:4533 \
  --username admin \
  --password mypassword

# View all options
python3 itunesPlaylistMigrator.py --help
```

## Migration Guide

### Prerequisites

1. **Backup your data** - Always work with backups until migration is verified
2. **Preserve file structure** - Keep the same directory structure between iTunes and Navidrome
3. **Set up Navidrome** - Ensure Navidrome has indexed your music files

### Step 1: Migrate Ratings and Play Data

1. **Stop Navidrome server**
2. **Copy database files** (`navidrome.db*`) to your working directory
3. **Run migration:**
   ```bash
   python3 itunestoND.py
   ```
4. **Replace database files** on your Navidrome server
5. **Start Navidrome** and verify the migration

### Step 2: Migrate Playlists

1. **Start Navidrome server**
2. **Ensure `IT_file_correlations.py`** exists (generated in Step 1)
3. **Choose migration approach:**
   - **Preview first:** `python3 itunesPlaylistMigrator.py --preview`
   - **Interactive:** `python3 itunesPlaylistMigrator.py`
   - **Batch:** `python3 itunesPlaylistMigrator.py --batch`

## Configuration

### Auto-Detection Paths

The scripts automatically search these locations:

**iTunes Library.xml:**
- Current directory
- `~/Music/iTunes/`
- `%USERPROFILE%\Music\iTunes\` (Windows)

**Navidrome Database:**
- Current directory
- `./data/`
- `~/.navidrome/`
- `/var/lib/navidrome/`

### Command-Line Options

#### `itunestoND.py`
```
--library PATH    Path to iTunes Library.xml file
--database PATH   Path to Navidrome database file  
--yes            Skip confirmation prompt
--help           Show help message
```

#### `itunesPlaylistMigrator.py`
```
--library PATH     Path to iTunes Library.xml file
--server URL       Navidrome server URL
--username USER    Navidrome username
--password PASS    Navidrome password
--batch           Accept all playlists automatically
--preview         Preview playlists without processing
--help            Show help message
```

## Examples

### Basic Migration
```bash
# Let the script find your files
python3 itunestoND.py
python3 itunesPlaylistMigrator.py
```

### Automated Migration
```bash
# Fully automated with explicit paths
python3 itunestoND.py --yes \
  --library ~/Music/iTunes/Library.xml \
  --database ~/navidrome/navidrome.db

python3 itunesPlaylistMigrator.py --batch \
  --library ~/Music/iTunes/Library.xml \
  --server http://localhost:4533 \
  --username admin
```

### Preview Mode
```bash
# See what playlists would be migrated
python3 itunesPlaylistMigrator.py --preview
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Files not found | Use `--library` and `--database` to specify paths |
| Permission denied | Check database file permissions |
| Missing tracks in playlists | Files may have been renamed or moved |
| Encoding errors | Ensure Library.xml uses UTF-8 encoding |

### Known Limitations

- **Smart playlists** are not migrated
- **Ratings without play data** won't transfer
- **Non-Latin characters** may not transfer correctly
- **File path changes** between iTunes and Navidrome break correlation

## Dependencies

- `beautifulsoup4` - XML parsing
- `requests` - HTTP API calls
- `PyInputPlus` - Enhanced input handling
- `lxml` - XML processing

See `requirements.txt` for version details.

## Testing

Tested with:
- **Python**: 3.7+
- **Navidrome**: v0.48.0+
- **Platforms**: Linux, macOS, Windows
- **iTunes**: Library.xml from iTunes on Windows/macOS

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is released into the public domain under the [Unlicense](LICENSE).

## Support

- 📧 **Issues**: [GitHub Issues](https://github.com/your-repo/itunes-navidrome-migration/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-repo/itunes-navidrome-migration/discussions)
- 🎵 **Navidrome**: [Official Discord](https://discord.gg/xh7j7yF)

## Acknowledgments

- [Navidrome](https://navidrome.org) developers for creating an excellent music server
- Community contributors and testers
- Original concept and implementation

---

⭐ **Found this helpful?** Give it a star and share with other music enthusiasts!