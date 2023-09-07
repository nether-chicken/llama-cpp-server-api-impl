#!/usr/bin/env python
from sys import argv
from flask import Flask, request
from llama_cpp import Llama
import os
import base64

def find_bin_file(directory, censored=False):
    for file_name in os.listdir(directory):
        if file_name.endswith('.bin') and os.path.isfile(os.path.join(directory, file_name)):
            is_unfiltered = 'unfiltered' in file_name.lower() or 'uncensored' in file_name.lower()
            if censored is not None and not censored ^ is_unfiltered:
                continue
            print('Loading: ' + file_name)
            return os.path.join(directory, file_name)
llama_kwargs = {
        'model_path': find_bin_file('/home/opc', censored=None) if len(argv) == 1 else argv[1],
        'n_threads': 4,
        'use_mlock': True,
        }
llm = Llama(**llama_kwargs)

app = Flask(__name__)
lock = False
b64e = base64.b64encode
preprompt = """
Robot Chicken is obsessed with chickens, the most glorious animal on the face of this Earth. Robot Chicken was created by Nether Chicken, and inhabits 0b0t, a land without laws that is owned by Synio, a german dictator who abuses his power over the land.
"""
def get_prompt(bare_prompt):
    global preprompt
    return f"{preprompt}\nQ: {bare_prompt}\nRobot Chicken: "

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    global lock
    if lock:
        return b64e('Wait a moment'.encode('utf-8'))
    lock = True
    data = request.get_json()
    try:
        bare_prompt_base64 = data.get('prompt')
        print('Prompt base64: ' + bare_prompt_base64)
        bare_prompt = base64.b64decode(bare_prompt_base64).decode('utf-8')
        full_prompt = get_prompt(bare_prompt)
        reply = llm(full_prompt, stop=["Q:"])['choices'][0]['text']
        lock = False
        return b64e(reply.replace('</s>','').encode('utf-8'))
    except Exception as e:
        app.logger.error(e)
        return 'Not a base64 string'

@app.route('/preprompt', methods=['GET'])
def handle_get_preprompt():
    global preprompt
    return b64e(preprompt.encode('utf-8'))

@app.route('/preprompt', methods=['POST'])
def handle_preprompt():
    global lock
    global preprompt
    if lock:
        return 'No'
    data = request.get_json()
    try:
        bare_preprompt_base64 = data.get('preprompt')
        bare_preprompt = base64.b64decode(bare_preprompt_base64).decode('utf-8')
        if bare_preprompt.endswith('.'):
            preprompt = bare_preprompt
        else:
            preprompt = bare_preprompt + '.'
        lock = False
        return 'Yes'
    except Exception as e:
        app.logger.error(e)
        return 'Not a base64 string'
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5957)
