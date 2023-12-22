from flask import Flask
from time import sleep
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

app = Flask(__name__)
NGO_BASE_URL = "https://www.ongsbrasil.com.br/"
NGO_URL = f"{NGO_BASE_URL}default.asp?Pag=37"

def get_row_data(row_element):
   cell = row_element.find_all('td')[-1]
   span = cell.find('span')
   if span:
      return span.text
   else:
      return cell.find('input')['value']

@app.route('/')
def fetch_ong_info():
   req = Request(NGO_URL, headers={'User-Agent': 'Mozilla/5.0'})
   html_page = urlopen(req).read()
   soup = BeautifulSoup(html_page, 'html.parser')
   table = soup.find('table')
   rows = table.find_all('tr')

   total_count = int(rows[2].find('span').text.split()[1])
   ngo_rows_with_ads = rows[3:]
   # Remove ads
   ngo_rows = [x for x in ngo_rows_with_ads if "Anuncio" not in str(x)]

   links = []
   for row in ngo_rows:
      title = row.find('h2').find('b').text
      # Filter NGOs without titles
      if len(title) > 0:
         links.append(f"{NGO_BASE_URL}{row.find('a')['href']}")
      
   ngo_data = []
   links = links[0:4]

   for link in links:
      sleep(0.2)
      ngo_req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
      ngo_page = urlopen(ngo_req).read()
      ngo_soup = BeautifulSoup(ngo_page, 'html.parser')

      name = ngo_soup.find('h1', attrs={'itemprop': 'name'}).text
      table = ngo_soup.find('table', attrs={'class': 'table'})
      table_rows = table.find_all('tr')
      table_info = [get_row_data(e) for e in table_rows]

      if (len(table_info) == 10):
         address, district, postal, town, state, _, phone, fantasy_name, email, _ = table_info
         website = ''
      else:
         address, district, postal, town, state, _, phone, fantasy_name, email, website, _ = table_info

      classifier_title = ngo_soup.find('h2', text='Classificação da Organização')
      if classifier_title:
         tag = classifier_title.find_next_sibling('p').find_all('span')[-1].text
      else:
         tag = ''

      ngo_data.append({
         'address': address,
         'district': district,
         'postal': postal,
         'town': town,
         'state': state,
         'phone': phone,
         'fantasy_name': fantasy_name,
         'email': email,
         'website': website,
         'tag': tag,
      })

   return str(ngo_data)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=5000)