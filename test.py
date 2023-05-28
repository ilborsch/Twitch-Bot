import requests_html
import bs4
import json


session = requests_html.HTMLSession()

response = session.get('https://www.dotabuff.com/players/1161246296')
bs = bs4.BeautifulSoup(response.content, "html.parser")


print(bs.find('div',  class_='rank-tier-wrapper')['title'])





