import vlc,pafy
video = pafy.new("https://www.youtube.com/watch?v=tW3J9XnBbqk")
p=vlc.MediaPlayer(video.audiostreams[1].url)
p.play()

p=vlc.MediaPlayer("https://r3---sn-32o-5hne.googlevideo.com/videoplayback?mt=1492980810&mv=m&pl=24&id=o-ALqbrYa75J5NXlMNSxjT9V-sP9KStmc7QBxANS9hD1ZU&ei=qRT9WIv4JMb01gK4p5uICQ&ms=au&ip=77.172.180.130&gir=yes&expire=1493002505&source=youtube&mm=31&mn=sn-32o-5hne&sparams=clen%2Cdur%2Cei%2Cgir%2Cid%2Cinitcwndbps%2Cip%2Cipbits%2Citag%2Ckeepalive%2Clmt%2Cmime%2Cmm%2Cmn%2Cms%2Cmv%2Cpl%2Crequiressl%2Csource%2Cupn%2Cexpire&lmt=1492699107738344&clen=3078780&requiressl=yes&key=yt6&initcwndbps=1518750&keepalive=yes&upn=YOBtIiXPhhA&itag=250&mime=audio%2Fwebm&ipbits=0&dur=363.081&signature=588EA7DE525A2D0D374EADF092108064A51E8525.8C29468D44F9510DB2826193414875D9E6BA3603&ratebypass=yes")
p.play()

