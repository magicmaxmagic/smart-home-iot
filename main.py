import streamlit as st
import plotly.graph_objects as go
from data import get_accelerator_data, get_alarm_data

# --- Charger les données ---
data = get_accelerator_data()
print(data)  # ← Ajoute ceci pour déboguer
alarms = get_alarm_data()

st.set_page_config(page_title="Connected Door Dashboard", layout="wide")
st.title("Connected Door Dashboard")

if data is None or data.empty:
    st.error("Aucune donnée capteur disponible.")
    st.stop()

if alarms is None or alarms.empty:
    st.warning("Aucune donnée d'alarme disponible.")

# --- État actuel ---
st.header("Current State")
col1, col2 = st.columns(2)

current_state = data.iloc[-1]
door_open = current_state['z'] > 0.5
door_state_text = "Open" if door_open else "Closed"
door_state_color = "red" if door_open else "green"

col2.markdown(f"<h2 style='color: {door_state_color};'>Door: {door_state_text}</h2>", unsafe_allow_html=True)
col1.metric("People in", value=current_state["people_count"])

# --- Timeline porte ---
st.header("Door Open/Close Timeline")
colors = ['green' if z <= 0.5 else 'red' for z in data['z']]
fig_door = go.Figure(go.Bar(x=data.index, y=[1]*len(data), marker_color=colors))
fig_door.update_layout(yaxis=dict(showticklabels=False, range=[0, 1.2]), xaxis_title="Time")
st.plotly_chart(fig_door, use_container_width=True)

# --- Données accéléromètre ---
st.header("Accelerometer Data")
st.line_chart(data[['x', 'y', 'z']])

# --- Données d’alarme ---
if alarms is not None and not alarms.empty:
    st.header("Alarm Events")

    st.dataframe(alarms)

    st.subheader("Intrusion Timeline")
    intrusion_data = alarms[alarms['alarm_state'] == 'INTRUSION']
    if not intrusion_data.empty:
        fig_intrusion = go.Figure(go.Scatter(
            x=intrusion_data.index,
            y=[1]*len(intrusion_data),
            mode='markers',
            marker=dict(size=10, color='red'),
            name="INTRUSION"
        ))
        fig_intrusion.update_layout(yaxis=dict(showticklabels=False), xaxis_title="Time")
        st.plotly_chart(fig_intrusion, use_container_width=True)
    else:
        st.info("Aucune intrusion détectée.")