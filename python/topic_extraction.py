import cPickle as pickle
from scrapper import Song
import re
import numpy as np

# lets create a data object: split each song by verse
class SongData(object): 
    def __init__(self, album_list=None):
        self.albums = [] if not album_list else album_list
        self.data = []

    def add(self, songs):
        for song in songs:
            if song.album in self.albums:
                lyrics = self.clean_lyrics(song.lyrics) 
                self.data.extend(self.split_verses(lyrics))
    
    def print_verses(self):
        for i, verse in enumerate(self.data):
            print("Verse #{0}: {1}\n".format(i, verse)) 

    def split_verses(self, lyrics):
        """
        Pretty non-pythonic way to split each song into it's verses
        """
        verses, verse = [], ""
        for i, line in enumerate(lyrics.splitlines()):
            if not line: # if we find a blank line, start of new verse
                if verse: # if the previous verse is not empty
                    verses.append(verse)
                verse = ""
            else:
                if verse:
                    seperator = ". "
                else:
                    seperator = "" 
                verse = verse + seperator + line
            
            # dumb way to check if we have a trailing line
            if i == len(lyrics.splitlines())-1 and line:
                if verse:
                    verse = verse + ". " + line
                else:
                    verse = verse + "" + line
                verses.append(verse)
        return verses

    def clean_lyrics(self, lyrics):
        """
        Regex:
            - \[.\]     removes anything within brackets
            - Hook:     matches Hook:
            - \(x\d\)   matches things like (x8) for repeated lines
        """
        lyrics = lyrics.encode('ascii', 'ignore')
        return re.sub(r"\[.+\]|Hook:|\(x\d\)", "", lyrics)

if __name__ == '__main__':  
    albums = ["Take Care", "If You're Reading This It's Too Late"]
    songs = pickle.load(open('drake.pkl'))
    
    dataset = SongData(album_list=albums)
    dataset.add(songs)
    dataset.print_verses()

    data = np.array(dataset.data)
