from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import urllib                                                                                                                                 
import urllib2
from bs4 import BeautifulSoup



app = Flask(__name__)
api = Api(app)

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class Search(Resource):
    def post(self):
        json_data = request.get_json(force=True)
        search_term = json_data['q']
        query = urllib.quote(search_term)
        url = "https://www.youtube.com/results?search_query=" + query
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html)
        result=[]

        for vid in soup.findAll(attrs={'class':'yt-lockup-video'}):
            soup = BeautifulSoup(vid.renderContents(),"html5lib")
            tile_div=soup.find(attrs={'class':'yt-uix-tile-link'})
            desc_html=soup.find(attrs={'class':'yt-lockup-description'}).decode_contents(formatter="html")

            if tile_div:
                link=tile_div['href']
                title=tile_div['title'] 
                item={"url":'https://www.youtube.com' + link,"title":title, "desc":desc_html}
                result.append(item)
            
        return jsonify(results=result)


api.add_resource(HelloWorld, '/')

api.add_resource(Search, '/search')

if __name__ == '__main__':
    app.run(debug=True)
