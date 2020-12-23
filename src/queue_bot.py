"""
A module containing a class that is capable of querying for a certain track and adding the track to the user's queue.
"""

from spotify_client import *

class QueueBot():
    """
    A command line-based bot that allows the user to search for and add a track to their queue on Spotify.
    """

    def __init__(self, client_id, client_secret):
        """
        Constructor method; creates a QueueBot object with default values.
        """
        self.spotify = SpotifyAPI(client_id, client_secret)
        self.active = False

    def perform_queue_adding(self):
        """
        Enters the process of prompting the user to add items to the queue.
        """
        self.active = True

        while self.active:
            query = input("Enter the name of the track you would like to add to your queue: ")
            
            tracks = self.spotify.search(query, search_type="track")
            track_uri = self.spotify.get_first_track_uri(tracks)

            self.spotify.add_to_queue(track_uri)

