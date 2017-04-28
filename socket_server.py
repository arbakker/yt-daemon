from tornado import websocket, web, ioloop, escape
import json,pafy,vlc,os
from bs4 import BeautifulSoup
import urllib                                                                                                                                 
import urllib.parse 
import threading

cl = []
playlist=[]
current_track={}
instance=vlc.Instance()
p=instance.media_player_new()
p_em = p.event_manager()
p.audio_set_volume(70)
mute_vol=-1
# playing,paused,stopped
state="stopped"



class myThread (threading.Thread):
    def __init__(self, threadID, name, socket_handler):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.socket_handler = socket_handler
    def run(self):
        self.socket_handler.change_track_thread()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("player/index.html")

class SocketHandler(websocket.WebSocketHandler):
    def initialize(self):
        global p_em
        p_em.event_attach(vlc.EventType.MediaPlayerEndReached, self.end_reached)

    def end_reached(self,event):
        # required to change track from a different track, since vlc callback cannot callback on the vlc object
        thread1 = myThread(1, "Thread-1", self)
        thread1.start()

    def change_track_thread(self):
        global state
        state="stopped"
        self.next()

    def set_track(self, track):
        global p
        global current_track
        global state
        global instance

        if state=="playing":
            p.stop()
            state="stopped"
        if state=="stopped" or state=="paused":                        
            video = pafy.new(track['url'])
            media=instance.media_new(video.getbestaudio().url)
            p.set_media(media)
            current_track=track
            self.current_changed()
        # keep paused state when paused
        if state=="stopped":
            p.play()
            self.state_changed("playing")

    def play_pause(self):
        p.play()
        self.state_changed("playing")


    def stop(self):
        global p
        global state
        if state=="playing" or state=="paused":
            p.stop()
            self.state_changed("stopped")

    def pause(self):
        global p
        global state
        if state=="playing":
            p.pause()
            self.state_changed("paused")

    def next(self):
        global current_track
        global playlist
        i=playlist.index(current_track)
        if i!=-1 and i<len(playlist)-1:
            track=playlist[i+1]
            self.set_track(track)

    def previous(self):
        global current_track
        global playlist

        i=playlist.index(current_track)
        if i!=-1 and i>0:
            track=playlist[i-1]
            self.set_track(track)

    def state_changed(self,in_state):
        global state
        state=in_state
        data= { "command":"state_changed", "payload":state}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)


    def playlist_changed(self): 
        global playlist
        data= { "command":"playlist_changed", "payload":playlist}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    def remove_track(self,track):
        global playlist
        global p
        global current_track
        index=-1
        for i, item in enumerate(playlist):
            if item['url'] == track['url']:
                index=i
                break   
                
        if index!=-1:
            if current_track:
                # check if to remove item is current item
                if track['url']==current_track['url']:
                    self.next()
                # Check if changed to new song, otherwise stop playing
                if current_track['url']==track['url']:
                    self.stop()
                    current_track={}
                    self.current_changed()

            playlist.pop(index)
            self.playlist_changed()

    def init_state(self):
        global playlist, current_track, state
        volume=self.volume_getter()
        data= { "command":"init_state", "payload":{"playlist":playlist,"current_track":current_track,"state": state,"volume":volume}}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)
    
    def mute(self):
        global p, mute_vol
        if p:
            # mute if mute_vol -1
            if mute_vol==-1:
                mute_vol=self.volume_getter()
                self.set_volume(0)
            # else restore volume
            else:
                self.set_volume(mute_vol)
                mute_vol=-1

    def volume_getter(self):
        global p
        result=-1
        if p:
            current_volume=p.audio_get_volume()
            output_volume=int(current_volume/0.7)
            result=output_volume
        return result

    def volume_setter(self,in_volume):
        global p
        if p:
            out_volume=int(in_volume*0.7)
            p.audio_set_volume(out_volume)


    def set_volume(self, volume):
        global p
        if volume>100:
            volume=100
        self.volume_setter(volume)
        data= { "command":"volume_changed", "payload":volume}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    def increment_volume(self):
        global p, mute_vol
        if p:
            mute_vol=-1
            current_volume=self.volume_getter()
            # volume ranges from 0,70 otherwise sounds gets distorted
            if current_volume<96:
                current_volume+=5
            else:
                current_volume=100
            self.set_volume(current_volume)

    def decrement_volume(self):
        global p
        if p:
            current_volume=self.volume_getter()
            if current_volume>4:
                current_volume-=5
            else:
                current_volume=0
            self.set_volume(current_volume)

    def current_changed(self):
        global current_track
        data= { "command":"current_changed", "payload":current_track}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    def check_origin(self, origin):
        return True
    
    def on_message(self, message):
        global state
        json_data = escape.json_decode(message)
        command=list(json_data.keys())[0]
        payload=json_data[command]

        if command=="add_track":
            playlist.append(payload)
            self.playlist_changed()
        elif command=="remove_track":
            self.remove_track(payload)
        elif command=="play":
            if state=="paused":
                self.play_pause()
            else:
                self.set_track(payload)
        elif command=="pause":
            self.pause()
        elif command=="next":
            self.next()
        elif command=="previous":
            self.previous()
        elif command=="init_state":
            self.init_state()
        elif command=="increment_volume":
            self.increment_volume()
        elif command=="decrement_volume":
            self.decrement_volume()
        elif command=="mute":
            self.mute()


    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)


class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        self.finish()
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value" : value}
        data = json.dumps(data)
        for c in cl:
            c.write_message(data)

    @web.asynchronous
    def post(self, *args):
        #self.finish()
        json_data = escape.json_decode(self.request.body)
        query=json_data['q']
        search_term =  urllib.parse.quote(query)
        url = "https://www.youtube.com/results?search_query=" + search_term
        response = urllib.request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html)
        result=[]

        for vid in soup.findAll(attrs={'class':'yt-lockup-video'}):
            soup = BeautifulSoup(vid.renderContents(),"lxml")
            tile_div=soup.find(attrs={'class':'yt-uix-tile-link'})
            desc=soup.find(attrs={'class':'yt-lockup-description'})
            desc_html=""
            if desc:
                desc_html = "".join([str(x) for x in desc.contents])
            if tile_div:
                link=tile_div['href']
                title=tile_div['title']
                yt_id=link.split("=")[1]
                item={"url":'https://www.youtube.com' + link,"title":title, "desc":desc_html, "id": yt_id}
                result.append(item)
        self.finish(json.dumps({"results":result}))

root = os.path.dirname(__file__)





#(r'/', IndexHandler),
app = web.Application([
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r"/(.*)", web.StaticFileHandler, {"path": root, "default_filename": "index.html"}),
    (r'/(rest_api_example.png)', web.StaticFileHandler, {'path': './player/'}),
])

if __name__ == '__main__':
    app.listen(9999)
    ioloop.IOLoop.instance().start()
