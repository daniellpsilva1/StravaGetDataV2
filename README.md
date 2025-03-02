# Strava Activity Dashboard

A Streamlit web application that integrates with the Strava API to fetch, store, and visualize your activity data.

## Features

- Connect to your Strava account using OAuth2 authentication
- Fetch your activities from Strava and store them in MongoDB
- Visualize your activity data with interactive charts:
  - Activity type distribution
  - Distance vs. time scatter plot
  - Weekly activity frequency
  - Monthly distance trends

## Requirements

- Python 3.7+
- A Strava account
- A Strava API application (for client ID and secret)

## Setup Instructions

1. **Clone this repository**

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **Create a Strava API Application**
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Create an application to get a Client ID and Client Secret
   - Set the "Authorization Callback Domain" to localhost (for local development) or your deployed app domain

4. **Set up environment variables**
   - Update the `.env` file with your Strava API credentials:
     ```
     STRAVA_CLIENT_ID=your_client_id
     STRAVA_CLIENT_SECRET=your_client_secret
     MONGO_URI=mongodb+srv://dssportsanalytics:dssportsanalytics@stravagetdatav2.swqpe.mongodb.net/?retryWrites=true&w=majority&appName=StravaGetDataV2
     ```

5. **Run the Streamlit app**
   ```
   streamlit run app.py
   ```

6. **Open the app in your browser**
   - The app will be available at http://localhost:8501

## Usage

1. **Home Page**: Connect your Strava account
2. **Get Data**: Fetch your activities from Strava and save them to MongoDB
3. **Visualizations**: View interactive charts and statistics of your activities

## Deployment

For production deployment, you can:
- Deploy on [Streamlit Cloud](https://streamlit.io/cloud)
- Deploy on [Heroku](https://www.heroku.com/)
- Run on any server with Python installed

When deploying, make sure to:
1. Set the appropriate Strava redirect URI in your Strava API application
2. Set the `REDIRECT_URI` in Streamlit secrets or environment variables

## Deployment on Streamlit Cloud

1. **Create a Streamlit Cloud account**
   - Sign up at [Streamlit Cloud](https://streamlit.io/cloud)

2. **Deploy the app**
   - Connect your GitHub repository
   - Select the repository and branch
   - Set the main file path to `app.py`

3. **Configure Secrets**
   - In the Streamlit Cloud dashboard, navigate to your app settings
   - Under "Secrets", add the following configuration (replace with your values):
   ```toml
   STRAVA_CLIENT_ID = "your_strava_client_id"
   STRAVA_CLIENT_SECRET = "your_strava_client_secret"
   REDIRECT_URI = "https://your-app-url.streamlit.app"
   MONGO_URI = "your_mongodb_connection_string"
   ```
   
4. **Update Strava API Settings**
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Update the "Authorization Callback Domain" to your Streamlit Cloud domain
   - The format will be: `your-app-name.streamlit.app`

5. **Reboot the app**
   - After configuring secrets, click "Reboot app" in the Streamlit Cloud dashboard

## License

MIT

## Acknowledgements

- [Strava API](https://developers.strava.com/)
- [Streamlit](https://streamlit.io/)
- [MongoDB](https://www.mongodb.com/)
- [Plotly](https://plotly.com/) 