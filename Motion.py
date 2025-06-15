import streamlit as st
import paho.mqtt.client as mqtt
import threading
import time
from collections import deque
import plotly.graph_objects as go

# Queue for sensor data
max_len = 100
ax_data, ay_data, az_data = deque(maxlen=max_len), deque(maxlen=max_len), deque(maxlen=max_len)
gx_data, gy_data, gz_data = deque(maxlen=max_len), deque(maxlen=max_len), deque(maxlen=max_len)

# MQTT callback
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        parts = dict(item.split(":") for item in payload.split(","))
        ax_data.append(float(parts["AX"]))
        ay_data.append(float(parts["AY"]))
        az_data.append(float(parts["AZ"]))
        gx_data.append(float(parts["GX"]))
        gy_data.append(float(parts["GY"]))
        gz_data.append(float(parts["GZ"]))
    except Exception as e:
        print("Parse error:", e)

# MQTT background thread
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.emqx.io", 1883, 60)
    client.subscribe("thammasat/aueaphum/sensor")
    client.loop_forever()

# Run MQTT once
if 'mqtt_started' not in st.session_state:
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state.mqtt_started = True

st.set_page_config(layout="wide")
st.title("📡 Real-Time IMU Plot (M5StickC via EMQX)")

# Create placeholders once
acc_placeholder = st.empty()
gyro_placeholder = st.empty()

# Loop to refresh chart
counter = 0
while True:
    counter += 1  # ใช้สร้าง key ไม่ซ้ำ

    # Accelerometer plot
    with acc_placeholder.container():
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(y=list(ax_data), name='AX'))
        fig1.add_trace(go.Scatter(y=list(ay_data), name='AY'))
        fig1.add_trace(go.Scatter(y=list(az_data), name='AZ'))
        fig1.update_layout(title="Accelerometer", yaxis=dict(range=[-2, 2]))
        st.plotly_chart(fig1, use_container_width=True, key=f"acc_{counter}")

    # Gyroscope plot
    with gyro_placeholder.container():
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(y=list(gx_data), name='GX'))
        fig2.add_trace(go.Scatter(y=list(gy_data), name='GY'))
        fig2.add_trace(go.Scatter(y=list(gz_data), name='GZ'))
        fig2.update_layout(title="Gyroscope", yaxis=dict(range=[-300, 300]))
        st.plotly_chart(fig2, use_container_width=True, key=f"gyro_{counter}")

    time.sleep(0.5)
