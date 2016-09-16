# coding: UTF-8

from flask import Flask, render_template, request, redirect, url_for
import csv
import socket
import datetime

from bs4 import BeautifulSoup
import urllib.request

app = Flask(__name__)

# products from Yahoo
def yahoo_(key):
    url =  'http://search.shopping.yahoo.co.jp/search?p=' + urllib.parse.quote(key)
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    div = soup.find_all("div", class_="elItemWrapper")
    ad = soup.find_all("li", class_="elItemMatch")
    def get_imfo(inData):
        product = {}
        products_contain_ad = []
        for iD in inData:
        # get title
            title = str(iD.find("dd", class_="elName").span)[6:-7].replace('<em>', '').replace('</em>', '')
        # get img_url
            img_url = str(iD.find("p", class_="elImage").img.get("src"))
        # get price
            price = iD.find("dd", class_="elPrice").span.string
        # get url
            url = str(iD.find("dd", class_="elName").a.get("href"))
        # make product(dictionary) and append it products(list)
            product = {'title': title, 'img': img_url, 'price': price, 'url': url}
            products_contain_ad .append(product)
        return products_contain_ad
    products = []
    for iP in get_imfo(div):
        # If iP is advertisement > pass, else append iP products
        if iP in get_imfo(ad):
            pass
        else:
            products.append(iP)
    return products

# products from Rakuten
def rakuten_(key):
    url = 'http://search.rakuten.co.jp/search/mall/' + urllib.parse.quote(key) +'/'
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    div = soup.find_all("div", class_="rsrSResultSect")
    product = {}
    products = []
    for iD in div:
    # get title
        title = iD.find("h2").a.string[5: ]
    # get img_url
        img_urt_contain_dust = iD.find("img").get("src")
        #dust_position =  img_urt_contain_dust.index('?')
        #img_url =  img_urt_contain_dust [ : dust_position]
        img_url = img_urt_contain_dust
    # get price
        price_start = str(iD.find("p", class_="price").a)
        a_start_index = price_start.index('">')
        a_start = price_start[a_start_index  + 2: ] # the reason why +2 is skip '">'
        span_end_index = a_start.index('<span>')
        price = a_start[ : span_end_index]
    # get url
        url = str(iD.find(class_="price").a.get("href"))
    # make product(dictionary) and append it products(list)
        product = {'title': title, 'img': img_url, 'price': price, 'url': url}
        products.append(product)
    return products

# products from Amazon
def amazon_(key):
    url = 'https://www.amazon.co.jp/s/field-keywords=' + urllib.parse.quote(key)
    req = urllib.request.Request(url)
    response = urllib.request.urlopen(req)
    html = response.read()
    soup = BeautifulSoup(html, "lxml")
    div = soup.find("div", id="atfResults")
    li = div.find_all("li", class_="s-result-item")
    product = {}
    products = []
    for iL in li:
    # get title
        title = iL.find("a", class_="s-access-detail-page").string
    # get img_url
        img_url = str(iL.find("a" ,class_="a-link-normal").img.get("src"))
    # get price
        price = iL.find("span", class_="a-color-price").string[1: ]
            # get url
        url = str(iL.find("a" ,class_="a-link-normal").get("href"))

        product = {'title': title, 'img': img_url, 'price': price, 'url': url}
        products.append(product)
    return products

# main app
@app.route('/', methods=['POST', 'GET'])
def index():
    title = "serch products in Yahoo, Rakuten and Amazon｜oPython"

    if request.method != 'POST':
        message = "Search under the product name in Yahoo, Rakuten and Amazon"
        #message = picked_up()
        return render_template('search.html',
                               title=title, message=message)
    else:
        keyword = request.form['input_key']

        if keyword:
            yahoo = yahoo_(keyword)
            rakuten = rakuten_(keyword)
            #amazon = amazon_(keyword)
            message = keyword
            yourIP = socket.gethostbyname(socket.gethostname())
            with open('histories.csv', mode = 'a', encoding = 'shift_jis') as imfo:
                imfo.write(keyword + "," + yourIP + "," + datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S') + "\n")

        else:
            message = "Please enter a product name"
        return render_template('search.html',
                               title=title, message=message, output_key=keyword,
                               yahoo=yahoo, rakuten=rakuten)#, amazon=amazon)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
