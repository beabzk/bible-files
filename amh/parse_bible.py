import sys
import json
import glob
import os
import re
import logging
from bs4 import BeautifulSoup

# Mapping of book abbreviations to (English Name, Amharic Name)
BOOK_MAPPINGS = {
    "gen": ("Genesis", "ዘፍጥረት"),
    "exo": ("Exodus", "ዘጸአት"),
    "lev": ("Leviticus", "ዘሌዋውያን"),
    "num": ("Numbers", "ዘኍልቍ"),
    "deu": ("Deuteronomy", "ዘዳግም"),
    "jos": ("Joshua", "መጽሐፈ ኢያሱ"),
    "jdg": ("Judges", "መጽሐፈ መሳፍንት"),
    "rut": ("Ruth", "መጽሐፈ ሩት"),
    "1sa": ("1 Samuel", "1ኛ ሳሙኤል"),
    "2sa": ("2 Samuel", "2ኛ ሳሙኤል"),
    "1ki": ("1 Kings", "1ኛ ነገሥት"),
    "2ki": ("2 Kings", "2ኛ ነገሥት"),
    "1ch": ("1 Chronicles", "1ኛ ዜና መዋዕል"),
    "2ch": ("2 Chronicles", "2ኛ ዜና መዋዕል"),
    "ezr": ("Ezra", "መጽሐፈ ዕዝራ"),
    "neh": ("Nehemiah", "መጽሐፈ ነህምያ"),
    "est": ("Esther", "መጽሐፈ አስቴር"),
    "job": ("Job", "መጽሐፈ ኢዮብ"),
    "psa": ("Psalms", "መዝሙረ ዳዊት"),
    "pro": ("Proverbs", "መጽሐፈ ምሳሌ"),
    "ecc": ("Ecclesiastes", "መጽሐፈ መክብብ"),
    "sos": ("Song of Solomon", "መኃልየ መኃልይ ዘሰሎሞን"),
    "isa": ("Isaiah", "ትንቢተ ኢሳይያስ"),
    "jer": ("Jeremiah", "ትንቢተ ኤርምያስ"),
    "lam": ("Lamentations", "ሰቆቃወ ኤርምያስ"),
    "eze": ("Ezekiel", "ትንቢተ ሕዝቅኤል"),
    "dan": ("Daniel", "ትንቢተ ዳንኤል"),
    "hos": ("Hosea", "ትንቢተ ሆሴዕ"),
    "joe": ("Joel", "ትንቢተ ኢዮኤል"),
    "amo": ("Amos", "ትንቢተ አሞጽ"),
    "oba": ("Obadiah", "ትንቢተ አብድዩ"),
    "jon": ("Jonah", "ትንቢተ ዮናስ"),
    "mic": ("Micah", "ትንቢተ ሚክያስ"),
    "nah": ("Nahum", "ትንቢተ ናሆም"),
    "hab": ("Habakkuk", "ትንቢተ ዕንባቆም"),
    "zep": ("Zephaniah", "ትንቢተ ሶፎንያስ"),
    "hag": ("Haggai", "ትንቢተ ሐጌ"),
    "zec": ("Zechariah", "ትንቢተ ዘካርያስ"),
    "mal": ("Malachi", "ትንቢተ ሚልክያስ"),
    "mat": ("Matthew", "የማቴዎስ ወንጌል"),
    "mar": ("Mark", "የማርቆስ ወንጌል"),
    "luk": ("Luke", "የሉቃስ ወንጌል"),
    "joh": ("John", "የዮሐንስ ወንጌል"),
    "act": ("Acts", "የሐዋርያት ሥራ"),
    "rom": ("Romans", "የሮሜ መልእክት"),
    "1co": ("1 Corinthians", "1ኛ ወደ ቆሮንቶስ ሰዎች"),
    "2co": ("2 Corinthians", "2ኛ ወደ ቆሮንቶስ ሰዎች"),
    "gal": ("Galatians", "የገላትያ መልእክት"),
    "eph": ("Ephesians", "የኤፌሶን መልእክት"),
    "php": ("Philippians", "የፊልጵስዩስ መልእክት"),
    "col": ("Colossians", "የቆላስይስ መልእክት"),
    "1th": ("1 Thessalonians", "1ኛ ወደ ተሰሎንቄ ሰዎች"),
    "2th": ("2 Thessalonians", "2ኛ ወደ ተሰሎንቄ ሰዎች"),
    "1ti": ("1 Timothy", "1ኛ ወደ ጢሞቴዎስ"),
    "2ti": ("2 Timothy", "2ኛ ወደ ጢሞቴዎስ"),
    "tit": ("Titus", "የቲቶ መልእክት"),
    "phi": ("Philemon", "የፊልሞና መልእክት"),
    "heb": ("Hebrews", "ወደ ዕብራውያን"),
    "jam": ("James", "የያዕቆብ መልእክት"),
    "1pe": ("1 Peter", "1ኛ የጴጥሮስ መልእክት"),
    "2pe": ("2 Peter", "2ኛ የጴጥሮስ መልእክት"),
    "1jo": ("1 John", "1ኛ የዮሐንስ መልእክት"),
    "2jo": ("2 John", "2ኛ የዮሐንስ መልእክት"),
    "3jo": ("3 John", "3ኛ የዮሐንስ መልእክት"),
    "jud": ("Jude", "የይሁዳ መልእክት"),
    "rev": ("Revelation", "የዮሐንስ ራእይ"),
}

def configure_logger(log_file, log_level=logging.INFO):
    """Configures the logger with a file handler and formatter.

    Args:
        log_file (str): The path to the log file.
        log_level (int): The logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: The configured logger.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # Create a file handler
    file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)
    return logger

def parse_title_from_toc(toc_file):
    """Parses the title of a book from a table of contents (TOC) file.

    Args:
        toc_file (str): The path to the TOC file.

    Returns:
        str: The title of the book, or "Unknown Book" if not found.
    """
    try:
        with open(toc_file, 'r', encoding='iso-8859-1') as f:
            soup = BeautifulSoup(f, 'html.parser')
            title_tag = soup.find('font', {'face': 'GF Zemen Unicode'})
            if title_tag:
                # Extract the text and remove the English name in parentheses
                title_text = title_tag.text.strip()
                title_text = title_text.split('(')[0].strip()
                return title_text
            else:
                logger.warning(f"Title tag not found in {toc_file}")
                return "Unknown Book"
    except Exception as e:
        logger.error(f"Error in parse_title_from_toc: {e}", exc_info=True)
        return "Unknown Book"

def parse_bible_html_no_main(toc_file, chapter_files, book_title_amharic):
    """Parses Bible HTML files when the main book file is missing, using TOC and chapter files.

    Args:
        toc_file (str): The path to the table of contents (TOC) file.
        chapter_files (list): A list of paths to the chapter files.
        book_title_amharic (str): The Amharic title of the book.

    Returns:
        str: A JSON string containing the parsed Bible data, or None if an error occurred.
    """
    chapters = []
    try:
        with open(toc_file, 'r', encoding='iso-8859-1') as f:
            soup = BeautifulSoup(f, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                if link['href'].startswith(os.path.splitext(os.path.basename(toc_file))[0].replace("_toc", "")):
                    chapter_num = link.text.strip().split(" ")[-1]
                    chapter_num = re.sub(r'\D', '', chapter_num)
                    chapters.append({
                        'chapter': int(chapter_num),
                        'verses': []
                    })
            logger.debug(f"Parsed chapter numbers from TOC: {chapters}")

        # Get English title from the toc file name
        book_title_english = os.path.splitext(os.path.basename(toc_file))[0].replace("_toc", "")
        logger.debug(f"Parsed English title: {book_title_english}")

        # Get Amharic title from mapping
        book_abbr = book_title_english.lower()
        if book_abbr in BOOK_MAPPINGS:
            book_title_english, book_title_amharic = BOOK_MAPPINGS[book_abbr]
            logger.debug(f"Using mapping for {book_abbr}: English='{book_title_english}', Amharic='{book_title_amharic}'")
        else:
            book_title_amharic = "Unknown Book"
            logger.warning(f"No mapping found for {book_abbr}, using default Amharic title.")


        for chapter_file in chapter_files:
            chapter_num = int(os.path.basename(chapter_file).split('-')[1].split('.')[0])
            with open(chapter_file, 'r', encoding='iso-8859-1') as f:
                soup = BeautifulSoup(f, 'html.parser')
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    font_tag = p.find('font', {'face': 'GF Zemen Unicode'})
                    if font_tag:
                        text = font_tag.text.strip()
                        parts = text.split(" ")
                        verse_numbers = parts[0].replace("&#4964;", "")
                        verse_numbers_list = verse_numbers.split("፤")
                        verse_numbers_list = [v for v in verse_numbers_list if v]  # Remove empty strings
                        if len(verse_numbers_list) > 1:
                            verse_numbers = "-".join(verse_numbers_list)
                        elif len(verse_numbers_list) == 1:
                            verse_numbers = verse_numbers_list[0]
                        verse_text = " ".join(parts[1:]).strip()

                        for chapter in chapters:
                            if chapter['chapter'] == chapter_num:
                                chapter['verses'].append({
                                    'verse': verse_numbers,
                                    'text': verse_text
                                })
                                logger.debug(f"Parsed verse: Chapter {chapter_num}, Verse {verse_numbers}: {verse_text}")
                                break
    except Exception as e:
        logger.error(f"Error in parse_bible_html_no_main: {e}", exc_info=True)
        return None

    logger.info(f"parse_bible_html_no_main - book_title_amharic: {book_title_amharic}")  # ADDED LOG
    return json.dumps({
        'book': book_title_english,
        'book_amharic': book_title_amharic,
        'chapters': chapters
    }, ensure_ascii=False, indent=2)

def parse_bible_html(toc_file, chapter_files, book_file):
    """Parses Bible HTML files and returns a JSON representation.

    Args:
        toc_file (str): The path to the table of contents (TOC) file.
        chapter_files (list): A list of paths to the chapter files.
        book_file (str): The path to the main book file.

    Returns:
        str: A JSON string containing the parsed Bible data, or None if an error occurred.
    """
    try:
        # Parse book title
        with open(book_file, 'r', encoding='iso-8859-1') as f:
            soup = BeautifulSoup(f, 'html.parser')

            # English title from file name
            book_title_english = os.path.splitext(os.path.basename(book_file))[0]
            logger.debug(f"Parsed English title: {book_title_english}")

            # Amharic title - USE MAPPING
            book_abbr = book_title_english.lower()
            if book_abbr in BOOK_MAPPINGS:
                book_title_english, book_title_amharic = BOOK_MAPPINGS[book_abbr]
                logger.debug(f"Using mapping for {book_abbr}: English='{book_title_english}', Amharic='{book_title_amharic}'")
            else:
                book_title_amharic = "Unknown Book"  # Default value
                logger.warning(f"No mapping found for {book_abbr}, using default Amharic title.")


        # Parse chapter information
        chapters = []
        with open(toc_file, 'r', encoding='iso-8859-1') as f:
            soup = BeautifulSoup(f, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                if link['href'].startswith(os.path.splitext(os.path.basename(book_file))[0]):
                  chapter_num = link.text.strip().split(" ")[-1]
                  chapter_num = re.sub(r'\D', '', chapter_num)
                  chapters.append({
                      'chapter': int(chapter_num),
                      'verses': []
                  })
            logger.debug(f"Parsed chapter numbers from TOC: {chapters}")

        # Parse verse content of each chapter
        for chapter_file in chapter_files:
            chapter_num = int(os.path.basename(chapter_file).split('-')[1].split('.')[0])
            with open(chapter_file, 'r', encoding='iso-8859-1') as f:
                soup = BeautifulSoup(f, 'html.parser')
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    font_tag = p.find('font', {'face': 'GF Zemen Unicode'})
                    if font_tag:
                        text = font_tag.text.strip()
                        parts = text.split(" ")
                        verse_numbers = parts[0].replace("&#4964;", "")
                        verse_numbers_list = verse_numbers.split("፤")
                        verse_numbers_list = [v for v in verse_numbers_list if v]  # Remove empty strings
                        if len(verse_numbers_list) > 1:
                            verse_numbers = "-".join(verse_numbers_list)
                        elif len(verse_numbers_list) == 1:
                            verse_numbers = verse_numbers_list[0]
                        verse_text = " ".join(parts[1:]).strip()

                        for chapter in chapters:
                            if chapter['chapter'] == chapter_num:
                                chapter['verses'].append({
                                    'verse': verse_numbers,
                                    'text': verse_text
                                })
                                logger.debug(f"Parsed verse: Chapter {chapter_num}, Verse {verse_numbers}: {verse_text}")
                                break
    except Exception as e:
        logger.error(f"Error in parse_bible_html: {e}", exc_info=True)
        return None

    logger.info(f"parse_bible_html - book_title_amharic: {book_title_amharic}")  # ADDED LOG
    return json.dumps({
        'book': book_title_english,
        'book_amharic': book_title_amharic,
        'chapters': chapters
    }, ensure_ascii=False, indent=2)

def parse_from_chapter_files(book_name, chapter_files):
    """Parses Bible data from chapter files when TOC and main files are missing.

    Args:
        book_name (str): The name of the book (used for English title).
        chapter_files (list): A list of paths to the chapter files.

    Returns:
        str: A JSON string containing the parsed Bible data, or None if an error occurred.
    """
    chapters = []

    try:
        # Use book_name directly
        book_title_english = book_name
        logger.debug(f"Parsed English title: {book_title_english}")

        # Get Amharic title from mapping
        book_abbr = book_name.lower()
        if book_abbr in BOOK_MAPPINGS:
            book_title_english, book_title_amharic = BOOK_MAPPINGS[book_abbr]
            logger.debug(f"Using mapping for {book_abbr}: English='{book_title_english}', Amharic='{book_title_amharic}'")

        else:
            book_title_amharic = "Unknown Book"
            logger.warning(f"No mapping found for {book_abbr}, using default Amharic title.")

        for chapter_file in chapter_files:
            chapter_num = int(os.path.basename(chapter_file).split('-')[1].split('.')[0])
            with open(chapter_file, 'r', encoding='iso-8859-1') as f:
                soup = BeautifulSoup(f, 'html.parser')
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    font_tag = p.find('font', {'face': 'GF Zemen Unicode'})
                    if font_tag:
                        text = font_tag.text.strip()
                        parts = text.split(" ")
                        verse_numbers = parts[0].replace("&#4964;", "")
                        verse_numbers_list = verse_numbers.split("፤")
                        verse_numbers_list = [v for v in verse_numbers_list if v]  # Remove empty strings
                        if len(verse_numbers_list) > 1:
                            verse_numbers = "-".join(verse_numbers_list)
                        elif len(verse_numbers_list) == 1:
                            verse_numbers = verse_numbers_list[0]
                        verse_text = " ".join(parts[1:]).strip()

                        chapters.append({
                            'chapter': chapter_num,
                            'verses': [{'verse': verse_numbers, 'text': verse_text}]
                        })
                    chapters.sort(key=lambda x: x['chapter'])

    except Exception as e:
        logger.error(f"Error in parse_from_chapter_files: {e}", exc_info=True)
        return None

    logger.info(f"parse_from_chapter_files - book_title_amharic: {book_title_amharic}")  # ADDED LOG
    return json.dumps({
        'book': book_title_english,
        'book_amharic': book_title_amharic,
        'chapters': chapters
    }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # Configure logging
    logger = configure_logger('bible_parser.log', log_level=logging.INFO)
    logger.info("Starting Bible parsing script")

    book_abbreviations = ["gen", "exo", "lev", "num", "deu", "jos", "jdg", "rut", "1sa", "2sa", "1ki", "2ki", "1ch", "2ch", "ezr", "neh", "est", "job",
                          "psa", "pro", "ecc", "sos", "isa", "jer", "lam", "eze", "dan", "hos", "joe", "amo", "oba", "jon", "mic", "nah", "hab", "zep",
                          "hag", "zec", "mal", "mat", "mar", "luk", "joh", "act", "rom", "1co", "2co", "gal", "eph", "php", "col", "1th", "2th", "1ti",
                          "2ti", "tit", "phi", "heb", "jam", "1pe", "2pe", "1jo", "2jo", "3jo", "jud", "rev"]

    processed_books = set() # Moved to here

    # REVISED LOGIC
    htm_files = []
    for f in glob.glob("source/*.htm"):
        filename = os.path.basename(f).replace('.htm', '').lower()

        if filename in book_abbreviations or re.match(r"^[0-9]?[a-z]+$", filename):
            htm_files.append(f)

            # Get book abbreviation and mapping
            book_abbr = filename
            if book_abbr in BOOK_MAPPINGS:
                book_name, book_amharic = BOOK_MAPPINGS[book_abbr]
            else:
                book_name = book_abbr # Use abbreviation if no mapping
                logger.warning(f"No mapping found for {book_abbr}, using abbreviation.")

            toc_file = f"source/{book_abbr}_toc.htm"
            if os.path.exists(toc_file):
                if os.path.exists(f"source/{book_abbr}.htm"):
                    chapter_files = sorted(glob.glob(f"source/{book_abbr}-[0-9]*.htm"))
                    if chapter_files:
                        logger.info(f"Processing {book_name} with main and TOC files...")
                        json_output = parse_bible_html(toc_file, chapter_files, f"source/{book_abbr}.htm")
                        if json_output is None:
                            logger.error(f"Failed to parse {book_name}.")
                        else:
                            output_file = f"json/{book_abbr}.json" # Always use abbreviation for filename

                            # Check if directory exists, create if necessary
                            if not os.path.exists("json/"):
                                os.makedirs("json/")
                                logger.info(f"Created directory: json/")
                            # Check if file exists
                            if not os.path.exists(output_file):
                                with open(output_file, 'w') as fp:
                                  pass # empty file
                                logger.info(f"Created empty file {output_file}")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(json_output)
                            logger.info(f"Successfully created {output_file}")
                            processed_books.add(book_abbr)
                    else:
                        logger.warning(f"Skipping {book_name} due to missing chapter files.")

                else:
                    # Handle missing main .htm file
                    logger.info(f"Main HTM file missing for {book_name}, attempting to parse from TOC and chapter files.")
                    chapter_files = sorted(glob.glob(f"source/{book_abbr}-[0-9]*.htm"))
                    if chapter_files:
                        json_output = parse_bible_html_no_main(toc_file, chapter_files, book_name)  # Pass book_name
                        if json_output is None:
                            logger.error(f"Failed to parse {book_name} from TOC and chapter files.")
                        else:
                            output_file = f"json/{book_abbr}.json"  # Always use abbreviation for filename

                            # Check if directory exists, create if necessary
                            if not os.path.exists("json/"):
                                os.makedirs("json/")
                                logger.info(f"Created directory: json/")
                            # Check if file exists
                            if not os.path.exists(output_file):
                                with open(output_file, 'w') as fp:
                                  pass # empty file
                                logger.info(f"Created empty file {output_file}")
                            with open(output_file, 'w', encoding='utf-8') as f:
                                f.write(json_output)
                            logger.info(f"Successfully created {output_file} (from TOC and chapter files)")
                            processed_books.add(book_abbr)
                    else:
                        logger.warning(f"Skipping {book_name} due to missing main HTM and chapter files.")

            else:
                # Handle missing toc file, but existing chapter files
                chapter_files = sorted(glob.glob(f"source/{book_abbr}-[0-9]*.htm"))
                if chapter_files:
                    logger.info(f"TOC file missing for {book_name}, attempting to parse from chapter files.")
                    json_output = parse_from_chapter_files(book_abbr, chapter_files) # Use book_abbr
                    if json_output:
                        output_file = f"json/{book_abbr}.json" # Always use abbreviation for filename

                        # Check if directory exists, create if necessary
                        if not os.path.exists("json/"):
                            os.makedirs("json/")
                            logger.info(f"Created directory: json/")

                        # Check if file exists
                        if not os.path.exists(output_file):
                            with open(output_file, 'w') as fp:
                                pass # empty file
                            logger.info(f"Created empty file {output_file}")
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(json_output)
                        logger.info(f"Successfully created {output_file} (from chapter files only)")
                        processed_books.add(book_abbr)
                    else:
                        logger.error(f"Failed to parse {book_name} from chapter files.")

                else:
                    logger.warning(f"Skipping {book_name} due to missing toc file and chapter files.")
        else:
            logger.debug(f"Filename {filename} skipped")

    logger.debug(f"processed_books: {processed_books}")

    # Check for books that were completely missed
    for book_abbr in book_abbreviations:
        if book_abbr not in processed_books:
            chapter_files = sorted(glob.glob(f"source/{book_abbr}-[0-9]*.htm"))
            if chapter_files:  # if chapter files exist
                logger.info(f"Attempting to parse {book_abbr} from chapter files (no main or TOC file).")

                # Use mapping for book name
                if book_abbr in BOOK_MAPPINGS:
                    book_name, _ = BOOK_MAPPINGS[book_abbr]
                    logger.info(f"Using mapping for output file name: {book_name} (from {book_abbr})")
                else:
                    book_name = book_abbr # Use abbreviation directly
                    logger.warning(f"No mapping found for {book_abbr}, using abbreviation for output file.")

                json_output = parse_from_chapter_files(book_abbr, chapter_files) # Use book_abbr
                if json_output:
                    output_file = f"json/{book_abbr}.json"  # Always use abbreviation for filename

                    # Check if directory exists, create if necessary
                    if not os.path.exists("json/"):
                        os.makedirs("json/")
                        logger.info(f"Created directory: json/")

                    # Check if file exists
                    if not os.path.exists(output_file):
                        with open(output_file, 'w') as fp:
                            pass # empty file
                        logger.info(f"Created empty file {output_file}")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(json_output)
                    logger.info(f"Successfully created {output_file} (from chapter files only)")
                    processed_books.add(book_abbr)
                else:
                    logger.error(f"Failed to parse {book_abbr} even from chapter files.")

    logger.info("Finished Bible parsing script")
