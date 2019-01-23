'''
ArXast: ArXiv Podcast Generator from ArXiv Papers
Author: Yuya Jeremy Ong (yuyajeremyong@gmail.com)
'''
from __future__ import unicode_literals, print_function
import re
import os
import glob
import arxiv
import spacy
import requests
import argparse
from gtts import gTTS
import en_core_web_sm
from bs4 import BeautifulSoup
from pydub import AudioSegment

# TTS Lib: https://github.com/desbma/GoogleSpeech

# Application Parameters
TEMP_DIR = 'tmp/'

# Initialize SpaCy NLP Parser
nlp = en_core_web_sm.load()

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
    abstract = list(soup.find('div', {'class': 'ltx_abstract'}).children)[3].text
    doc = nlp(abstract)
    script_dict['abstract'] = [sent.string.strip() for sent in doc.sents]

    # Extract Sections
    brem = lambda x: re.sub(r'\[.*?\]', "", x)
    sections = soup.find_all('section', {'class': 'ltx_section'})

    # Extract Section Content
    script_dict['body'] = {}
    script_dict['body']['sec_title'] = []
    script_dict['body']['sec_content'] = []

    for sec in sections:
        # Parse Section Title
        script_dict['body']['sec_title'].append(' '.join(sec.findAll('h2', {'class': 'ltx_title_section'})[0].text.split(' ')[1:]).replace('\n', ''))

        # Parse Section Text and Tokenize Sentence
        body_text = ' '.join(list(map(lambda x: brem(x.text), sec.findAll('p'))))
        doc = nlp(body_text)
        script_dict['body']['sec_content'].append([sent.string.strip() for sent in doc.sents])

    return script_dict

# Build Audio from Script Dictionary
def build_audio(script, output):
    audio_list = []
    index = 2

    # Title Section
    gTTS(script['title']).save(TEMP_DIR + '0.mp3')
    audio_list.append(0)
    audio_list.append('1')

    # Abstract
    gTTS('Abstract').save(TEMP_DIR + '1.mp3')
    audio_list.append(1)
    audio_list.append('0.5')

    for txt in script['abstract']:
        gTTS(txt).save(TEMP_DIR + str(index) + '.mp3')
        audio_list.append(index)
        audio_list.append('0.3')
        index += 1

    audio_list.append('1')

    # Body Content
    for i in range(len(script['body']['sec_title'])):
        gTTS('Section ' + str(i + 1) + ': ' + script['body']['sec_title'][i]).save(TEMP_DIR + str(index) + '.mp3')
        audio_list.append(index)
        index += 1

        audio_list.append('0.5')

        for txt in script['body']['sec_content'][i]:
            gTTS(txt).save(TEMP_DIR + str(index) + '.mp3')
            audio_list.append(index)
            audio_list.append('0.3')
            index += 1

    return audio_list

def speed_change(sound, speed=1.0):
    # From: https://stackoverflow.com/questions/51434897/how-to-change-audio-playback-speed-using-pydub
    sound_with_altered_frame_rate = sound._spawn(sound.raw_data,
        overrides={"frame_rate": int(sound.frame_rate * speed)})

    return sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)

def stitch_audio(track_list, output, rate):
    master = AudioSegment.empty()

    for track in track_list:
        if isinstance(track, int):
            sound = AudioSegment.from_mp3(TEMP_DIR + str(track) + '.mp3')
            master += speed_change(sound, rate)
        elif isinstance(track, str):
            master += AudioSegment.silent(duration=float(track) * 1000)

    master.export(output, format='mp3')

    # Cleanup Temp Files
    tmp_dir = glob.glob(TEMP_DIR+'*')
    for f in tmp_dir: os.remove(f)

if __name__ == '__main__':
    script = parse_paper('https://www.arxiv-vanity.com/papers/1710.06542/')
    track_list = build_audio(script, 'output')
    stitch_audio(track_list, script['title'] + '.mp3', rate=1.1)
