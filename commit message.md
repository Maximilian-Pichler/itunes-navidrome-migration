Root Cause

  The issue is Unicode normalization mismatch:

  1. iTunes XML: Uses NFD (decomposed) form - ü stored as u + combining diaeresis (%CC%88)
  2. Python's unquote(): Converts to NFD Unicode - u + ¨
  3. Navidrome database: Stores paths in NFC (composed) form - ü as single character

  When the script searches for the NFD path in the NFC database, no matches are found.


  ⎿ Fix Unicode Normalization Issue in itunestoND.py

    Problem: Script fails to match file paths containing special characters (umlauts, accents) because iTunes XML uses NFD 
    (decomposed) Unicode while Navidrome database uses NFC (composed) Unicode.

    Solution:
    1. Add Unicode normalization import: import unicodedata to the imports
    2. Normalize path after URL decoding: Convert the path from NFD to NFC form using unicodedata.normalize('NFC', song_path)
     
    3. Apply normalization in the path processing logic: After unquote() and before database lookup

    Changes needed:
    - Add unicodedata import at top of file
    - Modify path processing in the main loop (around line 110-114) to normalize Unicode after URL decoding
    - This will ensure paths with special characters like ü, ä, ö, é match correctly between iTunes XML and Navidrome database

    Expected result: Files with special characters will successfully match and have their play counts, ratings, and play dates migrated.