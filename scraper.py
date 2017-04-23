import urllib
import urllib2
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify


url = "https://www.youtube.com/results?search_query=nirvana"
response = urllib2.urlopen(url)

html = response.read()
soup = BeautifulSoup(html,"html5lib")
result=[]

for vid in soup.findAll(attrs={'class':'yt-lockup-video'}):

	soup = BeautifulSoup(vid.renderContents(),"html5lib")
	tile_div=soup.find(attrs={'class':'yt-uix-tile-link'})
	#img_src=soup.find(attrs={'class':'yt-thumb video-thumb'}).span.img['src']
	desc_html=soup.find(attrs={'class':'yt-lockup-description'}).decode_contents(formatter="html")
	
	if tile_div:
		link=tile_div['href']
		title=tile_div['title']	
		item={"url":'https://www.youtube.com' + link,"title":title, "desc":desc_html}
		result.append(item)

print result
