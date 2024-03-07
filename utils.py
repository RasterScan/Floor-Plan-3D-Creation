import numpy as np
import json
import os
from shutil import which
import configparser
import shutil



def generate_config_file():
    
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'image_path': 'Examples/example.png',
    'blender_installation_path': 'C:\\Program Files\\Blender Foundation\\Blender\\blender.exe',
    'file_structure': '[[[0,0,0], [0,0,0], [0,0,0]], [[0,0,0], [0,0,0], [0,0,0]], [[0,0,0], [0,0,0], [0,0,0]]]',
    'mode': 'simple'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def config_file_exist(name):
    
    return os.path.isfile(name)

def config_get_default():
    
    config = configparser.ConfigParser()

    if not config_file_exist('config.ini'):
        generate_config_file()
    config.read('config.ini')
    return config['DEFAULT']['image_path'], config['DEFAULT']['blender_installation_path'], config['DEFAULT']['file_structure'], config['DEFAULT']['mode']

def save_to_file(file_path, data):
    
    with open(file_path+'.txt', 'w') as f:
        f.write(json.dumps(data))

    print("Created file : " + file_path + ".txt")

def read_from_file(file_path):
    
    with open(file_path+'.txt', 'r') as f:
        data = json.loads(f.read())
    return data

def clean_data_folder(folder):
    
    for root, dirs, files in os.walk(folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

def create_new_floorplan_path(path):
    
    res = 0;
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            try:
                if(int(dir) is not None):
                    res = int(dir) + 1
            except:
                continue

    res = path + str(res) + "/"

    if not os.path.exists(res):
        os.makedirs(res)

    return res;


def get_current_path():
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path

def find_program_path(name):
    
    return which(name)
