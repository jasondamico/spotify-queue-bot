import base64
import datetime
from urllib.parse import urlencode

import requests

class SpotifyAPI(object):
    access_token = None
    access_token_expires = None
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    
    def __init__(self, client_id, client_secret, *args, **kwargs):
        """
        Paramaterized constructor: initializes a SpotifyAPI object with the specified client ID and client secret.

        :param client_id: The id associated with the registered Spotify application.
        :param client_secret: The secret key associated with the registered Spotify application.
        """
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret
        
    def get_client_credentials(self):
        """
        Returns a base64 encoded string based on the stored client id and client secret key. Throws an exception if the client id or client key is not set.

        :return: A base64 encoded string containing the client secret key and client id.
        """
        if self.client_id == None or self.client_secret == None:
            raise Exception("You must set client_id and client_secret.")
        else:        
            client_creds = f"{self.client_id}:{self.client_secret}"
            client_creds_b64 = base64.b64encode(client_creds.encode())
            return client_creds_b64.decode()
    
    def get_token_headers(self):
        """
        Returns a dictionary containing the header for retreiving the token associated with this application.

        :param: The header to be passed as a parameter to the post function retreiving the client token.
        """
        client_creds_b64 = self.get_client_credentials()
        
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }
    
    def get_token_data(self):
        """
        Returns a dictionary containing the token data to be used in the post request to receive the client token URL.

        :return: The data to be used to make a request to retreive the token associated with this application.
        """
        return {
            "grant_type": "client_credentials"
        }
        
    def perform_auth(self):     
        """ 
        Performs the authentication of the the client application based on the stored client id and client key. Returns TRUE if the authentication was successful, throws an exception otherwise.

        :return: TRUE if the authentication was successful.
        """   
        r = requests.post(self.token_url, data=self.get_token_data(), headers=self.get_token_headers())
        valid_request = r.status_code in range(200, 299)

        if valid_request:
            data = r.json()
            now = datetime.datetime.now()
            self.access_token = data["access_token"]
            expires_in = data["expires_in"]  # seconds
            self.access_token_expires = now + datetime.timedelta(seconds=expires_in)
            self.access_token_did_expire = self.access_token_expires < now
            
            return True
        else:
            raise Exception("Could not authenticate client.")
        
    def get_access_token(self):
        """
        Returns the valid authentication token stored within the object.

        :return: A valid authentication token that is presently stored within the object.
        """
        token = self.access_token
        
        auth_done = self.perform_auth()
        
        if not auth_done:
            raise Exception("Authentication failed")
        
        now = datetime.datetime.now()
        
        if self.access_token_expires < now or token == None:
            self.perform_auth()
            return self.get_access_token()
        
        return token
    
    def get_resource_headers(self):
        """
        Returns the header to be used when retreiving resources from the Spotify API.

        :return: A dictionary to be passed to the post function when retreiving resources from the API.
        """
        headers = {
            "Authorization": f"Bearer {self.get_access_token()}"
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

        print(r.status_code)
        
        if r.status_code in range(200, 299):
            return r.json()
        else:
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
        
        print(query_params)
        
        return self.base_search(query_params)
