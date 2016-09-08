from newspaper import Article
from flask import Flask
from flask import request
from flask import jsonify
from bs4 import BeautifulSoup
import time
import cgi
import re



app = Flask(__name__)

@app.route("/v1/extract")
def article_extract():
    start = time.time()
    url = request.args.get("url")
    try:
  
        article = Article(url, keep_article_html=True)
        article.download()
        article.parse()
        article.nlp()
        
        d = {
            "is_readable": article.text != '',
            "title": article.title,
            "top_image": article.top_image,
            "summary": article.summary,
            "keywords": article.keywords,
            "text_html": getHTMLText2(article, 2048),
            "url": article.url
          
            }
        elapsed = time.time() - start

        ret = {
            "status":"OK",
            "elapsed":elapsed,
            "data":d
        }
        return jsonify(**ret), 200    

    except:
        raise
        elapsed = time.time() - start
        ret = {
            "status":"ERROR",
            "elapsed":elapsed
            }
        return jsonify(**ret), 500  


def getHTMLText(article, limit_bytes = 2048):
    if article.text == '': 
        return "";
    s = "";
    s += "<h1>"+article.title+"</h1>"
    s += "<p>"
    
    s += re.sub("\n+", "</p><p>", article.text)
    s = unicode_truncate(s,2048)
    s += "</p>"

    return s

       
def getHTMLText2(article, limit_bytes = 2048):
    if article.text == '': 
        return "";
    s = "";
    s += "<h1>"+article.title+"</h1>"
   
    s = BeautifulSoup(s+article.article_html, 'lxml')

    for tag in s.findAll(True): 
        tag.attrs = {}
        if len(tag.text.strip()) == 0:
            tag.extract()

    s=s.prettify()
    s = unicode_truncate(s,2048)
    
    s = BeautifulSoup(s, 'lxml')

    s = s.prettify()[17:-17];
    return re.sub("\n+\s*", "", s)
    #return s
    
def unicode_truncate(s, length, encoding='utf-8'):
    encoded = s.encode(encoding)[:length]
    return encoded.decode(encoding, 'ignore')

def _remove_attrs(html_text):
    for tag in soup.findAll(True): 
        tag.attrs = {}
    return soup

if __name__ == "__main__":
    app.run()

