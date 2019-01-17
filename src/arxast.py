'''
ArXast: ArXiv Podcast Generator from ArXiv Papers
Author: Yuya Jeremy Ong (yuyajeremyong@gmail.com)
'''
from __future__ import print_function
import re
import arxiv
import requests
import argparse
from gtts import gTTS
from bs4 import BeautifulSoup

def parse_args():
    return None

def parse_paper(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    full_text = ''

    # Paper Metadata
    title = soup.findAll("h1", {"class": "ltx_title"})[0].text
    authors = None

    # Extract Abstract
    abstract = list(soup.find('div', {'class': 'ltx_abstract'}).children)[3].text

    # Extract Sections
    brem = lambda x: re.sub("[\[].*?[\]]", "", x)
    sections = soup.find_all('section', {'class': 'ltx_section'})

    # Process Script
    full_text += title + '\n'
    full_text += 'Abstract\n' + abstract + '\n'

    for idx, sec in enumerate(sections):
        # Parse Content
        sect_title = ' '.join(sec.findAll('h2', {'class': 'ltx_title_section'})[0].text.split(' ')[1:]).replace('\n', '')
        sect_text = ' '.join(list(map(lambda x: x.text, sec.findAll('p'))))

        # Append Script
        full_text += 'Section ' + str(int(idx + 1)) + '.\n'
        full_text += sect_title + '\n'
        full_text += sect_text + '\n\n'

    # Generate Audio
    tts = gTTS(full_text)
    tts.save(title + '.mp3')

if __name__ == '__main__':
    parse_paper('https://www.arxiv-vanity.com/papers/1710.06542/')
