from bs4 import BeautifulSoup
import requests


def getdatancov():
    soup = BeautifulSoup(requests.get("http://ncov.mohw.go.kr/bdBoardList_Real.do").text.replace(u"\xa0", ""), 'html.parser')

    return [str(i).split(">")[1].split("<")[0].replace(',', '') for i in
            soup.find_all('td')[:4]] + [str(soup.find('p')).split("황")[1].split("<")[0]]