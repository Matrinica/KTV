import vlc
import os
import fnmatch
from pprint import pprint
import re
import cPickle
import pdb
import sys
import urllib

FLIST_FILE = 'flist'
SONG_DIR = 'D:\D\songs'
#SONG_DIR = '/Users/martin/Movies'

def scan_files(path):
    matches = []
    for root, dirnames, filenames in os.walk(SONG_DIR):
        for filename in filenames:
            if not r'.KSC' in filename:
                matches.append(os.path.join(root, filename))
    return matches

def build_flist():
    flist = scan_files(SONG_DIR)
    cPickle.dump(flist, open(FLIST_FILE, 'w'))

def play_song(ref):
    print ('now playing: ' + urllib.unquote(str(os.path.basename(ref.player.get_media().get_mrl()))).decode('utf8')) # windows weird character encoding
    ref.player.play()

def next_song(event, ref):
    # pdb.set_trace()
    if ref.plist:
        ref.player.set_mrl(ref.plist.pop().decode("mbcs").encode("utf-8")) # windows weird character encoding issue
        play_song(ref)
    else:
        print "playlist empty"


class KTV:
    def __init__(self):
       self.player = vlc.MediaPlayer()
       self.em = self.player.event_manager()
       self.em.event_attach(vlc.EventType.MediaPlayerEndReached, next_song, self)
       self.plist = []
       self.flist = cPickle.load(open(FLIST_FILE, 'r'))
       self.audio_track = 1

    def add_song(self, mrl):
        self.plist.insert(0, mrl)
        if not self.player.is_playing():
            next_song(None, self)

    def search(self, keyword):
        return [mrl for mrl in self.flist if keyword.lower() in  os.path.basename(mrl).lower()]

    def user_search(self, keyword):
        results = self.search(keyword)
        if results:
            self.show_filelist(results)
            option = raw_input("select: ")
            if option.isdigit() and 0 <= int(option) < len(results):
                self.add_song(results[int(option)])
            else:
                print 'invalid option'
        else:
            print 'nothing much'
        print 
        self.show_plist()

    def show_plist(self):
        print "Playlists:"
        self.show_filelist(self.plist)

    def show_filelist(self, lst):
        for (counter, item) in enumerate(lst):
            print counter, os.path.basename(item)

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def next(self):
        next_song(None, self)

    def toggle_audio_track(self):
        self.audio_track = 3 - self.audio_track
        print self.audio_get_track_description()
        print 'success: ' + str(self.player.audio_set_track(self.audio_track))

def show_help():
    print '''
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
    print "loading..."
    ktv = KTV()
    show_help()
    while True:
        action = raw_input("action: ")
        if action in ('find', 'f'):
            print '[find]'
            keyword = raw_input("keyword: ")
            ktv.user_search(keyword)
        elif action in ('pause','p'):
            print '[pause]'
            ktv.pause()
        elif action in ('stop', 's'):
            print '[stop]'
            ktv.stop()
        elif action in ('next', 'n'):
            print '[next song]'
            ktv.next()
        elif action in ('track', 't'):
            print '[toggle audio track]'
            ktv.toggle_audio_track()
        elif action in('quit', 'q'):
            print '[quit]'
            ktv.stop()
            break
        elif action in ('build', 'b'):
            print '[build song list]'
            build_flist()
        elif action in ('playlist', 'l'):
            ktv.show_plist()       
        elif action in ('help', 'h'):
            show_help()
        else:
            print 'unknown action: ' + action
        print 
    print 'bye'

if __name__ == '__main__':
    main()


