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
            raw_query = input("Enter the name of the item you would like to add to your queue: ")
            query = self.__process_queue_query(raw_query)
            
            if self.active:
                if self.__has_album_flag(raw_query):
                    search_type = "album"
                else:
                    search_type = "track"

                results = self.spotify.search(query, search_type=search_type)

                try:
                    if search_type == "track":
                        track_uri = self.spotify.get_first_track_uri(results)

                        self.spotify.add_to_queue(track_uri)
                    else:
                        album_id = self.spotify.get_first_album_id(results)

                        self.spotify.add_album_to_queue(album_id)
                except IndexError:
                    print("No results returned for \'%s\'." % raw_query)

    def __process_queue_query(self, query):
        """
        Performs all actions necessary based on the passed add-to-queue query and returns an altered query when appropriate flags are entered.

        :param query: The keyword query entered by the user.
        :return: Either the same query passed to the method or a modified query based on the contents of the arguement.
        """
        if query == "-quit":
            self.active = False
        elif self.__has_album_flag(query):
            return query.replace("-album", "")
        else:
            return query

    def __has_album_flag(self, query):
        """
        Returns a boolean corresponding to whether or not the passed query has an album flag (-album), corresponding to a wish for an entire album to be queued.
        """
        return "-album" in query
