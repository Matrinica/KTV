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
def next_song(event, ref):
    if len(ref.plist) < 1:
        print 'No next song'
    else:
        next = ref.plist.pop(0)
        print next
        ref.player.set_mrl(next.decode("mbcs").encode("utf-8"))
        ref.player.play()
        ref.set_audio_track()
    ref.show_plist()

def decode_mrl(mrl):
    return urllib.unquote(str(mrl)).decode('utf8')


##########################
# Class definitions
##########################
class KTV:
    def __init__(self):
       self.player = vlc.MediaPlayer()
       self.em = self.player.event_manager()
       self.em.event_attach(vlc.EventType.MediaPlayerEndReached , next_song, self)
       self.plist = []
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
            cPickle.dump(flist, open(LIB_FILE, 'w'))
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
        self.plist.append(mrl)
        if not self.player.is_playing() and len(self.plist) == 1:
            self.next()

    def search(self, keywords):
        return [mrl for mrl in self.flist if all(keyword.lower() in os.path.basename(mrl).lower() for keyword in keywords)]

    def user_search(self, keywords):
        results = self.search(keywords)
        if results:
            print 
            print 'Results: '
            self.show_filelist(results)
            while True:
                option = raw_input("Select: ")
                if option.isdigit() and 0 <= int(option) < len(results):
                    self.add_song(results[int(option)])
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
        self.show_filelist(self.plist)

    def show_filelist(self, lst):
        for (counter, item) in enumerate(lst):
            print counter, (os.path.basename(item))

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def next(self):
        next_song(None, self)

    def toggle_audio_track(self):
        self.audio_track = 3 - self.audio_track
        self.set_audio_track()

    def build_db(self):
        self.flist = self.build_flist(True)
        self.lib = self.build_lib(self.flist, True)
        
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
            print '[Find song by keywords]'
            while True:
                keywords = raw_input("keywords: ")
                if keywords == '':
                    break
                else:
                    ktv.user_search(keywords.split())
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