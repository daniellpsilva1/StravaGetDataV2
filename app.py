import os
import streamlit as st
import time
from urllib.parse import urlparse, parse_qs
import pandas as pd
from utils.db import save_user, get_user, save_activities, get_user_activities, get_all_user_ids
from utils.strava import get_auth_url, exchange_code_for_token, get_activities
from utils.visualization import (
    prepare_activity_data,
    create_activity_type_chart,
    create_distance_time_chart,
    create_weekly_activity_chart,
    create_monthly_distance_chart
)

# Page configuration
st.set_page_config(
    page_title="Strava Activity Dashboard",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'activities_loaded' not in st.session_state:
    st.session_state.activities_loaded = False
if 'offline_mode' not in st.session_state:
    st.session_state.offline_mode = False

# Check authentication from URL parameters (after Strava callback)
current_url = st.experimental_get_query_params()

if 'code' in current_url and not st.session_state.authenticated:
    with st.spinner('Authenticating with Strava...'):
        try:
            code = current_url['code'][0]  # Get the first value as query params are returned as lists
            token_data = exchange_code_for_token(code)
            
            if token_data:
                user_id = token_data['user_id']
                save_user(user_id, token_data['access_token'], token_data['refresh_token'], token_data['expires_at'])
                st.session_state.user_id = user_id
                st.session_state.authenticated = True
                
                # Clear URL parameters by rerunning the app
                st.success("Successfully authenticated with Strava!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Authentication failed. Please try again.")
        except Exception as e:
            st.error("Authentication error. Please try again.")

# Sidebar navigation
st.sidebar.title("Strava Dashboard")

# Offline mode toggle
offline_mode = st.sidebar.checkbox("Offline Mode", value=st.session_state.offline_mode)
if offline_mode != st.session_state.offline_mode:
    st.session_state.offline_mode = offline_mode
    st.rerun()

# User selector in offline mode
if st.session_state.offline_mode:
    user_ids = get_all_user_ids()
    if user_ids:
        selected_user = st.sidebar.selectbox(
            "Select User", 
            options=user_ids,
            index=0 if st.session_state.user_id not in user_ids else user_ids.index(st.session_state.user_id)
        )
        if selected_user != st.session_state.user_id:
            st.session_state.user_id = selected_user
            st.rerun()
    else:
        st.sidebar.warning("No users found in database")

page = st.sidebar.radio("Navigation", ["Home", "Get Data", "Visualizations"])

# Display user authentication status
if st.session_state.offline_mode:
    st.sidebar.info("📱 Offline Mode - Using stored data")
elif st.session_state.authenticated:
    st.sidebar.success("✅ Connected to Strava")
else:
    st.sidebar.warning("❌ Not connected to Strava")

# Home page
if page == "Home":
    st.title("Strava Activity Dashboard")
    st.write("This app allows you to retrieve your Strava activities and visualize them.")
    
    if st.session_state.offline_mode:
        st.info("You are in offline mode. You can view your previously saved data.")
        st.write("Use the sidebar to navigate to Visualizations.")
    elif not st.session_state.authenticated:
        st.write("To get started, connect your Strava account:")
        
        # Generate a redirect URL to this app
        redirect_uri = st.secrets.get("REDIRECT_URI", "http://localhost:8501")
        # For Streamlit Cloud, make sure we're using https
        if "streamlit.app" in redirect_uri and not redirect_uri.startswith("http"):
            redirect_uri = "https://" + redirect_uri
        
        auth_url = get_auth_url(redirect_uri)
        
        st.markdown(f"<a href='{auth_url}'><button style='background-color:#FC4C02; color:white; padding:10px; border-radius:5px; border:none;'>Connect with Strava</button></a>", unsafe_allow_html=True)
        st.markdown("""
        **Instructions:**
        1. Click the button above to connect with Strava
        2. Sign in to Strava if prompted
        3. Click the orange 'Authorize' button on the Strava page
        4. You will be redirected back to this app
        """)
    else:
        st.write("You are connected to Strava! Use the sidebar to navigate.")
        
        # Show a button to disconnect if needed
        if st.button("Disconnect from Strava"):
            st.session_state.user_id = None
            st.session_state.authenticated = False
            st.session_state.activities_loaded = False
            st.rerun()

# Get Data page
elif page == "Get Data":
    st.title("Get Data from Strava")
    
    if st.session_state.offline_mode:
        st.info("You are in offline mode. Switch to online mode to fetch new data from Strava.")
        
        # Check if any activities are in the database for the selected user
        if st.session_state.user_id:
            activities = get_user_activities(st.session_state.user_id)
            if activities and len(activities) > 0:
                st.success(f"{len(activities)} activities found in the database for the selected user.")
            else:
                st.warning("No activities found in the database for the selected user.")
    elif not st.session_state.authenticated:
        st.warning("You need to connect your Strava account first. Go to the Home page.")
    else:
        st.write("Fetch your activities from Strava and save them to the database.")
        
        col1, col2 = st.columns(2)
        with col1:
            # Option to set how many pages of activities to fetch
            max_pages = st.number_input("Number of pages to fetch (50 activities per page)", 
                                        min_value=1, max_value=10, value=2)
        
        with col2:
            # Fetch activities button
            if st.button("Fetch Activities"):
                activities_count = 0
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for page in range(1, max_pages + 1):
                    status_text.text(f"Fetching page {page} of {max_pages}...")
                    activities = get_activities(st.session_state.user_id, page=page)
                    
                    if activities and len(activities) > 0:
                        count = save_activities(st.session_state.user_id, activities)
                        activities_count += count
                    else:
                        break
                    
                    progress_bar.progress(page / max_pages)
                
                progress_bar.progress(1.0)
                status_text.text(f"Completed: Saved {activities_count} activities to the database.")
                st.session_state.activities_loaded = True

        # Check if any activities are in the database
        activities = get_user_activities(st.session_state.user_id)
        if activities and len(activities) > 0:
            st.success(f"{len(activities)} activities found in the database.")
        else:
            st.info("No activities found in the database. Click 'Fetch Activities' to get your data.")

# Visualizations page
elif page == "Visualizations":
    st.title("Activity Visualizations")
    
    if not st.session_state.offline_mode and not st.session_state.authenticated:
        st.warning("You need to connect your Strava account first or enable offline mode to view visualizations.")
    elif not st.session_state.user_id:
        st.warning("No user selected. Please select a user in offline mode or connect to Strava.")
    else:
        activities = get_user_activities(st.session_state.user_id)
        
        if not activities or len(activities) == 0:
            st.warning("No activities found. Go to the 'Get Data' page to fetch your activities.")
        else:
            # Prepare data for visualization
            df = prepare_activity_data(activities)
            
            # Display summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Activities", len(df))
            
            with col2:
                if 'distance_km' in df.columns:
                    total_distance = round(df['distance_km'].sum(), 2)
                    st.metric("Total Distance (km)", total_distance)
            
            with col3:
                if 'moving_time_min' in df.columns:
                    total_time = round(df['moving_time_min'].sum() / 60, 2)
                    st.metric("Total Time (hours)", total_time)
            
            with col4:
                if 'type' in df.columns:
                    activity_types = df['type'].nunique()
                    st.metric("Activity Types", activity_types)
            
            # Select visualization tab
            st.subheader("Visualizations")
            tab1, tab2, tab3, tab4 = st.tabs(["Activity Types", "Distance vs Time", "Weekly Activity", "Monthly Distance"])
            
            with tab1:
                st.plotly_chart(create_activity_type_chart(df), use_container_width=True)
            
            with tab2:
                st.plotly_chart(create_distance_time_chart(df), use_container_width=True)
            
            with tab3:
                st.plotly_chart(create_weekly_activity_chart(df), use_container_width=True)
            
            with tab4:
                st.plotly_chart(create_monthly_distance_chart(df), use_container_width=True)

if __name__ == "__main__":
    # Run the app
    pass 