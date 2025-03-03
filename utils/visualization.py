import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def prepare_activity_data(activities):
    """
    Convert activities data to a DataFrame and prepare for visualization
    """
    if not activities or len(activities) == 0:
        return pd.DataFrame()
    
    # Convert to DataFrame
    df = pd.DataFrame(activities)
    
    # Convert timestamp strings to datetime objects
    if 'start_date' in df.columns:
        df['start_date'] = pd.to_datetime(df['start_date'])
        df['date'] = df['start_date'].dt.date
        df['month'] = df['start_date'].dt.month
        df['year'] = df['start_date'].dt.year
        df['day_of_week'] = df['start_date'].dt.dayofweek
        df['week'] = df['start_date'].dt.isocalendar().week
        df['week_year'] = df['start_date'].dt.isocalendar().year
        # Create a week identifier (year + week)
        df['week_id'] = df['week_year'].astype(str) + '-' + df['week'].astype(str).str.zfill(2)
    
    # Convert distances from meters to kilometers
    if 'distance' in df.columns:
        df['distance_km'] = df['distance'] / 1000
    
    # Convert moving_time and elapsed_time from seconds to minutes
    if 'moving_time' in df.columns:
        df['moving_time_min'] = df['moving_time'] / 60
    
    if 'elapsed_time' in df.columns:
        df['elapsed_time_min'] = df['elapsed_time'] / 60
        
    # Calculate velocity (km/h) if we have both distance and time
    if 'distance' in df.columns and 'moving_time' in df.columns:
        # Convert to km/h: (meters/1000) / (seconds/3600)
        df['velocity_kmh'] = (df['distance'] / 1000) / (df['moving_time'] / 3600)
    
    return df

def create_weekly_volume_chart(df):
    """
    Create a line chart showing weekly volume (total distance) over time
    """
    if df.empty or 'distance_km' not in df.columns or 'week_id' not in df.columns:
        return go.Figure()
    
    # Group by week and sum distances
    weekly_volume = df.groupby(['week_year', 'week', 'week_id'])['distance_km'].sum().reset_index()
    
    # Create a proper date for each week (using the first day of each week)
    weekly_volume['week_date'] = weekly_volume.apply(
        lambda x: datetime.strptime(f"{int(x['week_year'])}-{int(x['week'])}-1", "%Y-%W-%w"), axis=1
    )
    weekly_volume = weekly_volume.sort_values('week_date')
    
    fig = px.line(
        weekly_volume,
        x='week_date',
        y='distance_km',
        title='Weekly Volume Over Time',
        labels={
            'week_date': 'Week',
            'distance_km': 'Total Distance (km)'
        }
    )
    
    # Add markers
    fig.update_traces(mode='lines+markers')
    
    return fig

def create_weekly_velocity_chart(df):
    """
    Create a line chart showing average weekly velocity over time
    """
    if df.empty or 'velocity_kmh' not in df.columns or 'week_id' not in df.columns:
        return go.Figure()
    
    # Group by week and calculate average velocity
    weekly_velocity = df.groupby(['week_year', 'week', 'week_id'])['velocity_kmh'].mean().reset_index()
    
    # Create a proper date for each week (using the first day of each week)
    weekly_velocity['week_date'] = weekly_velocity.apply(
        lambda x: datetime.strptime(f"{int(x['week_year'])}-{int(x['week'])}-1", "%Y-%W-%w"), axis=1
    )
    weekly_velocity = weekly_velocity.sort_values('week_date')
    
    fig = px.line(
        weekly_velocity,
        x='week_date',
        y='velocity_kmh',
        title='Average Weekly Velocity Over Time',
        labels={
            'week_date': 'Week',
            'velocity_kmh': 'Average Velocity (km/h)'
        }
    )
    
    # Add markers
    fig.update_traces(mode='lines+markers')
    
    return fig 