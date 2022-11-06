import json
from random import Random

gifs = json.load(open('resources/gifs/gifs.json', 'r'))


def gif(label: str) -> str:
    labeled_gifs = gifs[label]
    idx = Random().randint(0, len(labeled_gifs) - 1)
    return labeled_gifs[idx]
