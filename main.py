from newspaper import Article
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import cgi
import re

app = Flask(__name__)

@app.route("/v1/extract")
def extract():

    url = request.args.get("url")
    url = url if "://" in url else "http://" + url
    hook_id = request.args.get("hook_id")
    ret, error_code = processArticle(url, hook_id)
    return jsonify(**ret), error_code  

@app.route("/v1/display")
def display():
    url = request.args.get("url")
    hook_id = request.args.get("hook_id")
    ret, error_code = processArticle(url, hook_id)
    if ret['data']['text_html']=="": 
        return "Not readable content",500
    return render_template("webview.html", body = ret['data']['text_html'], hook_id = hook_id, css = "CSS")

@app.route("/v1/css")
def css():
    return render_template("style.css"), 200, {'Content-Type': 'text/css; charset=utf-8'}

def processArticle(url, hook_id):
    start = time.time()
    
    try:
       
        article = Article(url, keep_article_html=True)
        article.download()
        article.parse()

        #article.nlp()
        
        d = {
            "is_readable": article.text != '',
            "title": article.title,
            "top_image": article.top_image,
            "summary": article.summary,
            "keywords": article.keywords,
            "text_html": getHTMLText2(article, 768),
            "url": article.url,
            "amp_url": extract_amp_url(article)
          
            }
        elapsed = time.time() - start

        ret = {
            "status":"OK",
            "elapsed":elapsed,
            "data":d
        }
        return ret, 200    

    except Exception:
        raise
        elapsed = time.time() - start
        ret = {
            "status":"ERROR",
            "elapsed":elapsed
            }
        return ret, 500  

def getHTMLText(article, limit_bytes = 2048):
    if article.text == '': 
        return "";
    s = "";
    s += "<h1>"+article.title+"</h1>"
    s += "<p>"
    
    s += re.sub("\n+", "</p><p>", article.text)
    s = unicode_truncate(s,limit_bytes)
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
    s = unicode_truncate(s,limit_bytes)
    
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

def  extract_amp_url(article): 

    soup = BeautifulSoup(article.html, 'html.parser')
    
    element = soup.find('link', attrs={'rel': 'amphtml'})
    if element:
        try:
            href = element['href']
        except ValueError:
            # In case there are not enough values to unpack
            # for instance: <meta http-equiv="refresh" content="600" />
            return None
        else:
            return href if not href.startswith('//') else ((urlparse(article.url).scheme)+":"+href)
            



@app.errorhandler(500)
def internal_error(error):
    return  '{ "status":"ERROR", "message":"INTERNAL"}', 500


@app.errorhandler(404)
def notfound_error(error):
    return  '{ "status":"ERROR", "message":"NOT_FOUND" }', 400


if __name__ == "__main__":
    app.run()

