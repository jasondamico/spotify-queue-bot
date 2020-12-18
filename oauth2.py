import base64
import datetime
from urllib.parse import urlencode

import requests

class SpotifyAPIOAuth2(object):
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
    
    def get_token_data(self, auth_code=False):
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
