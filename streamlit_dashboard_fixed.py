#!/usr/bin/env python3
"""
BHIV Analytics - Fixed Dashboard
"""

import streamlit as st
import requests
import plotly.graph_objects as go
import time
from datetime import datetime

# Page config
st.set_page_config(
    page_title="BHIV Analytics",
    page_icon="🚀",
    layout="wide"
)

def fetch_data():
    """Fetch all data with error handling"""
    try:
        # Analytics data
        response = requests.get('http://127.0.0.1:9000/bhiv/analytics', timeout=5)
        analytics = response.json() if response.status_code == 200 else {}
        
        # System metrics
        response = requests.get('http://127.0.0.1:9000/metrics', timeout=5)
        metrics = response.json() if response.status_code == 200 else {}
        
        # Task queue stats
        response = requests.get('http://127.0.0.1:9000/tasks/queue/stats', timeout=5)
        tasks = response.json() if response.status_code == 200 else {}
        
        return {
            'analytics': analytics,
            'metrics': metrics,
            'tasks': tasks,
            'api_connected': bool(analytics or metrics)
        }
    except:
        return {
            'analytics': {},
            'metrics': {},
            'tasks': {},
            'api_connected': False
        }

def main():
    # Fetch data
    data = fetch_data()
    analytics = data['analytics']
    metrics = data['metrics']
    tasks = data['tasks']
    api_connected = data['api_connected']
    
    # Header
    st.markdown("# 🚀 BHIV Analytics Dashboard")
    st.markdown("Advanced AI-Powered Content Analytics Platform")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Dashboard Controls")
        if st.button("🔄 Refresh"):
            st.rerun()
        
        st.markdown("### 📡 System Status")
        if api_connected:
            st.success("🟢 API Connected")
        else:
            st.error("🔴 API Disconnected")
    
    # Get values safely
    total_users = analytics.get('total_users', 0)
    total_content = analytics.get('total_content', 0)
    total_feedback = analytics.get('total_feedback', 0)
    avg_rating = analytics.get('average_rating', 0.0)
    
    # Task queue values
    task_stats = tasks.get('queue_stats', tasks)
    total_tasks = task_stats.get('total_tasks', 0)
    pending_tasks = task_stats.get('pending_queue_size', 0)
    
    # Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("👥 Total Users", total_users)
    
    with col2:
        st.metric("📱 Content Items", total_content)
    
    with col3:
        st.metric("💬 Feedback Count", total_feedback)
    
    with col4:
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5.0")
    
    with col5:
        st.metric("⚙️ Task Queue", total_tasks)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Simple sentiment chart
        sentiment_data = analytics.get('sentiment_breakdown', {'Positive': 1})
        if sentiment_data:
            fig = go.Figure(data=[go.Pie(
                labels=list(sentiment_data.keys()),
                values=list(sentiment_data.values()),
                hole=0.6
            )])
            fig.update_layout(title="🧠 AI Sentiment Analysis")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Simple engagement gauge
        engagement_rate = max(0, min(100, analytics.get('engagement_rate', 0)))
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=engagement_rate,
            title={'text': "📈 Engagement Rate"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Task Queue Section
    st.markdown("### ⚙️ Task Queue Management")
    
    if api_connected and tasks:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Queue Overview**")
            st.markdown(f"- Total Tasks: {total_tasks}")
            st.markdown(f"- Pending: {pending_tasks}")
        
        with col2:
            st.markdown("**⚡ Worker Status**")
            workers_started = task_stats.get('workers_started', False)
            status = "🟢 Active" if workers_started else "🔴 Inactive"
            st.markdown(f"- Workers: {status}")
        
        with col3:
            st.markdown("**📈 Status**")
            st.markdown("- Queue Type: Async")
            st.markdown("- Max Concurrent: 2")
    else:
        st.warning("⚠️ Task Queue API not available. Make sure the FastAPI server is running.")
    
    # Status info
    st.markdown("---")
    if api_connected:
        st.success("✅ Dashboard connected to API")
    else:
        st.error("❌ Dashboard not connected to API - Check if server is running on port 9000")
    
    st.markdown(f"⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()