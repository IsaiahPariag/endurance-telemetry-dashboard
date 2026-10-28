import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Endurance Telemetry & Workload Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Endurance Telemetry & Athletic Workload Platform")
st.caption("Quantitative physiological telemetry, workload distributions, and overtraining risk modeling.")
st.write("")

@st.cache_data
def load_data():
    file_path = "data/processed/clean_telemetry.csv"
    if not os.path.exists(file_path):
        st.error(f"Processed telemetry file not found at {file_path}.")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

df = load_data()

if not df.empty:
    st.sidebar.subheader("Parameters")
    
    activity_types = sorted(df['type'].unique().tolist())
    selected_types = st.sidebar.multiselect(
        "Activity Classification",
        options=activity_types,
        default=activity_types
    )
    
    min_date = df['date'].min().to_pydatetime()
    max_date = df['date'].max().to_pydatetime()
    
    date_range = st.sidebar.date_input(
        "Observation Period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_filter, end_filter = date_range
        filtered_df = df[
            (df['type'].isin(selected_types)) &
            (df['date'] >= pd.to_datetime(start_filter)) &
            (df['date'] <= pd.to_datetime(end_filter))
        ]
    else:
        filtered_df = df[df['type'].isin(selected_types)]
    
    st.subheader("Primary Metrics")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_miles = round(filtered_df['distance_miles'].sum(), 1)
    avg_hr = int(filtered_df['avg_heart_rate'].mean()) if not filtered_df.empty else 0
    avg_pace_sec = filtered_df['pace_seconds_per_mile'].mean() if not filtered_df.empty else 0
    avg_pace_formatted = f"{int(avg_pace_sec // 60)}:{int(avg_pace_sec % 60):02d} /mi"
    
    latest_acwr = filtered_df.sort_values('date').iloc[-1]['acwr'] if not filtered_df.empty else 0.0
    acwr_status = "Optimal" if 0.8 <= latest_acwr <= 1.3 else ("Fatigue Risk" if latest_acwr > 1.3 else "Under-training")
    
    kpi1.metric("Cumulative Mileage", f"{total_miles} mi")
    kpi2.metric("Mean Session Pace", avg_pace_formatted)
    kpi3.metric("Mean Heart Rate", f"{avg_hr} bpm")
    kpi4.metric("Acute:Chronic Ratio", f"{latest_acwr}", delta=acwr_status)
    
    st.write("")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Pacing Distribution")
        fig_pace = px.scatter(
            filtered_df,
            x="date",
            y="pace_seconds_per_mile",
            color="type",
            size="distance_miles",
            hover_data=["pace_formatted", "avg_heart_rate", "distance_miles"],
            labels={"pace_seconds_per_mile": "Pace (Seconds/Mile)", "date": "Date", "type": "Type"},
            template="plotly_white"
        )
        fig_pace.update_yaxes(autorange="reversed")
        fig_pace.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_pace, use_container_width=True)
        
    with col_right:
        st.subheader("Acute:Chronic Workload Ratio")
        fig_acwr = go.Figure()
        
        # Transparent optimal zone
        fig_acwr.add_hrect(
            y0=0.8, y1=1.3,
            line_width=0,
            fillcolor="gray",
            opacity=0.12,
            annotation_text="Optimal Zone (0.8 - 1.3)",
            annotation_position="top left"
        )
        
        fig_acwr.add_hline(
            y=1.5,
            line_dash="dot",
            line_color="red",
            opacity=0.6,
            annotation_text="Spike Threshold (1.5)",
            annotation_position="bottom right"
        )
        
        fig_acwr.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df['acwr'],
            mode='lines+markers',
            name='ACWR',
            line=dict(width=2)
        ))
        
        fig_acwr.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0.4, 2.0]),
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_acwr, use_container_width=True)
        
    with st.expander("Tabular Records"):
        table_df = filtered_df[[
            'date', 'type', 'distance_miles', 'pace_formatted', 
            'avg_heart_rate', 'elevation_gain_ft', 'acwr'
        ]].sort_values('date', ascending=False)
        st.dataframe(table_df, use_container_width=True, hide_index=True)