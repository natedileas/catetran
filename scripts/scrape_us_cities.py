import re
from bs4 import BeautifulSoup
s = BeautifulSoup(open('List of cities and towns in the United States _ Britannica.html', encoding='utf-8').read(), 'html.parser')
places = s.find_all(href=re.compile('https://www.britannica.com/place/'))
	
# list(map(lambda i: i.get('href','').split('/')[-1], filter(None, places[:1000])))

all_places = {}
state = []
curr_state = ''
for place in places:
	text = place.get('href','').split('/')[-1]

	if place.parent.name == 'h2':
		# print(state)
		curr_state = text.replace('-state', '')
		state = all_places.setdefault(curr_state.replace('-', ' '), [])
	else:
		state.append(text.replace('-' + curr_state, '').replace('-United-States','').replace('-', ' '))

import json
with open('us-cities-towns.json', 'w') as f:
	json.dump(all_places, f)
	