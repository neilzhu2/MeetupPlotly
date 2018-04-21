from secrets import *
from requests_oauthlib import OAuth1Session


protected_url = 'https://api.meetup.com'

api_param = {'key': api_key}

def OAuthorize():
    #1.0 GET A REQUEST TOKEN
    request_token_url = 'https://api.meetup.com/oauth/request/'
    oauth = OAuth1Session(client_key, client_secret = client_secret)
    fetch_response = oauth.fetch_request_token(request_token_url)
    resource_request_key = fetch_response.get('oauth_token')
    resource_request_secret = fetch_response.get('oauth_token_secret')

    #1.1 GET AUTHORIZATION FROM THE USER
    base_authorization_url = 'https://secure.meetup.com/authorize/'
    authorization_url = oauth.authorization_url(base_authorization_url) #, oauth_callback = "http://neil-zhu2.appspot.com"
    print ('\nPlease go here and authorize:\n', authorization_url, '\n')
    verifier = input('Type anything after authorization: ')

    #1.2 GET ACCESS TOKEN
    access_token_url = 'https://api.meetup.com/oauth/access/'
    oauth = OAuth1Session(client_key,
                              client_secret=client_secret,
                              resource_owner_key=resource_request_key,
                              resource_owner_secret=resource_request_secret,
                              verifier=verifier)
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    resource_access_key = oauth_tokens.get('oauth_token')
    resource_access_secret = oauth_tokens.get('oauth_token_secret')

    #1.3 FINAL AUTHORIZE
    oauth = OAuth1Session(client_key,
                              client_secret=client_secret,
                              resource_owner_key=resource_access_key,
                              resource_owner_secret=resource_access_secret)
