import cPickle as pickle
from scrapper import Song
import re
import numpy as np

# copy of sklearn's dataset object
class Bunch(dict):
    """Container object for datasets: dictionary-like object that
       exposes its keys as attributes."""

    def __init__(self, **kwargs):
        dict.__init__(self, kwargs)
        self.__dict__ = self

def clean_lyrics(lyrics):
    """
    Regex:
        - \[.+\]     removes anything within brackets
        - Hook:     matches Hook:
        - \(x\d*\)   matches things like (x8) for repeated lines
    """
    lyrics = lyrics.encode('ascii', 'ignore')
    return re.sub(r"\[.+\]|Hook:|\(x\d*\)", "", lyrics)

def split_verses(lyrics):
    """
    Pretty non-pythonic way to split each song into it's verses
    """
    verses, verse = [], ""

    def seperator(verse):
        if verse:
            return ". "
        else:
            return ""

    for i, line in enumerate(lyrics.splitlines()):
        if not line: # if we find a blank line, start of new verse
            if verse: # if the previous verse is not empty
                verses.append(verse)
            verse = ""
        else:
            verse = verse + seperator(verse) + line 

        # dumb way to check if we have a trailing line
        if i == len(lyrics.splitlines())-1 and line:
            verse = verse + seperator(verse) + line
            verses.append(verse)

    return verses

def load_songs(artist='drake', album_list=None, shuffle=False):
    """
    Load the songs by verse into a Bunch object
    Note:
        You can map a verse to it's song or album by matching
        the indices of the underlying data.album or data.song
        array
    """
    songs = pickle.load(open(artist+'.pkl'))
    data, titles, albums = list(), list(), list()

    # filter by album if necessary
    if album_list:
        songs = [song for song in songs if song.album in album_list]
    
    # clean the song lyrics / split into verses
    for song in songs:
        lyrics = clean_lyrics(song.lyrics)
        verses = split_verses(lyrics)

        # add to data sets
        data.extend(verses)
        albums.extend([song.album for verse in verses])
        titles.extend([song.title for verse in verses])

    # convert to numpy arrays
    data = np.asarray(data)
    albums = np.asarray(albums)
    titles = np.asarray(titles)
    data = Bunch(data=data, album=albums, song=titles)

    if shuffle:
        indices = np.arange(data.data.shape[0])
        np.random.shuffle(indices)
        data.data = data.data[indices]
        data.album = data.album[indices]
        data.song = data.song[indices]

    return data

def print_verses(data):
    for i, verse in enumerate(data.data):
        print("Verse #{0}: {1}\n".format(i, verse)) 
    
if __name__ == '__main__':  
    albums = ["Take Care", "If You're Reading This It's Too Late"]
    dataset = load_songs(artist='drake', album_list=albums, shuffle=True)
    print_verses(dataset) 
