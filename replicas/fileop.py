import os
import argparse
import datastore
from pathlib import Path

dic = {"path": "", "fname": "", "port": "6379"}

def getinfo():
    print("creating file")
    global fname, path
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', dest='directory', type=str, help='where to store rdb file')
    parser.add_argument('--dbfilename', dest='filename', type=str, help='rdb filename')
    parser.add_argument('--port', dest='port', type=str, help='port info for different servers')

    args = parser.parse_args()
    dic['fname'] = args.filename
    dic["port"] = args.port if(args.port is not None) else "6379"
    dic['path'] = args.directory
    filepath = os.path.join(dic['path'], dic['fname'])
    print(filepath)

    if not os.path.exists(dic['path']):
        os.makedirs(dic['path'])
    f = open(filepath, "a")
    print("filecreated")

    file_size = os.path.getsize(filepath)
    if(file_size == 0):
        datastore.write()

    datastore.fetch()

def getfilename():
    return dic['fname']

def getpath():
    return dic['path']

    

