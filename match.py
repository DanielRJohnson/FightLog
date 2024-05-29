import re

class Match:
    """ 
    A full representation of a match, which is a 
    chapter of a YouTube video belonging to some channel.
    """

    def __init__(self, vid: dict, chapter: dict, game: str):
        self.game = game
        self.channel_id = vid["playlist_id"].replace("UU", "UC")
        self.channel_name = vid["uploader_id"]
        self.video_id = vid["id"]
        self.video_title = vid["title"]
        self.video_date = vid["upload_date"]
        self.chapter_name = chapter["title"]
        self.chapter_begin = int(chapter["start_time"])
        self.chapter_end = int(chapter["end_time"])
        self.p1_name, self.p1_char, self.p2_name, self.p2_char = \
            self._extract_names_and_chars_from_chapter(chapter)
        self.tuple = (self.game, self.channel_id, self.channel_name, self.video_id,
                        self.video_title, self.video_date, self.chapter_name, self.chapter_begin, 
                        self.chapter_end, self.p1_name, self.p1_char, self.p2_name, self.p2_char)


    @staticmethod
    def _extract_names_and_chars_from_chapter(chapter: dict) -> tuple[str, str, str, str]:
        """ Given a chapter, return the names and characters for p1 and p2. """
        # helper functions
        strip_all = lambda strings: [s.strip() for s in strings]
        remove_whitespace_and_lower_all = lambda strings: ["".join(s.split()).lower() for s in strings]
        split_player = lambda s: s.split(")")[0].split("(", maxsplit=1) if "(" in s and ")" in s else [s, "Not Provided"]
        take_first_char = lambda s: re.split(r"[ \t,/&]+", s)[0]

        # split chapter title into names and characters, normalize to lower case with no whitespace, and take first character
        p1, p2 = strip_all(re.split(r"vs.|vs", chapter["title"], maxsplit=1))
        p1_name, p1_char = remove_whitespace_and_lower_all(split_player(p1))
        p1_char = take_first_char(p1_char)
        p2_name, p2_char = remove_whitespace_and_lower_all(split_player(p2))
        p2_char = take_first_char(p2_char)

        return p1_name, p1_char, p2_name, p2_char


    def __iter__(self):
        """allow conversion to list, tuple, etc."""
        for field in self.tuple:
            yield (field)
