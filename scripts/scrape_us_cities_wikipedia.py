import re
import urllib.parse
from more_itertools import unique_everseen

import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_soup_for_link(link):
    req = requests.get(link)
    soup = BeautifulSoup(req.text, 'html.parser')
    return soup

def extract_table(soup):
    def filter_str_elem(e):   # normalize the names
        return re.sub(r'\[\d{1,2}\]', '', e.replace(u'\u2020', '').replace('*', '').replace('Town of', '').replace('City of', '')).strip()

    table = soup.find(lambda t: t.name=='table' and 'wikitable' in (i.lower() for i in t.get('class')) and 'sortable' in t.get('class'))

    if not table: return []

    # The first tr contains the field names.
    headings = [filter_str_elem(th.get_text()) for th in table.find("tr").find_all("th")]    

    datasets = []
    for row in table.find_all("tr")[1:]:
        dataset = dict(zip(headings, (filter_str_elem(td.get_text()) for td in row.find_all(["td", 'th']))))
        datasets.append(dataset)

    return datasets


if __name__ == '__main__':
    root = 'https://en.wikipedia.org'
    path = '/wiki/Lists_of_populated_places_in_the_United_States'
    
    rootsoup = get_soup_for_link(urllib.parse.urljoin(root, path))
    links = rootsoup.find_all('a', text=re.compile('(Cities|Towns|Cities and towns) in'))

    all_places = {}
    for l in links:
        link = l.get('href')
        soup = get_soup_for_link(urllib.parse.urljoin(root, link))

        tbl = extract_table(soup)
        df = pd.DataFrame(tbl)
        df = df.dropna()

        places = []
        if 'Name' in df.columns:
            places = df.Name.to_list()
        elif 'City' in df.columns:
            places = df.City.to_list()
        elif 'Town' in df.columns:
            places = df.Town.to_list()
        elif 'Municipality' in df.columns:
            places = df.Municipality.to_list()
        elif 'Place Name' in df.columns:
            places = df['Place Name'].to_list()
        else:
            print(df.columns)

        statename = link.split('_in_')[-1].replace('_(state)', '').replace('_', ' ')
        state = all_places.setdefault(statename, [])
        state.extend(places)
        print(link, statename, places[:10])

    # unique-ify
    all_places = {k:list(unique_everseen(i)) for k, i in all_places.items()}

    import json
    with open('us-cities-towns-wiki.json', 'w') as f:
      json.dump(all_places, f)
        
