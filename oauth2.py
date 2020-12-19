import base64
import datetime
from urllib.parse import urlencode
import webbrowser
import urllib.parse as urllibparse
from urllib.parse import parse_qs

import requests

class SpotifyAPIOAuth2(object):
    access_token = None
    access_token_expires = None
    auth_code = None
    redirect_uri = "http://jasondamico.me"
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"
    auth_code_url = "https://accounts.spotify.com/authorize"
    
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
    
    def get_token_data(self, auth_type):
        """
        Returns a dictionary containing the token data to be used in the post request to receive the client token URL.

        :return: The data to be used to make a request to retreive the token associated with this application.
        """
        data = {
            "grant_type": auth_type
        }

        if auth_type == "authorization_code":
            data["code"] = self.auth_code
            data["redirect_uri"] = self.redirect_uri

        return data
        
    def perform_auth(self, auth_type):     
        """ 
        Performs the authentication of the the client application based on the stored client id and client key. Returns TRUE if the authentication was successful, throws an exception otherwise.

        :param auth_type: A string representing which type of authentication should be performed. Two possible options are available at this time:
            - `"client_credentials"`
            - `"authorization_code"`
        :return: TRUE if the authentication was successful.
        """   
        if auth_type == "client_credentials":
            r = requests.post(self.token_url, data=self.get_token_data("client_credentials"), headers=self.get_token_headers())
        elif auth_type == "authorization_code":
            self.store_auth_code()

            r = requests.post(self.token_url, data=self.get_token_data("authorization_code"), headers=self.get_token_headers())
        else:
            raise Exception("Invalid authorization flow entered.")

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
        
    def get_access_token(self, auth_type):
        """
        Returns the valid authentication token stored within the object.

        :param auth_type: A string representing which type of authentication should be performed.
        :return: A valid authentication token that is presently stored within the object.
        """
        auth_done = self.perform_auth(auth_type)

        token = self.access_token
        
        if not auth_done:
            raise Exception("Authentication failed")
        
        now = datetime.datetime.now()
        
        if self.access_token_expires < now or token == None:
            self.perform_auth(auth_type)
            return self.get_access_token(auth_type)
        
        return token

    def get_auth_code_params(self):
        """
        Returns a dictionary containing the parameters to be used in obtaining the authorization code.

        :return: The parameters to be passed to the authorization code URL to obtain a user authorization code.
        """
        return {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "user-modify-playback-state",
            "state": 123
        }

    def store_auth_code(self):
        """
        Obtains (with the consent of the user) a user authorization code and stores it as an instance variable.

        :return: The authorization code obtained from the user.
        """
        url_params = urllibparse.urlencode(self.get_auth_code_params())
        auth_code_url = "%s?%s" % (self.auth_code_url, url_params)

        webbrowser.open(auth_code_url)
        uri = input("Please enter the URL you were redirected to: ")

        self.auth_code = self.get_code_from_uri(uri)

    def get_code_from_uri(self, uri):
        """
        Retrieves the code from the passed URI and returns the value.

        :return: The code stored within the passed URI.
        """
        parsed = urllibparse.urlparse(uri)

        return parse_qs(parsed.query)["code"][0]
