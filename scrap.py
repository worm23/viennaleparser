#! /usr/bin/python3
import requests
import datetime
from bs4 import BeautifulSoup
from urllib.parse import unquote


def scrap(url):
    year = datetime.datetime.now().year

    page= requests.get(url)
    results = BeautifulSoup(page.content, 'html.parser')

    # get basic infos
    title = results.find("h1", class_="c-title--xl").text
    translated = results.find("h5", class_="c-article__translated")
    if translated:
        translated = translated.text
    else:
        translated = ""
    # most infos are only interesting as a concatinated text
    infoElement = results.find("div", class_="c-article__sub")
    info = infoElement.getText("|", strip=True)
    # except the length of the movie, needed for end time of screenings
    length = int(infoElement.find_all("div")[2].text.replace("min",""))

    # get the actors
    creditsElement = results.find("ul", class_="c-credit__items")
    credits = ""
    if creditsElement:
        elements = creditsElement.find_all("li", class_="c-credit__item")
        for element in elements:
            credits = credits + element.text.partition(' - ')[0] + ', '
        if len(elements)>0:
            credits = credits.rpartition(', ')[0]

    # easiest consistent way to support different video plattforms is to extract it from the url parameter of the video iframe
    videoElement = results.find("div", class_="c-video")
    videoUrl = ""
    if videoElement:
        videoElement = videoElement.find("iframe")
        videoUrl = videoElement['src']
        if videoUrl:
            videoUrl = unquote(videoUrl.rpartition('url=')[2]).partition('&max_width=0&max_height=0')[0]
    
    # print scraped infos as a csv
    print(title, end = '')
    print(';', end = '')
    print(translated, end = '')
    print(';', end = '')
    print(info, end = '')
    print(';', end = '')
    print(credits, end = '')
    print(';', end = '')
    print(videoUrl, end = '')
    print(';', end = '')
    print(url, end = '')
    print(';', end = '')

    # get screening times and locations
    screeningsElement = results.find("div", class_="c-screening").find_all("div", class_="c-screening__item")
    # convert film length to timedelta to calculate end time
    delta = datetime.timedelta(minutes=length)
    for screeningElement in screeningsElement:
        # extract date and time of the screening
        day = int(screeningElement.find("div", class_="c-date").find("span", class_="c-date__day").text)
        month = screeningElement.find("div", class_="c-date").find("span", class_="c-date__month").text
        # ugly, but come on, viennale is only in october or november, didn't want to fuck around with date parsing
        if month=='Oct':
            month=10
        else:
            month=11
        timeString = screeningElement.find("div", class_="c-screening__info").find("div", class_="c-screening__time").text
        date = "{}.{}.{} {}".format(day, month, year, timeString)
        date = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')

        # calculate End time and format strings
        startdate = date.strftime("%d.%m.%Y %H:%M")
        dateEnd = date + delta
        enddate = dateEnd.strftime("%d.%m.%Y %H:%M")

        # get basic screening data
        location = screeningElement.find("div", class_="c-screening__info").find("div", class_="c-screening__location").text
        version = screeningElement.find("div", class_="c-screening__info").find("div", class_="c-screening__fassung").text
        # print as csv
        print(startdate, end = '')
        print(';', end = '')
        print(enddate, end = '')
        print(';', end = '')
        print(location, end = '')
        print(';', end = '')
        print(version, end = '')
        print('; ;', end = '')
    # Finally newline to end CSV row
    print('')



# read file with urls to viennale movies
urlFile = open('scrapurls', 'r')
while True:
    line = urlFile.readline()
    if not line:
        break
    # do your stuff
    scrap(line.strip())
urlFile.close()
