import pandas as pd
from datetime import datetime
from json import load
import streamlit as st
from thefuzz import process

def get_all_games():
    """ Retrieves a list of all games present in the database. """
    conn = st.connection("matches_db", type="sql")
    games = conn.query("SELECT DISTINCT Game FROM Matches;")
    return list(games["Game"])


def get_match_data(game_filter):
    """ Retrieves all match data from the sqlite database and does basic feature creation and filtering. """
    conn = st.connection("matches_db", type="sql")
    command = f'SELECT * FROM Matches WHERE game="{game_filter}"'
    matches = conn.query(command)

    matches["VideoDate"] = pd.to_datetime(matches["VideoDate"]).dt.date
    # the correct link with timecode is youtube.com/watch?v=<video_id>&t=<time_seconds>
    matches["Link"] = "https://youtube.com/watch?v=" + matches["VideoId"] + "&t=" + matches["ChapterBegin"].astype(str)

    # only show these columns in this order
    return matches


def clean_character_name(dirty_name, correct_character_names):
    """ For some character name with possible typos, try to match it to a correct name. """
    if dirty_name == "":
        return "Not Provided", 0
    prediction, confidence = process.extractOne(dirty_name, correct_character_names)
    return (prediction if confidence >= 70 else "Not Provided"), confidence


def filter_match_data(matches, char_filter, player_filter, channel_filter, date_filter):
    """ Filters matches based on character, player, channel, and date. """
    if len(char_filter) == 2: # filter by one exact matchup
        matches = matches.query("p1Character in @char_filter and p2Character in @char_filter and p1Character != p2Character")
    elif len(char_filter) == 1: # filter by only one character
        matches = matches.query("p1Character in @char_filter or p2Character in @char_filter")

    if len(player_filter) == 2: # filter by one exact player matchup
        matches = matches.query("p1Name in @player_filter and p2Name in @player_filter")
    elif len(player_filter) == 1: # filter by only one player
        matches = matches.query("p1Name in @player_filter or p2Name in @player_filter")

    if len(channel_filter) > 0: # filter by any number of channels
        matches = matches.query("ChannelName in @channel_filter")

    if len(date_filter) == 2: # filter by date range
        matches = matches[(matches["VideoDate"] > date_filter[0]) & (matches["VideoDate"] < date_filter[1])]

    return matches
    

def create_page():
    """ Defines the content of the page imperatively. """
    st.set_page_config(
        page_title="FightLog",
        page_icon="📒"
    )

    st.markdown("# 📒 FightLog")
    st.markdown("##### *Never go digging through descriptions again.*")

    # create radio buttons to filter by game
    all_games = sorted(get_all_games(), reverse=True)
    game_filter = st.radio("Select Game", all_games, horizontal=True, index=all_games.index("TEKKEN 8"))

    # get all matches of the chosen game
    matches = get_match_data(game_filter)

    # use a set of predefined character names to correct typos or other spellings
    # for instance "Alisa Bosconovitch" should be mapped to "Alisa"
    with open("character_lists.json") as f:
        correct_character_names = load(f)[game_filter]

    # thefuzz library for fuzzy matching
    clean_name = lambda s: clean_character_name(s, correct_character_names)
    matches["p1Character"], matches["p1CharacterConfidence"] = zip(*matches["p1Character"].apply(clean_name))
    matches["p2Character"], matches["p2CharacterConfidence"] = zip(*matches["p2Character"].apply(clean_name))

    # split page into two columns
    col1, col2 = st.columns(2)

    # create a multiselect dropdown to filter by character
    all_chars = sorted(pd.concat([matches["p1Character"], matches["p2Character"]]).unique())
    char_filter = col1.multiselect("Characters", all_chars, [], max_selections=2)

    # create a multiselect dropdown to filter by player
    all_players = sorted(pd.concat([matches["p1Name"], matches["p2Name"]]).unique())
    player_filter = col2.multiselect("Players", all_players, [], max_selections=2)

    # create a multiselect dropdown to filter by channel
    all_channels = sorted(matches["ChannelName"].unique())
    channel_filter = col1.multiselect("Channels", all_channels, [])

    # create a date input to filter by a range of dates
    date_filter = col2.date_input("Date Range", (matches["VideoDate"].min(), datetime.now()), format="MM/DD/YYYY")

    # actually filter the matches based on previously defined inputs
    filtered_matches = filter_match_data(matches, char_filter, player_filter, channel_filter, date_filter)
    
    st.write(f"{len(filtered_matches):,} matches shown, with a most recent match on {filtered_matches['VideoDate'].max()}.")

    # show the resulting dataframe with some chosen columns
    chosen_columns = ["p1Name", "p1Character", "p2Name", "p2Character", 
                      "Link", "VideoDate", "ChannelName", "VideoTitle", 
                      "ChapterName", "p1CharacterConfidence", "p2CharacterConfidence"]

    st.dataframe(
        filtered_matches[chosen_columns], 
        column_config={
            "Link": st.column_config.LinkColumn("Link to Match")
        }, 
        hide_index=True
    )

    # add my ko-fi link ;)
    st.markdown("""
                <a href='https://ko-fi.com/Y8Y8YM9JW' style='text-align: center' target='_blank'>
                <img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=3' 
                border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
                """, unsafe_allow_html=True)


if __name__ == "__main__":
    create_page()