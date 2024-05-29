# 📒 FightLog

## *Never go digging through descriptions again.*

FightLog is a tool for finding, searching, and filtering fighting game tournament matches pulled directly from YouTube videos.

FightLog allows you to:
* View and choose from a large set of automatically updated tournament matches.
* Filter by character or even by character matchup.
* Filter by player.
* Filter by channel.
* Filter by date.

## 10-Second Demo

<p align="center">
  <img src="https://github.com/DanielRJohnson/FightLog/assets/39017265/9ab27aeb-e6b7-450c-8f3d-d3bf59269e50" alt="FightLog Demo Gif"/>
</p>

## Brief Technical Description

The critical pieces of information that we gather are the chapter names of a YouTube video. For channels that use them, it tells us which players played, which characters they played, and when in the video they played. 

With this in mind, FightLog works as follows:
* `search_list.csv` outlines which channels to search, what regex to match videos with, etc.
* Every so often, the `update_database.py` script is ran to scrape information from matched videos like chapters, video date, etc.
* The streamlit frontend (in `fightlog.py`) does some data cleaning and preparation like character name typo correction and YouTube URL creation before the data is shown to the user.

This process was designed to be as simple as possible while still giving something very useful to the fighting game community.

## Limitations
* Single-match videos are not currently supported. (e.g. "Evo Japan 2024: TEKKEN 8 2024 Grandfinals | Lowhigh vs Chikurin")
* Spoiler prevention inhibits us from parsing some important matches. (e.g. "1:36:54 Grand Finals")
* Videos without chapters give us nothing. (e.g. "TEKKEN 8 Top 6, Evo Japan 2024 Day 3")
* Only Tekken 8, Street Fighter 6, Guilty Gear Strive, and Granblue Fantasy Versus Rising are currently supported.

## Appreciate this tool?
<a href='https://ko-fi.com/Y8Y8YM9JW' style='text-align: center' target='_blank'>
    <img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=3' border='0' alt='Buy Me a Coffee at ko-fi.com' />
</a>
