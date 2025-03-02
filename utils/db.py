import os
from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

def get_database():
    """
    Create a connection to MongoDB and return the database
    """
    try:
        # First try to get from streamlit secrets
        if hasattr(st, "secrets") and "MONGO_URI" in st.secrets:
            mongo_uri = st.secrets["MONGO_URI"]
        else:
            # Fall back to env variable
            mongo_uri = os.getenv("MONGO_URI")
        
        # Display connection status message
        st.sidebar.info("Connecting to MongoDB...")
        
        client = MongoClient(mongo_uri)
        
        # Force a connection to verify it works
        client.admin.command('ping')
        
        st.sidebar.success("✅ Connected to MongoDB")
        return client.strava_data
    except Exception as e:
        st.sidebar.error(f"❌ MongoDB Connection Error: {str(e)}")
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        # Create an in-memory fallback for demo purposes
        st.warning("Using in-memory storage instead. Data will not persist after closing the app.")
        return None

def save_user(user_id, access_token, refresh_token, expires_at):
    """
    Save or update user authentication details
    """
    db = get_database()
    if db is None:
        # Store in session state as fallback
        if 'users' not in st.session_state:
            st.session_state.users = {}
        
        st.session_state.users[user_id] = {
            "user_id": user_id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at
        }
        return
    
    users = db.users
    
    user_data = {
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }
    
    # Update if exists, insert if not
    users.update_one(
        {"user_id": user_id}, 
        {"$set": user_data}, 
        upsert=True
    )

def get_user(user_id):
    """
    Retrieve user authentication details
    """
    db = get_database()
    if db is None:
        # Retrieve from session state
        if 'users' in st.session_state and user_id in st.session_state.users:
            return st.session_state.users[user_id]
        return None
    
    users = db.users
    return users.find_one({"user_id": user_id})

def get_all_user_ids():
    """
    Retrieve all user IDs from the database
    """
    db = get_database()
    if db is None:
        # Retrieve from session state
        if 'users' in st.session_state:
            return list(st.session_state.users.keys())
        return []
    
    users = db.users
    user_records = users.find({}, {"user_id": 1})
    return [user["user_id"] for user in user_records]

def save_activities(user_id, activities):
    """
    Save user's activities to database
    """
    db = get_database()
    if db is None:
        # Store in session state as fallback
        if 'activities' not in st.session_state:
            st.session_state.activities = {}
        
        if user_id not in st.session_state.activities:
            st.session_state.activities[user_id] = []
        
        # Add user_id to each activity and store in session
        for activity in activities:
            activity["user_id"] = user_id
            # Use activity id as key
            activity_id = activity["id"]
            
            # Check if it exists already
            exists = False
            for i, existing in enumerate(st.session_state.activities[user_id]):
                if existing.get("id") == activity_id:
                    st.session_state.activities[user_id][i] = activity
                    exists = True
                    break
            
            if not exists:
                st.session_state.activities[user_id].append(activity)
        
        return len(activities)
    
    activities_collection = db.activities
    
    for activity in activities:
        # Add user_id to each activity for reference
        activity["user_id"] = user_id
        
        # Update if exists, insert if not
        activities_collection.update_one(
            {"id": activity["id"]},
            {"$set": activity},
            upsert=True
        )
    
    return len(activities)

def get_user_activities(user_id):
    """
    Retrieve all activities for a specific user
    """
    db = get_database()
    if db is None:
        # Retrieve from session state
        if 'activities' in st.session_state and user_id in st.session_state.activities:
            return st.session_state.activities[user_id]
        return []
    
    activities_collection = db.activities
    return list(activities_collection.find({"user_id": user_id})) 