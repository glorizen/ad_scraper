import requests
import codecs
import time
import os
from bs4 import BeautifulSoup
from adblockparser import AdblockRules

# =============================================================================
# global vars
DOMAIN_FILE = 'domains.txt'
EASYLIST_FILE = 'easylist.txt'
RESULT_FILE = 'scrapped.txt'
PROGRESS_FILE = 'progress.txt'
COUNT = 0

REQUEST_HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; ' + \
		'LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) ' + \
		'Version/4.0 Mobile Safari/534.30',
	'Accept-Language': 'en-US,en;q=0.8',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate, sdch'
}

# =============================================================================
# definitions

def get_domains():
	domains = ['http://www.' + x.replace('\r', '').replace('\n', '') for x in 
		codecs.open(DOMAIN_FILE, 'r', 'utf8').readlines()]
	return domains


def get_rules():
	raw_rules = [x.replace('\r', '').replace('\n', '') for x in 
		codecs.open(EASYLIST_FILE, 'r', 'utf8').readlines()]

	rules = AdblockRules(raw_rules)
	return rules


def download_image(image_url):

	image_name = str(int(time.time())) + os.path.splitext(image_url)[-1]

	r = requests.get(image_url, stream=True)
	if r.status_code == 200:
		with open(image_name, 'wb') as f:
			for chunk in r.iter_content(2048):
				f.write(chunk)

	return image_name

# =============================================================================
# main

def main():
	global EASYLIST_FILE, DOMAIN_FILE, RESULT_FILE, PROGRESS_FILE
	global COUNT, REQUEST_HEADERS

	domains = get_domains()
	rules = get_rules()

	if not os.path.exists(RESULT_FILE):
		f = codecs.open(RESULT_FILE, 'w', 'utf8')
		f.close()

	if not os.path.exists(PROGRESS_FILE):
		f = codecs.open(PROGRESS_FILE, 'w', 'utf8')
		f.close()
	else:
		scrapped_domains = [x.replace('\n', '').replace('\r', '') for x in 
			codecs.open(PROGRESS_FILE, 'r', 'utf8').readlines()]

		COUNT = len(scrapped_domains)

		for domain in scrapped_domains:
			domains.remove(domain)
	
	for domain in domains:
		try:
			r = requests.get(domain, headers=REQUEST_HEADERS, verify=True)
		except:
			continue

		bsObj = BeautifulSoup(r.text, 'html.parser')
		
		blocked = list()	
		for link in bsObj.find_all('a'):
			if link.get('href') and rules.should_block(link.get('href')):
				href = link.get('href').rstrip('/')
				
				if href.endswith('.jpg') or href.endswith('.png'):
					image_name = download_image(href)
					blocked.append(image_name)
				else:
					blocked.append(href)

		f = codecs.open(PROGRESS_FILE, 'a', 'utf8')
		f.write(domain + '\n')
		f.close()

		if blocked:
			ads = ', '.join(blocked)
			line = domain + " >> " + ads + "\n"
			f = codecs.open(RESULT_FILE, 'a', 'utf8')
			f.write(line)
			f.close()

			domain = '*** ' + domain

		COUNT += 1
		print('[%04d] %s' % (COUNT, domain))

if __name__ == '__main__':
	main()
