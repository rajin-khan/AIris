import streamlit as st
import requests
import cv2
import numpy as np
import time

st.set_page_config(page_title="ESP32 Cam Stream", layout="wide")

st.title("ESP32-CAM Wireless Controller")

# Sidebar for controls
st.sidebar.header("Connection Settings")
mode = st.sidebar.radio("Select Mode", ["Live Stream", "Setup Camera WiFi"])

# ================= SETUP MODE =================
if mode == "Setup Camera WiFi":
    st.header("Step 1: WiFi Provisioning")
    st.info("Instructions:\n1. Power on your ESP32-CAM.\n2. Connect your PC's WiFi to the network named **ESP32-CAM-SETUP**.\n3. Enter your Home WiFi credentials below.\n4. Click 'Send Configuration'.")
    
    wifi_ssid = st.text_input("Home WiFi SSID")
    wifi_pass = st.text_input("Home WiFi Password", type="password")
    
    if st.button("Send Configuration"):
        if not wifi_ssid:
            st.error("Please enter an SSID.")
        else:
            # The ESP32 in AP mode is always at 192.168.4.1
            setup_url = f"http://192.168.4.1/set-wifi?ssid={wifi_ssid}&pass={wifi_pass}"
            try:
                with st.spinner("Sending credentials to camera..."):
                    resp = requests.get(setup_url, timeout=5)
                    if resp.status_code == 200:
                        st.success("Credentials received! The camera is restarting. Please reconnect your PC to your Home WiFi now.")
                    else:
                        st.error(f"Error: {resp.text}")
            except Exception as e:
                st.error(f"Connection failed: {e}. Are you connected to ESP32-CAM-SETUP?")

# ================= STREAM MODE =================
elif mode == "Live Stream":
    st.header("Step 2: Live Monitor")
    
    # We allow the user to input the IP, or we can hardcode it if using a Static IP
    # Since DHCP assigns dynamic IPs, looking at the Serial Monitor is the best way to get this initially
    cam_ip = st.sidebar.text_input("Camera IP Address", "192.168.1.X")
    
    start_stream = st.sidebar.button("Start Streaming")
    stop_stream = st.sidebar.button("Stop Streaming")
    
    # Placeholder for the video image
    image_spot = st.empty()
    
    if start_stream:
        stream_url = f"http://{cam_ip}:80/stream"
        st.success(f"Connecting to {stream_url}...")
        
        # Open video stream using OpenCV
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            st.error("Cannot open stream. Check IP or Network connection.")
        else:
            stop_pressed = False
            while cap.isOpened() and not stop_pressed:
                ret, frame = cap.read()
                if ret:
                    # Convert color from BGR to RGB for Streamlit
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image_spot.image(frame, channels="RGB")
                else:
                    st.warning("Frame dropped or stream ended.")
                    break
                
                # Check if stop button was clicked in previous UI cycle 
                # (Streamlit logic makes real-time breaking tricky, usually requires rerun)
                # For this simple example, we rely on the user stopping the script or using the sidebar
                
            cap.release()

st.sidebar.markdown("---")
st.sidebar.info("Note: Ensure your PC and the Camera are on the same WiFi network for streaming.")