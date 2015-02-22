import requests
from bs4 import BeautifulSoup
from collections import namedtuple
import json
import cPickle as pickle
import pymongo

# Object for storing song data
Song = namedtuple('Song', ['album', 'title', 'lyrics'])

def get_soup(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36'})
    return BeautifulSoup(r.text, 'lxml')

def scrap_rapgenius(artist):
    """
    Get all of an artist's songs page on rapgenius
    """
    
    BASE_URL = 'http://genius.com' 
    url = BASE_URL + '/artists/' + artist
    soup = get_soup(url)

    songs = []
    for album_link in soup.select('div.artist_sidebar > ul.album_list > li > a'):
        album_title = album_link.get_text()
        album_url =  BASE_URL + album_link.get('href')
        album_soup = get_soup(album_url)

        # loop through songs in album
        for song_link in album_soup.select('div.album_tracklist > ul.song_list > li > a'):
            song_title = song_link.select('span > span.song_title')
            song_title = song_title[0].get_text()
            
            # We do not need the album art...
            if 'Album Art' in song_title:
                continue

            song_url =  song_link.get('href')
            song_soup = get_soup(song_url)
            lyrics = song_soup.find('div', class_='lyrics').get_text()
            songs.append( Song(album_title, song_title, lyrics) )

    return songs
    

class TreeNode(dict):
    """
    Tree data structure (a little bloated...)
    NOTE: inhereting form dict makes it simple to serialze to a json object
    """
    def __init__(self, name, children=None):
        super(TreeNode, self).__init__()
        self.__dict__ = self
        self.name = name
        self.children = [] if not children else children

    def add_child(self, node):
        """ 
        Useful for chaining, i.e.
        tree.add_child(TreeNode(..)).add_child(TreeNode(..))
        """
        self.children.append(node)
        return node

    def __repr__(self, level=0):
        ret = '\t'*level+repr(self.name)+'\n'
        for child in self.children:
            ret += child.__repr__(level+1)
        return ret

    def to_json(self, filename=None):
        json_str = json.dumps(self, indent=2)

        if filename:
            with open(filename, 'w') as f:
                f.write(json_str)

        return json_str

class MongoDBPipeline(object):
    """
    Take a hint from scrapy and create an object to connect the scrapper
    with our database
    """
    def __init__(self):
        pass

def create_artist_tree(artist, songs):
    # loop through songs once to build the first layer
    tree = TreeNode(artist)
    for song in songs:
        if song.album not in [node.name for node in tree.children]: # this could be cached...
            tree.add_child(TreeNode(song.album))
    
    # loop through the albums and add the songs/lyrics
    for song in songs:
        for node in tree.children:
            if song.album == node.name:
                node.add_child({'name' : song.title, 'lyrics' : song.lyrics})
    
    return tree

if __name__ == '__main__': 
    #songs = pickle.load(open('drake.pkl', 'r'))
    songs = scrap_rapgenius('Drake')
    pickle.dump(songs, open('drake.pkl', 'wb'))
    tree = create_artist_tree('Drake', songs) 
    tree.to_json('drake.json')
