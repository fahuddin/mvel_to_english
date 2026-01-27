import os 
from typing import List, Tuple 

def read_files(dir: str):
    docs = []
    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        with open(path, "r", encoding="utf-8", errors="replace") as f: 
            docs.append((name, f.read()))
    return docs


