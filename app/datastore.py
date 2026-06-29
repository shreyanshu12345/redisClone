

import threading
import rdbwrite
import parser

store = {}
def fetch():
    global store
    print()
    print("setting store")
    store = parser.parse_rdb_file("dump.rdb")

def remove(key):
    print("calling remove")
    store.pop(key)

def set(key, value, ttl):
    print()
    print("setting ...", key)
    print(store)
    print()
    store[key] = value
    ttl = ttl/1000
    print
    print(ttl)
    if(ttl > 0):
        print("calling remove...")
        threading.Timer(ttl, remove, args=(key, )).start()      


def retrive(key):
    print()
    print("fetching for value...", key)
    print(key)
    print(store)
    print()
    print(type(key))
    
    if(key in store):
        return store[key]
    else:
        return None
    
def write():
    print()
    print("before write = ", store)
    rdbwrite.write_rdb_file(store)
    print("after write = ", store)
    print()

def get_all_keys():
    return [i for i in store]
