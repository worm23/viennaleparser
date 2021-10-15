#! /usr/bin/python
import requests
import datetime
from bs4 import BeautifulSoup
from urllib import unquote


def scrap(url):
    year = datetime.datetime.now().year

    page= requests.get(url)
    results = BeautifulSoup(page.content, 'html.parser')

    title = results.find("h1", class_="c-title--xl").text
    translated = results.find("h5", class_="c-article__translated")
    if translated:
        translated = translated.text
    else:
        translated = ""
    infoElement = results.find("div", class_="c-article__sub")
    info = infoElement.getText("|", strip=True)
    time = int(infoElement.find_all("div")[2].text.replace("min",""))

    creditsElement = results.find("ul", class_="c-credit__items")
    credits = ""
    if creditsElement:
        elements = creditsElement.find_all("li", class_="c-credit__item")
        for element in elements:
            credits = credits + element.text.partition(' - ')[0] + ', '
        if len(elements)>0:
            credits = credits.rpartition(', ')[0]

    videoElement = results.find("div", class_="c-video")
    videoUrl = ""
    if videoElement:
        videoElement = videoElement.find("iframe")
        videoUrl = videoElement['src']
        if videoUrl:
            videoUrl = unquote(videoUrl.rpartition('url=')[2]).decode('utf8').partition('&max_width=0&max_height=0')[0]
    
    print(title),
    print(';'),
    print(translated),
    print(';'),
    print(info),
    print(';'),
    print(credits),
    print(';'),
    print(videoUrl),
    print(';'),
    print(url),
    print(';'),

    screeningsElement = results.find("div", class_="c-screening").find_all("div", class_="c-screening__item")
    delta = datetime.timedelta(minutes=time)
    for screeningElement in screeningsElement:
        day = int(screeningElement.find("div", class_="c-date").find("span", class_="c-date__day").text)
        month = screeningElement.find("div", class_="c-date").find("span", class_="c-date__month").text
        if month=='Oct':
            month=10
        else:
            month=11
        timeString = screeningElement.find("div", class_="c-screening__info").find("div", class_="c-screening__time").text
        date = "{}.{}.{} {}".format(day, month, year, timeString)
        date = datetime.datetime.strptime(date, '%d.%m.%Y %H:%M')

        location = screeningElement.find("div", class_="c-screening__info").find("div", class_="c-screening__location").text
        version = screeningElement.find("div", class_="c-screening__info").find("div", class_="c-screening__fassung").text

        startdate = date.strftime("%d.%m.%Y %H:%M")
        dateEnd = date + delta
        enddate = dateEnd.strftime("%d.%m.%Y %H:%M")

        print(startdate),
        print(';'),
        print(enddate),
        print(';'),
        print(location),
        print(';'),
        print(version),
        print('; ;'),

    print



# Using readline()
urlFile = open('scrapurls', 'r')
while True:
    # Get next line from file
    line = urlFile.readline()
                      
    # if line is empty
    # end of file is reached
    if not line:
        break
    scrap(line.strip())
                                               
urlFile.close()
