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


##########################
# Constants
##########################
LIB_FILE = 'lib'
FLIST_FILE = 'flist'
SONG_DIR = 'D:\D\songs'
#SONG_DIR = '/Users/martin/Movies'


##########################
# Global functions
##########################
def build_lib(flist, write_to_file=False):
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
        cPickle.dump(flist, open(LIB_FILE, 'w'))
    return lib


def build_flist(write_to_file=False):
    flist = []
    for root, dirnames, filenames in os.walk(SONG_DIR):
        for filename in filenames:
            if not r'.KSC' in filename:
                flist.append(os.path.join(root, filename))
    if write_to_file:
        cPickle.dump(flist, open(FLIST_FILE, 'w'))
    return flist

def next_song(event, ref):
        if len(ref.plist) <= 1:
            print 'No next song'
        else:
            # if event == None: # called by class method
            #     ref.lplayer.play_item_at_index(1)
            ref.plist.remove_index(0)
            ref.player.audio_set_track(ref.audio_track)
        ref.show_plist()

def decode_mrl(mrl):
    return urllib.unquote(str(mrl)).decode('utf8')


##########################
# Class definitions
##########################
class KTV:
    def __init__(self):
       self.player = vlc.MediaPlayer()
       self.lplayer = vlc.MediaListPlayer()
       self.lplayer.set_media_player(self.player)
       self.em = self.lplayer.event_manager()
       self.em.event_attach(vlc.EventType.MediaListPlayerNextItemSet, next_song, self)
       self.plist = vlc.MediaList()
       self.lplayer.set_media_list(self.plist)
       self.flist = cPickle.load(open(FLIST_FILE, 'r'))
       self.lib = cPickle.load(open(LIB_FILE, 'r'))
       self.audio_track = 1

    def add_song(self, mrl):
        self.plist.add_media(mrl)
        if not self.lplayer.is_playing():
            if len(self.plist) == 1:
                self.lplayer.play()
            else:
                self.lplayer.play_item_at_index(1)
            ref.player.audio_set_track(ref.audio_track)

    def search(self, keyword):
        return [mrl for mrl in self.flist if keyword.lower() in  os.path.basename(mrl).lower()]

    def user_search(self, keyword):
        results = self.search(keyword)
        if results:
            print 
            print 'Results: '
            self.show_filelist(results)
            while True:
                option = raw_input("Select: ")
                if option.isdigit() and 0 <= int(option) < len(results):
                    self.add_song(results[int(option)].decode("mbcs").encode("utf-8"))
                elif option == '':
                    break
                else:
                    print 'Invalid option' 
        else:
            print 'Nothing'
        self.show_plist()
       
    def show_plist(self):
        print 
        print "Playlists:"
        self.show_filelist([decode_mrl(i.get_mrl()) for i in self.plist])

    def show_filelist(self, lst):
        for (counter, item) in enumerate(lst):
            print counter, (os.path.basename(item))

    def pause(self):
        self.lplayer.pause()

    def stop(self):
        self.lplayer.stop()

    def next(self):
        self.lplayer.next()

    def toggle_audio_track(self):
        self.audio_track = 3 - self.audio_track
        self.player.audio_set_track(self.audio_track)

    def build_db(self):
        self.flist = build_flist(True)
        self.lib = build_lib(self.flist, True)
        
    # def play_song(self):
    #     self.lplayer.play()
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
    f, find:      find song by keyword (song/artist name)
    p, pause:     pause the current song
    s, stop:      stop the current song
    n, next:      jump to next song
    t, track:     toggle audio track (vocal/instrumental)
    l, playlist:  show the playlist
    b, build:     scan and build the file list
    q, quit:      quit the program
    '''
    
def main(argv=None):
    show_help()
    while True:
        action = raw_input("action: ")
        if action in ('find', 'f'):
            print '[Find song by keyword]'
            while True:
                keyword = raw_input("keyword: ")
                if keyword == '':
                    break
                else:
                    ktv.user_search(keyword)
        elif action in ('pause','p'):
            print '[Pause]'
            ktv.pause()
        elif action in ('stop', 's'):
            print '[Stop]'
            ktv.stop()
        elif action in ('next', 'n'):
            print '[Next song]'
            ktv.next()
        elif action in ('track', 't'):
            print '[Toggle audio track]'
            ktv.toggle_audio_track()
        elif action in('quit', 'q'):
            print '[Quit]'
            ktv.stop()
            break
        elif action in ('build', 'b'):
            print '[Build song database]'
            ktv.build_db()
        elif action in ('playlist', 'l'):
            ktv.show_plist()       
        elif action in ('help', 'h'):
            show_help()
        else:
            print 'Unknown action: ' + action
            show_help()
        print 
    print 'bye'

if __name__ == '__main__':
    main()