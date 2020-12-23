import base64
import datetime
from urllib.parse import urlencode

import oauth2

import requests

class SpotifyAPI(oauth2.SpotifyAPIOAuth2):
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        """
        Paramaterized constructor: initializes a SpotifyAPI object with the specified client ID and client secret.

        :param client_id: The id associated with the registered Spotify application.
        :param client_secret: The secret key associated with the registered Spotify application.
        """
        oauth2.SpotifyAPIOAuth2.__init__(self, client_id, client_secret, *args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
    
    def get_resource_headers(self):
        """
        Returns the header to be used when retreiving resources from the Spotify API.

        :return: A dictionary to be passed to the post function when retreiving resources from the API.
        """
        token = self.get_access_token("authorization_code")

        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        return headers
    
    def get_resource(self, lookup_id, resource_type="albums", version="v1"):
        """
        Returns the resource specified stored with the passed lookup id in the form of a dictionary.

        :param lookup_id: The id at which the resource is stored.
        :param resource_type: The type of resource that should be returned (e.g.: albums, artists)
        :param version: The API version from which the resource should be retrieved. 
        :return: A dictionary containing the specified resource. Returns an empty dictionary if the specified resource is not found.
        """
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.get_resource_headers()
        r = requests.get(endpoint, headers=headers)
        
        if r.status_code in range (200, 299):
            return r.json()
        else:
            return {}
    
    def get_album(self, _id):
        """
        Returns a dictionary containing the album stored with the specified id.

        :param id: The id which an album is stored.
        :return: A dictionary containing the specified album. Returns an empty dictionary if the specified album is not found.
        """
        return self.get_resource(_id, resource_type="albums")
    
    def get_artist(self, _id):
        """
        Returns a dictionary containing the artist stored with the specified id.

        :param id: The id which an artist is stored.
        :return: A dictionary containing the specified artist. Returns an empty dictionary if the specified artist is not found.
        """
        return self.get_resource(_id, resource_type="artists")
        
    def base_search(self, query_params):
        """
        Performs a search in the Spotify API with the passed query parameters and returns the query results.

        :param query_parameters: The parameters to be used in the search query (see https://developer.spotify.com/documentation/web-api/reference/search/search/#query-parameters).
        :return: A dictionary containing the result of the search query.
        """
        headers = self.get_resource_headers()
        
        endpoint = "https://api.spotify.com/v1/search"

        lookup_url = f"{endpoint}?{query_params}"

        r = requests.get(lookup_url, headers=headers)
        
        if r.status_code in range(200, 299):
            return r.json()
        else:
            print(r.status_code)
            return {}
        
    def search(self, query=None, operator=None, operator_query=None, search_type="track"):
        """
        Performs a search in the Spotify API with the passed query and returns the query results.

        :param query: Keywords to be used in the search or a dictionary containing field filters (e.g. {'artist': 'John Mayer', 'track': 'New Light'}).
        :param operator: Either "NOT" to exclude results or "OR" to expand results.s
        :param operator_query: The query which the operator uses to modify the base query.
        :param search_type: The type of outputs to be received (valid types are: album, artist, playlist, track, show and episode).
        :return: A dictionary containing the result of the search.
        """
        if query == None:
            raise Exception("A query is required")
        
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
            
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        
        query_params = {
            "q": query,
            "type": search_type.lower(),
            "limit": 50
        }
        
        query_params = urlencode(query_params)
        
        return self.base_search(query_params)

    def get_queue_headers(self):
        """
        Returns a dictionary holding the header values to be used in a query to add a track to the user's queue.

        :return: The headers arguments to be used when making a request to add to a user's queue.
        """
        token = self.get_access_token("authorization_code")

        headers = {
            "Authorization": f"Bearer {token}"
        }

        return headers

    def get_queue_params(self, uri):
        """
        Returns a dictionary holding the paramater values to be used in a query to add a track with the passed URI to the user's queue.

        :param uri: The URI of a track to be added to the user's queue.
        :return: The params arguments to be used when making a request to add to a user's queue.
        """
        return {
            "uri": uri
        }

    def add_to_queue(self, uri):
        """
        Adds the track held at the passed URI to the user queue.

        :param uri: The URI of a track to be added to the user's queue.
        """
        endpoint = "https://api.spotify.com/v1/me/player/queue"
        params = self.get_queue_params(uri)
        headers = self.get_queue_headers()

        r = requests.post(endpoint, params=params, headers=headers)
        
        valid_request = r.status_code in range(200, 299)

        if not valid_request:
            error_code = r.status_code

            reason = r.reason

            if error_code == 404:
                reason = "Connection not made, please launch your Spotify application"

            print("%d ERROR: %s" % (error_code, reason))

    def get_first_track_uri(self, track_search_json):
        """
        Returns the URI of the first track stored in the passed JSON object returned from a track search query.

        :param track_search_json: The JSON object returned from a track search.
        :return: The URI of the first track held in the passed JSON object.
        """
        return track_search_json["tracks"]["items"][0]["uri"]
