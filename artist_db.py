"""Utility functions for managing my Simplenote artist database."""
import os
import time
import logging
import getpass

import simplenote

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("{levelname}: {message}", style="{"))
logger.addHandler(handler)

NOTE_TITLES = {
    "artists": "# Danbooru Artists",
    "vips": "# Danbooru VIPs",
}
TAGS = ["danbooru"]


def get_simplenote(attempts=5):
    """Attempt to authenticate and return a Simplenote instance."""
    username = input("Username: ")
    try:
        password = os.environ["SN_PSWD"]
    except KeyError as exception:
        logger.debug(exception)
        logger.info(
            "Consider saving the password in an environmental variable as "
            "SN_PSWD.")
        for _ in range(attempts):
            password = getpass.getpass()
            s_note = simplenote.Simplenote(username, password)
            try:
                s_note.authenticate(username, password)
            # Beetlejuice, Beetlejuice, Beetlejuice
            except simplenote.simplenote.SimplenoteLoginFailed as exception:
                logger.debug(exception)
                print("Incorrect password.")
            else:
                return s_note
        raise ValueError("Too many incorrect password attempts.")


def add_artist_notes(s_note):
    """Add semi-empty artist and VIP notes to the database."""
    artist_notes = {
        "artists": {
            "content": NOTE_TITLES["artists"],
            "tags": TAGS,
        },
        "vips": {
            "content": NOTE_TITLES["vips"],
            "tags": TAGS,
        },
    }
    s_note.add_note(artist_notes["artists"])
    s_note.add_note(artist_notes["vips"])


def get_artist_notes(s_note, attempts=5):
    """Return a dict of artist and VIP notes."""
    artist_notes = {
        "artists": None,
        "vips": None,
    }
    FAIL = -1
    SimplenoteAPIError = OSError(
        "Failed to access API - is Internet available?")

    logger.info("Getting notes list...")
    print("Please wait...")
    for _ in range(attempts):
        try:
            (notes, status) = s_note.get_note_list(tags=TAGS)
        except simplenote.simplenote.SimplenoteLoginFailed as exception:
            logger.debug(exception)
        else:
            break
    else:
        raise ValueError("Failed to get notes too many times.")
    if status == FAIL:
        raise SimplenoteAPIError

    for note in notes:
        (full_note, status) = s_note.get_note(note["key"])
        if status == FAIL:
            raise SimplenoteAPIError
        note_title = full_note["content"].split("\n")[0]
        logger.debug(f"note_title = {repr(note_title)}")

        if note_title == NOTE_TITLES["artists"]:
            logger.info(f"Getting full {NOTE_TITLES['artists']} note...")
            (artist_notes["artists"], status) = s_note.get_note(note["key"])
            logger.debug(
                "artist_notes['artists']['content'] = "
                f"{repr(artist_notes['artists']['content'])}")
        elif note_title == NOTE_TITLES["vips"]:
            logger.info(f"Getting full {NOTE_TITLES['vips']} note...")
            (artist_notes["vips"], status) = s_note.get_note(note["key"])
            logger.debug(
                "artist_notes['vips']['content'] = "
                f"{repr(artist_notes['vips']['content'])}")
        if status == FAIL:
            raise SimplenoteAPIError
        if artist_notes["artists"] and artist_notes["vips"]:
            return artist_notes
    else:
        add_artist_notes(s_note)


def update_simplenote(s_note, artist_notes, original_notes):
    """Write missing artists to Simplenote."""
    script_directory = os.path.dirname(os.path.realpath(__file__))
    paths = {
        "artists": os.path.join(script_directory, "artists.txt"),
        "vips": os.path.join(script_directory, "vips.txt"),
    }
    is_modified = {
        "artists": artist_notes["artists"] != original_notes["artists"],
        "vips": artist_notes["vips"] != original_notes["vips"],
    }

    if any(is_modified.values()):
        print("Please wait...")

    if is_modified["artists"]:
        artist_notes["artists"]["modifydate"] = time.time()
        logger.info("Backing up artist database...")
        with open(paths["artists"], "w") as artists_file:
            artists_file.write(artist_notes["artists"]["content"])
        logger.info("Writing changes to artist database...")
        s_note.update_note(artist_notes["artists"])

    if is_modified["vips"]:
        artist_notes["vips"]["modifydate"] = time.time()
        logger.info("Backing up VIP database...")
        with open(paths["vips"], "w") as vips_file:
            vips_file.write(artist_notes["vips"]["content"])
        logger.info("Writing changes to VIP database...")
        s_note.update_note(artist_notes["vips"])

