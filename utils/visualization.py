import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

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
    
    # Convert distances from meters to kilometers
    if 'distance' in df.columns:
        df['distance_km'] = df['distance'] / 1000
    
    # Convert moving_time and elapsed_time from seconds to minutes
    if 'moving_time' in df.columns:
        df['moving_time_min'] = df['moving_time'] / 60
    
    if 'elapsed_time' in df.columns:
        df['elapsed_time_min'] = df['elapsed_time'] / 60
    
    return df

def create_activity_type_chart(df):
    """
    Create a pie chart showing distribution of activity types
    """
    if df.empty or 'type' not in df.columns:
        return go.Figure()
    
    type_counts = df['type'].value_counts().reset_index()
    type_counts.columns = ['Activity Type', 'Count']
    
    fig = px.pie(
        type_counts, 
        values='Count', 
        names='Activity Type',
        title='Distribution of Activity Types'
    )
    return fig

def create_distance_time_chart(df):
    """
    Create a scatter plot of distance vs. moving time
    """
    if df.empty or 'distance_km' not in df.columns or 'moving_time_min' not in df.columns:
        return go.Figure()
    
    fig = px.scatter(
        df, 
        x='distance_km', 
        y='moving_time_min',
        color='type',
        hover_data=['name', 'start_date'],
        title='Distance vs. Moving Time',
        labels={
            'distance_km': 'Distance (km)',
            'moving_time_min': 'Moving Time (min)',
            'type': 'Activity Type'
        }
    )
    return fig

def create_weekly_activity_chart(df):
    """
    Create a bar chart showing activity frequency by day of week
    """
    if df.empty or 'day_of_week' not in df.columns:
        return go.Figure()
    
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df['day_of_week'].value_counts().reindex(range(7)).fillna(0)
    day_counts.index = days
    
    fig = px.bar(
        x=day_counts.index, 
        y=day_counts.values,
        title='Activity Frequency by Day of Week',
        labels={'x': 'Day of Week', 'y': 'Number of Activities'}
    )
    return fig

def create_monthly_distance_chart(df):
    """
    Create a line chart showing total distance by month
    """
    if df.empty or 'month' not in df.columns or 'distance_km' not in df.columns:
        return go.Figure()
    
    # Group by month and year, and sum the distances
    monthly_distance = df.groupby(['year', 'month'])['distance_km'].sum().reset_index()
    monthly_distance['month_year'] = monthly_distance.apply(
        lambda x: datetime(int(x['year']), int(x['month']), 1), axis=1
    )
    monthly_distance = monthly_distance.sort_values('month_year')
    
    fig = px.line(
        monthly_distance,
        x='month_year',
        y='distance_km',
        title='Total Distance by Month',
        labels={
            'month_year': 'Month',
            'distance_km': 'Total Distance (km)'
        }
    )
    return fig 