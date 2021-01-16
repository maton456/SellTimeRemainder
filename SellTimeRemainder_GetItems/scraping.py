import requests
from bs4 import BeautifulSoup
import datetime

def get_price(url):
    
    site = requests.get(url)

    data = BeautifulSoup(site.text, "html.parser")
    str_table = data.find_all('table', {'class': 'wg-statistics wg-wonder-price-statistics margin-right'})
    # トリム平均を取得
    price = int(str(str_table[0]).split('</td>')[1].split('円')[0].split('<span class="line">')[3].replace(' ', '').replace(',', ''))
    print(price)
    
    return price

if __name__ == "__main__":
    get_price("http://wonder.wisdom-guild.net/price/Arclight+Phoenix/")
    print(datetime.date.today())
    
