import os


def startup_operations():
    dirs = [
        'data',
        'data/train_wave'
    ]
    [make_directory(dir) for dir in dirs]


def make_directory(path):
    if not os.path.isdir(path):
        os.mkdir(path)
    return None