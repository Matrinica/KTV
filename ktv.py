##############################
# Martin's Simple KTV System
##############################

##########################
# Imports
##########################
import vlc
import os
import fnmatch
from pprint import pprint
import re
import cPickle
import pdb
import sys
import urllib
import signal
import random


##########################
# Constants
##########################
LIB_FILE = 'lib'
FLIST_FILE = 'flist'
SONG_DIR = 'D:\D\songs'
# MAX_NUM_OF_PLAYED_SONGS_IN_MEDIALIST = 2a
#SONG_DIR = '/Users/martin/Movies'


##########################
# Global functions
##########################
def decode_mrl(mrl):
    return urllib.unquote(str(mrl)).decode('utf8')

# def next_song(event, ref):
#     print 'next song!!!!!!!!!!!'
#     if len(ref.plist) < 1:
#         print 'No next song'
#     else:
#         # next = ref.plist.pop(0)
#         # print next
#         # ref.player.set_mrl(next.decode("mbcs").encode("utf-8"))
#         # ref.player.play()
#         # ref.plist.lock()
#         ref.plist.remove_index(0)
#         # ref.plist.unlock()
#         # ref.set_audio_track()
#     ref.show_plist()

# debug
# def attach_events(em):
#     for key, value in vlc.EventType._enum_names_.iteritems():
#         if value not in ('MediaPlayerPositionChanged', 'MediaPlayerTimeChanged', 'MediaPlayerBuffering'):
#             print '\n\n     attaching ' + value + '\n'
#             em.event_attach(vlc.EventType(key), (lambda evt, value=value: pprint('EVENT: ' + value)))


##########################
# Class definitions
##########################
class KTV:
    def __init__(self):
        # self.instance = vlc.Instance()
        # self.player = vlc.MediaPlayer(self.instance)
        self.player = vlc.MediaPlayer()
        self.plist = vlc.MediaList()
        # self.lplayer = vlc.MediaListPlayer(self.instance)
        self.lplayer = vlc.MediaListPlayer()
        self.lplayer.set_media_player(self.player)
        self.lplayer.set_media_list(self.plist)
        # self.em = self.player.event_manager()
        # self.player.event_manager().event_attach(vlc.EventType.MediaPlayerVout, lambda evt,ref=self: ref.set_audio_track())
        # self.player.event_manager().event_attach(vlc.EventType.MediaPlayerVout, next_song, self)

        # attach_events(self.player.event_manager())
        # attach_events(self.plist.event_manager())
        # attach_events(self.lplayer.event_manager())

        self.audio_track = 1
        self.flist = cPickle.load(open(FLIST_FILE, 'r'))
        self.lib = cPickle.load(open(LIB_FILE, 'r'))

    def set_audio_track(self):
        if self.player.audio_get_track_count() > 1:
            self.player.audio_set_track(self.audio_track)

    def build_lib(self, flist, write_to_file=False):
        lib = {}
        regex = re.compile('^(?P<artist>.+?)-')
        # regex = re.compile('^(?P<artist>.+?)-(?P<song>.+)\..+$')
        for filename in flist:
            result = regex.match(os.path.basename(filename))
            if result:
                artist = result.group(1)
                # print 'match: %s >> %s' % (artist, song)
                if artist in lib:
                    lib[artist].append(filename)
                else:
                    lib[artist] = [filename]
        if write_to_file:
            cPickle.dump(lib, open(LIB_FILE, 'w'))
        return lib

    def build_flist(self, write_to_file=False):
        flist = []
        for root, dirnames, filenames in os.walk(SONG_DIR):
            for filename in filenames:
                if not r'.KSC' in filename:
                    flist.append(os.path.join(root, filename))
        if write_to_file:
            cPickle.dump(flist, open(FLIST_FILE, 'w'))
        return flist

    def add_song(self, mrl):
        self.plist.add_media(mrl)
        if not self.player.is_playing() and len(self.plist) == 1:
            self.next()

    def search(self, keywords):
        return [mrl for mrl in self.flist if all(keyword.lower() in os.path.basename(mrl).lower() for keyword in keywords)]

    def search_and_add(self):
        while True:
            keywords = raw_input("Keywords: ")
            if keywords == '':
                break
            else:
                results = self.search(keywords.split())
                if results:
                    print 
                    print 'Results: '
                    self.show_filelist(results)
                    while True:
                        select = raw_input("Select: ")
                        if select.isdigit() and 0 <= int(select) < len(results):
                            self.add_song(results[int(select)].decode("mbcs").encode("utf-8"))
                        elif select == '*':
                            for result in results:
                                self.add_song(result.decode("mbcs").encode("utf-8"))
                            break
                        elif select == '':
                            break
                        else:
                            print 'Invalid select' 
                    self.show_plist()
                else:
                    print 'Nothing'
       
    def show_plist(self):
        # if self.get_current_index() >= MAX_NUM_OF_PLAYED_SONGS_IN_MEDIALIST:
        #     self.remove_played_songs()
        # print 'current index: %s' % self.get_current_index()
        # print 'count: %s' % self.plist.count()
        print 
        print "Playlists:"
        self.show_filelist([decode_mrl(media.get_mrl()) for media in self.plist], self.get_current_index())

    def show_filelist(self, lst, start=0):
        for (counter, item) in enumerate(lst):
            if counter >= start:
                print (counter - start), (os.path.basename(item))

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def next(self):
        # next_song(None, self)
        self.lplayer.next()
        self.show_plist()

    def toggle_audio_track(self):
        self.audio_track = 3 - self.audio_track
        self.set_audio_track()

    def build_db(self):
        self.flist = self.build_flist(True)
        self.lib = self.build_lib(self.flist, True)
    
    def get_current_index(self):
        return self.plist.index_of_item(self.player.get_media())

    def remove_songs(self):
        while True:
            self.show_plist()
            select = raw_input('Select: ')
            if select.isdigit() and 0 <= int(select) < self.plist_count():
                index = int(select)
                if index == 0:
                    print 'Cannot remove current song'
                else:
                    self.plist.remove_index(self.get_current_index() + index)
            elif select == '':
                break
            else:
                print 'Invalid input'

    def push_songs(self):
        while True:
            self.show_plist()
            select = raw_input('Select: ')
            if select.isdigit() and 0 <= int(select) < self.plist_count():
                index = int(select)
                if index == 0:
                    print 'Cannot push current song'
                else:
                    item = self.plist.item_at_index(self.get_current_index() + index)
                    self.plist.remove_index(self.get_current_index() + index)
                    self.plist.insert_media(item, self.get_current_index() + 1)
            elif select == '':
                break
            else:
                print 'Invalid input'

    def swap_song(self, index1, index2):
        if index1 == index2:
            return
        if index1 > index2:
            index1, index2 = index2, index1
        # now index1 < index2
        self.plist.lock()
        item1 = self.plist.item_at_index(self.get_current_index() + index1)
        item2 = self.plist.item_at_index(self.get_current_index() + index2)
        self.plist.insert_media(item1, self.get_current_index() + index2)
        self.plist.insert_media(item2, self.get_current_index() + index1)
        self.plist.remove_index(self.get_current_index() + index1 + 1)
        self.plist.remove_index(self.get_current_index() + index2 + 1)
        self.plist.unlock()
        self.show_plist()

    def plist_count(self):
        return self.plist.count() - self.get_current_index()

    def browse_by_artist(self):
        while True:
            for i in range(20):
                print self.get_artist()
            k = raw_input("Hit enter to continue: ")
            if k != '':
                break
    
    # TODO
    def get_artist(self):
        for artist, songs in self.lib.iteritems():
            yield artist

    # def hot_songs(self):

    # def relevant_songs(self):

    # def favorite_songs(self):

    # def history_songs(self):

    def shuffle_playlist(self):
        for i in range(self.plist_count()):
            self.swap_song(1 + i, random.randint(1, self.plist_count() - 1))

    # def remove_played_songs(self):
    #     print 'removing played songs'
    #     self.plist.lock()
    #     for i in range(self.get_current_index()):
    #         self.plist.remove_index(0)
    #     self.plist.unlock()

    # def play_song(self):
    #     self.player.play()
    #     print 'Now playing: ' + decode_mrl(os.path.basename(self.player.get_media().get_mrl())) # windows weird character encoding


##########################
# Initialization
##########################
ktv = KTV()


##########################
# Interrupt Handling
##########################
def signal_handler(signal, frame):
    print 'Abort'
    ktv.stop()
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)


##########################
# User Interface
##########################
def show_help():
    print '''
    [List of Actions]
    h, help:      show this help info
    f, find:      find song by keywords (song/artist name)
    a, artist:    browse by artist
    p, pause:     pause the current song
    s, stop:      stop the current song
    n, next:      jump to next song
    u, push:      push songs to the font of playlist
    r, remove:    remove songs from playlist
    e, shuffle:   shuffle playlist
    t, track:     toggle audio track (vocal/instrumental)
    l, playlist:  show the playlist
    b, build:     scan and build the file list
    q, quit:      quit the program
    '''
    
def main(argv=None):
    show_help()
    while True:
        action = raw_input("Action: ")
        if action in ('f', 'find'):
            print '[Find song by keywords]'
            ktv.search_and_add()
        elif action in ('a', 'artist'):
            print '[Browse by artist]'
            ktv.browse_by_artist()
        elif action in ('p', 'pause'):
            print '[Pause]'
            ktv.pause()
        elif action in ('s', 'stop'):
            print '[Stop]'
            ktv.stop()
        elif action in ('n', 'next'):
            print '[Next song]'
            ktv.next()
        elif action in ('u', 'push'):
            print '[Push songs]'
            ktv.push_songs()
        elif action in ('r', 'remove'):
            print '[Remove songs]'
            ktv.remove_songs()
        elif action in ('e', 'shuffle'):
            print '[shuffle]'
            ktv.shuffle_playlist()
        elif action in ('t', 'track'):
            print '[Toggle audio track]'
            ktv.toggle_audio_track()
        elif action in ('b', 'build'):
            print '[Build song database]'
            ktv.build_db()
        elif action in ('l', 'playlist'):
            ktv.show_plist()       
        elif action in ('h', 'help'):
            show_help()
        elif action in('q', 'quit'):
            print '[Quit]'
            ktv.stop()
            break
        else:
            print 'Unknown action: ' + action
            show_help()
        print 
    print 'bye'

if __name__ == '__main__':
    main()