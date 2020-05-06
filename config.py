import argparse

def get_args():
    argparser =  argparse.ArgumentParser(description="scrape web pages for rankings")
    argparser.add_argument('--source', help="source to pull scrape functions from")
    argparser.add_argument('--url', default=None, help="url to scrape from at source")
    argparser.add_argument('--root', default="./", help="url to scrape from at source")
    return argparser.parse_args()
