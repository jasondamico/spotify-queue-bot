"""
A program that allows the user to add tracks to their Spotify queue by searching keywords.
"""

import sys
sys.path.append("src/")
from src.queue_bot import *

import secrets

def main():
    spotify = QueueBot(secrets.client_id, secrets.client_secret)
    spotify.perform_queue_adding()


if __name__ == "__main__":
    main()
