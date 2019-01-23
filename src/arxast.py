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

# TTS Lib: https://github.com/desbma/GoogleSpeech

def parse_args():
    return None

# Parse Paper and Build Script Dictionary
def parse_paper(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    script_dict = {}

    # Paper Metadata
    script_dict['title'] = soup.findAll("h1", {"class": "ltx_title"})[0].text
    script_dict['author'] = None

    # Extract Abstract
    script_dict['abstract'] = list(soup.find('div', {'class': 'ltx_abstract'}).children)[3].text

    # Extract Sections
    brem = lambda x: re.sub("[\[].*?[\]]", "", x)
    sections = soup.find_all('section', {'class': 'ltx_section'})

    # Extract Section Content
    script_dict['body'] = {}
    script_dict['body']['sec_title'] = []
    script_dict['body']['sec_content'] = []

    for sec in sections:
        # Parse Content
        script_dict['body']['sec_title'].append(' '.join(sec.findAll('h2', {'class': 'ltx_title_section'})[0].text.split(' ')[1:]).replace('\n', ''))
        script_dict['body']['sec_content'].append(' '.join(list(map(lambda x: x.text, sec.findAll('p')))))

    return script_dict

# Build Audio from Script Dictionary
def build_audio(script, output):
    return None

    # Generate Audio
    tts = gTTS(full_text)
    tts.save(title + '.mp3')

if __name__ == '__main__':
    parse_paper('https://www.arxiv-vanity.com/papers/1710.06542/')
