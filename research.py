"""Session research helper; never imported by the offline renderer."""
import concurrent.futures
import subprocess
import sys
from bs4 import BeautifulSoup

def fetch(url):
    raw = subprocess.check_output(['curl', '-Ls', '--max-time', '35', url], text=True)
    soup = BeautifulSoup(raw, 'html.parser')
    for node in soup(['script', 'style', 'nav', 'footer', 'header']):
        node.decompose()
    text = soup.get_text(' ', strip=True)
    links = [(a.get_text(' ', strip=True), a.get('href')) for a in soup.find_all('a', href=True)]
    return url, text, links

def article(url):
    raw = subprocess.run(['curl', '-Ls', '--max-time', '25', url], capture_output=True, text=True).stdout
    soup = BeautifulSoup(raw, 'html.parser')
    dates = [m.get('content') for m in soup.find_all('meta') if 'time' in str(m.get('property', '')) or 'date' in str(m.get('name', '')).lower()]
    dates += [t.get('datetime', t.get_text(' ', strip=True)) for t in soup.find_all('time')]
    for node in soup(['script', 'style', 'nav', 'footer', 'header']):
        node.decompose()
    main = soup.find('main') or soup
    text = main.get_text(' ', strip=True)
    return {'url': url, 'dates': dates, 'text': text[:6500]}

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for url, text, links in pool.map(fetch, sys.argv[1:]):
            print('\nSOURCE:', url, '\n', text[:15000])
            print('\nLINKS:', [(t,h) for t,h in links if t and len(t)>32 and h and ('/articles/' in h or '/story/' in h or '/2026' in h or '/stories/' in h)][:70])
