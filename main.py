import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- Simulated Data Generation ---
def generate_door_data(num_points=100):
    time_index = pd.date_range(end=datetime.now(), periods=num_points, freq='1min')
    open_close = np.random.choice([0, 1], size=num_points)  # 0: closed, 1: open
    temperature = np.random.uniform(18, 25, size=num_points) + np.sin(np.linspace(0, 10, num_points)) * 2
    accelerometer_x = np.random.normal(0, 0.1, size=num_points)
    accelerometer_y = np.random.normal(0, 0.1, size=num_points)
    accelerometer_z = np.random.normal(9.8, 0.1, size=num_points)  # Simulate gravity in z-axis
    df = pd.DataFrame({
        'time': time_index,
        'open_close': open_close,
        'temperature': temperature,
        'acc_x': accelerometer_x,
        'acc_y': accelerometer_y,
        'acc_z': accelerometer_z,
    })
    return df

data = generate_door_data()

# --- Streamlit App ---
st.set_page_config(page_title="Connected Door Dashboard", layout="wide")

st.title("Connected Door Dashboard")

# --- Current State ---
st.header("Current State")
col1, col2 = st.columns(2)

current_state = data.iloc[-1]

# Temperature Gauge
fig_gauge = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = current_state['temperature'],
    mode = "gauge+number",
    title = {'text': "Temperature (°C)"},
    gauge = {'axis': {'range': [min(data['temperature']), max(data['temperature'])]},
             'bar': {'color': "darkblue"},
             'steps' : [
                 {'range': [min(data['temperature']), (min(data['temperature'])+max(data['temperature']))/2], 'color': "lightgray"},
                 {'range': [(min(data['temperature'])+max(data['temperature']))/2, max(data['temperature'])], 'color': "gray"}]}))

col1.plotly_chart(fig_gauge, use_container_width=True)

# Door Status (Conditional Formatting)
if current_state['open_close'] == 1:
    col2.markdown(f"<h2 style='color: red;'>Door: Open</h2>", unsafe_allow_html=True)
else:
    col2.markdown(f"<h2 style='color: green;'>Door: Closed</h2>", unsafe_allow_html=True)

# --- Door Open/Close Timeline (Bar Chart) ---
st.header("Door Open/Close Timeline")

fig_door_bar = go.Figure()

colors = ['green' if status == 0 else 'red' for status in data['open_close']]

fig_door_bar.add_trace(go.Bar(x=data['time'], y=[1]*len(data), marker_color=colors, name='Door State'))

fig_door_bar.update_layout(yaxis=dict(showticklabels=False, range=[0, 1.2]), xaxis_title="Time", yaxis_title="")

st.plotly_chart(fig_door_bar, use_container_width=True)

# --- Temperature Timeline ---
st.header("Temperature Timeline")

fig_temp = go.Figure()
fig_temp.add_trace(go.Scatter(x=data['time'], y=data['temperature'], mode='lines', name='Temperature',
                             line=dict(color='red')))
fig_temp.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)")
st.plotly_chart(fig_temp, use_container_width=True)

# --- Stats Page (Raw Sensor Data) ---
st.header("Sensor Data")

if st.checkbox("Show Raw Sensor Data"):
    st.subheader("Accelerometer Data")
    st.line_chart(data[['time','acc_x', 'acc_y', 'acc_z']].set_index('time'))

    st.subheader("Temperature Data")
    st.line_chart(data[['time','temperature']].set_index('time'))
    st.subheader("Raw sensor data table")
    st.dataframe(data)