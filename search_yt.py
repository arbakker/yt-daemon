import urllib
import urllib2
from bs4 import BeautifulSoup

textToSearch = 'gorillaz'
query = urllib.quote(textToSearch)
url = "https://www.youtube.com/results?search_query=" + query
response = urllib2.urlopen(url)
html = response.read()
soup = BeautifulSoup(html)
for vid in soup.findAll(attrs={'class':'yt-uix-tile-link'}):
        print 'https://www.youtube.com' + vid['href']
