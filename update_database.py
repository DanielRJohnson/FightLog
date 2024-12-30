import os
from multiprocessing import Pool
import yt_dlp
import sqlite3
from pandas import read_csv

from match import Match


def scrape_videos(channel_id: str, title_regex: str) -> list[dict]:
    """ Search a YouTube channel for all videos matching a regex and return them. """
    opts = {"ignoreerrors": True, "matchtitle": title_regex}
    with yt_dlp.YoutubeDL(opts) as ydl:
        uploads_playlist_id = channel_id.replace(
            "UC", "UU")  # UC is channel, UU is uploads
        playd = ydl.extract_info(uploads_playlist_id, download=False)
    return playd["entries"]


def update_database(videos: list, game: str, conn: sqlite3.Connection) -> None:
    """ Given a list of videos, extract match info and update the database. """
    for vid in videos:
        if vid is None:
            continue
        for chapter in vid["chapters"] if vid["chapters"] else []:
            if "vs" not in chapter["title"]:
                continue

            match = Match(vid, chapter, game)
            insert_match_into_database(match, conn)


def insert_match_into_database(match: Match, conn: sqlite3.Connection) -> None:
    """ Given a Match object, insert it into a sqlite database. """
    cur = conn.cursor()
    cur.execute("BEGIN TRANSACTION;")
    # imagine getting SQL injectioned from a youtube description. Surely not, right?
    command = """INSERT OR IGNORE INTO Matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
    try:
        cur.execute(command, tuple(match))
        cur.execute("COMMIT TRANSACTION;")
    except sqlite3.Error as e:
        print(e)
        cur.execute("ROLLBACK TRANSACTION;")


def process_search(row: list, conn: sqlite3.Connection) -> None:
    """ For one search defined in search_list.csv find each video and update the database. """
    videos = scrape_videos(row["channel_id"], row["channel_search_regex"])
    update_database(videos, row["game"], conn)


if __name__ == '__main__':
    # list of channels to search, what to search for, etc.
    search_list = read_csv("search_list.csv")

    with sqlite3.connect("matches.db") as conn:
        # multiprocessing pool likes only one argument
        def process_search_partial(r):
            process_search(r, conn)

        # for each search, update the database
        n_workers = min(len(search_list), len(
            os.sched_getaffinity(0)))  # max procs needed
        with Pool(n_workers) as pool:
            pool.map(process_search_partial, [
                     row for _, row in search_list.iterrows()])
