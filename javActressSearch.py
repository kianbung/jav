import requests, bs4

javCode = 'SSNI002'

url = 'https://onejav.com/search/' + javCode

javSearch = requests.get(url)

javSoup = bs4.BeautifulSoup(javSearch.text, 'html.parser')

actressSelect = javSoup.select('body > div > div:nth-child(2) > div > div > div.column.is-5 > div > div.panel > a')

actressName = actressSelect[0].getText()

print(actressName)
