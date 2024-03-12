import numpy as np
import requests
import os
from constants import __TOKEN, __chat_id

def gain(x):
    return ((x > 0) * x).sum()

def loss(x):
    return ((x < 0) * x).sum()

def is_far_from_level(value, levels, data):    
    ave =  np.mean(data['high'] - data['low'])    
    return np.sum([abs(value-level)<ave for _,level in levels])==0

def send_photo(token, chat_id, image_path, image_caption=""):
    #print('image_path',os.path.join(os.path.abspath(os.getcwd()), image_path))
    for cid in chat_id:
        data = {"chat_id": cid, "caption": image_caption}
        url = f"https://api.telegram.org/bot{token}/sendPhoto?chat_id={cid}"
        filepath = os.path.join(os.path.abspath(os.getcwd()), image_path)
        # with open(os.path.join(os.path.abspath(os.getcwd()), image_path), "rb") as image_file:
        #     ret = requests.post(url, data=data, files={"photo": image_file,'rb'})
        ret = requests.post(url, data=data, files = {'photo':open(filepath, 'rb')})
    return ret.json()

def send_msg(token,chat_id, msg):
    for cid in chat_id:
        data = {"chat_id" : cid, "text": msg}
        url = f"https://api.telegram.org/bot{token}/sendMessage?"
        res = requests.post(url, json=data)