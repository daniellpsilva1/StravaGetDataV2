import os
import time
import requests
from dotenv import load_dotenv
from utils.db import get_user, save_user

# Load environment variables
load_dotenv()

# Strava API endpoints
AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

# Strava client info
CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")

def get_auth_url(redirect_uri):
    """
    Generate Strava authorization URL
    """
    scope = "read,activity:read_all"
    return f"{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={redirect_uri}&scope={scope}&approval_prompt=force"

def exchange_code_for_token(code):
    """
    Exchange authorization code for access token
    """
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(TOKEN_URL, data=payload)
    if response.status_code != 200:
        return None
    
    token_data = response.json()
    return {
        'user_id': token_data['athlete']['id'],
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token'],
        'expires_at': token_data['expires_at']
    }

def refresh_access_token(refresh_token):
    """
    Refresh the access token using the refresh token
    """
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    
    response = requests.post(TOKEN_URL, data=payload)
    if response.status_code != 200:
        return None
    
    token_data = response.json()
    return {
        'access_token': token_data['access_token'],
        'refresh_token': token_data['refresh_token'],
        'expires_at': token_data['expires_at']
    }

def get_valid_token(user_id):
    """
    Get a valid access token, refreshing if necessary
    """
    user = get_user(user_id)
    if not user:
        return None
    
    # Check if token is expired
    current_time = int(time.time())
    
    # If token is valid, return it
    if user['expires_at'] > current_time + 60:  # Add buffer of 60 seconds
        return user['access_token']
    
    # Token is expired, refresh it
    token_data = refresh_access_token(user['refresh_token'])
    if not token_data:
        return None
    
    # Save the new token data
    save_user(user_id, token_data['access_token'], token_data['refresh_token'], token_data['expires_at'])
    
    return token_data['access_token']

def get_activities(user_id, page=1, per_page=50):
    """
    Fetch activities from Strava API
    """
    access_token = get_valid_token(user_id)
    if not access_token:
        return None
    
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'page': page, 'per_page': per_page}
    
    response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
    if response.status_code != 200:
        return None
    
    return response.json() 