import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL


def whats_new():
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    session = CachedSession()
    response = session.get(whats_new_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = soup.find(name='section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = main_div.find(name='div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = []
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = soup.find(name='h1')
        dl = soup.find(name='dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    for row in results:
        print(*row)


def latest_versions():
    session = CachedSession()
    response = session.get(MAIN_DOC_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = soup.find(name='div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all(name='ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    results = []
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)

        if text_match:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append((link, version, status))

    for row in results:
        print(*row)


def download():
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    session = CachedSession()
    response = session.get(downloads_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')

    table_tag = soup.find(
        name='table', attrs={'class': 'docutils'}
    )
    zip_tag = table_tag.find(
        name='a', attrs={'href': re.compile(r'.+\.zip$')}
    )
    link = zip_tag['href']
    archive_url = urljoin(downloads_url, link)
    filename = archive_url.split('/')[-1]

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)

    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
