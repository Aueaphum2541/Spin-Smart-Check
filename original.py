import streamlit as st
from datetime import datetime
import pandas as pd
import io
from xhtml2pdf import pisa
import tempfile
import os
import base64
import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
import threading
import time
from collections import deque
import math
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


st.set_page_config(page_title="แบบสอบถามอาการเวียนศรีษะ", layout="wide")
st.title("แบบสอบถามอาการเวียนศรีษะ")
st.markdown("กรณีผู้ป่วยไม่สามารถทำแบบสอบถามเองได้ ให้ผู้ดูแลช่วยทำให้ได้")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
<style>
    html, body {
        font-family: 'Roboto', sans-serif;
        background: linear-gradient(120deg, #f0f9ff, #e0f7fa);
        color: #1e293b;
        scroll-behavior: smooth;
    }
    h1, h2, h3 {
        color: #0f172a;
    }
    .sidebar .sidebar-content {
        background-color: #e0f2f1;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.05);
    }
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f1f5f9);
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 15px 25px rgba(0,0,0,0.1);
        transition: all 0.3s ease-in-out;
        transform: perspective(1000px);
    }
    .feature-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 25px 35px rgba(0,0,0,0.15);
    }
    .video-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    .infographic {
        margin-top: 2rem;
        padding: 2rem;
        border-radius: 16px;
        background: #ffffffaa;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    .infographic h4 {
        color: #0284c7;
        margin-bottom: 1rem;
    }
    ul li::marker {
        color: #38bdf8;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #0f172a;
        text-align: center;
        margin-top: 1rem;
    }
    .hero-subtitle {
        font-size: 1.4rem;
        font-weight: 400;
        text-align: center;
        color: #334155;
        margin-bottom: 2rem;
    }
    .glass-card {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 16px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    padding: 1.5rem;
    color: #0f172a;
}
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11, tab12 = st.tabs(["1. Home and About Project",
    "2.ข้อมูลพื้นฐาน", "3.ลักษณะของอาการเวียนศรีษะ คุณรู้สึกเวียนศรีษะอย่างไรบ้าง? (เลือกทั้งหมดที่ตรงกับคุณ)", 
    "4.การเริ่มต้นและระยะเวลา", "5.สิ่งกระตุ้น",
    "6.อาการร่วม คุณมีอาการเหล่านี้ร่วมด้วยหรือไม่? (เลือกทั้งหมดที่ตรงกับคุณ)", "7.ประวัติทางการป่วย", 
    "8.สิ่งที่ทำให้อาการของคุณแย่ลง?", "9.ผลกระทบต่อชีวิตประจำวัน", "10.สรุปผลเบื้องต้น", "11.Eye Tracking","12.Motion Tracking"
])

with tab1:
    st.header("Welcome to Spin Smart Check")
    st.markdown("""
    <style>
    .guide-card {
    background: rgba(255,255,255,0.25);
    border-radius:18px;
    box-shadow:0 8px 32px rgba(31,38,135,.15);
    backdrop-filter:blur(12px);
    -webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,0.18);
    padding:2.5rem;
    margin-bottom:32px;
    color:#0f172a;
    font-size:1.4rem !important;
    line-height:1.8rem;
    }
    .guide-card h1 {
    font-size:2.8rem !important;
    margin-bottom:1.2rem;
    color:#0f172a;
    font-weight:800;
    }
    .guide-card ul {
    padding-left:2rem;
    margin:0;
    }
    .guide-card li {
    margin:10px 0;
    font-size:1.4rem;
    }
    .guide-card li::marker {
    color:#38bdf8;
    font-size:1.6rem;
    }
    .notice-red {
    font-size:1.6rem;
    color:#b91c1c;
    font-weight:900;
    margin-top:2.2rem;
    text-align:center;
    }
    </style>

    <div class="guide-card">
    <h1>📘 คู่มือการใช้งาน – หน้าแรก (Tab 1)</h1>
    <ul>
        <li>🧠 อ่านรายละเอียดของระบบ <strong>Spin Smart Check</strong> และวัตถุประสงค์</li>
        <li>🎥 ดูวิดีโอแนะนำระบบ การใช้งานจริงกับผู้ป่วย</li>
        <li>🖼️ ดู Infographics และภาพประกอบที่อธิบายโรค เช่น BPPV, Vestibular</li>
        <li>✨ อ่านคุณสมบัติเด่น เช่น ใช้ IMU Sensor + กล้อง + AI วิเคราะห์</li>
        <li>🗣️ อ่านคำแนะนำจากผู้ใช้งานจริง เพื่อสร้างความเข้าใจและความมั่นใจ</li>
    </ul>

    <p class="notice-red">🔻 หน้าถัดไปคือแบบกรอกข้อมูล กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ <strong>Tab 2: ข้อมูลพื้นฐาน</strong></p>
    </div>
    """, unsafe_allow_html=True)



    st.markdown("""
    <div class="glass-card">
        <h3>🏥 Why Spin Smart Check?</h3>
        <p>Spin Smart Check is an intelligent system designed to monitor head movements and eye gaze using IMU and camera data. It empowers healthcare and assistive applications through real-time analysis, visualization, and machine learning.</p>
    </div>
    """, unsafe_allow_html=True)
    image_path = r"C:\Users\Asus\OneDrive\Desktop\Spin-Smart-Check\S__4710416.jpg"
    image = Image.open(image_path)
    resized_image = image.resize((1000, 1000))  # ปรับขนาดตามที่ต้องการ
    # center the image in the Streamlit app
    st.markdown("<div style='text-align: center;'><h1 class='hero-title'>Spin Smart Check</h1></div>", unsafe_allow_html=True)
    # ✂️ ตัดขอบบนและล่าง (crop)
    # (left, upper, right, lower)
    width, height = resized_image.size
    cropped_image = resized_image.crop((0, 200, width, height - 120))  # ตัดบนและล่าง 20 px
   
    st.image(cropped_image)
    
    st.header("🔍 About Spin Smart Check")
    st.subheader("🧠 Head Motion & Eye Gaze Insights")
    st.video("https://youtu.be/KHFdeS8D6e4?feature=shared")
    st.image(r"C:\Users\Asus\OneDrive\Desktop\Spin-Smart-Check\Picture1.png", caption="Benign Paroxysmal Positional Vertigo", use_container_width=True)

    st.markdown("""
    <div class='feature-card'>
    <h3>&#10071; Pain Points</h3>
    <ul>
        <li>Patients or elderly individuals with dizziness or balance issues often cannot perceive their own head movements accurately.</li>
        <li>Healthcare professionals lack <strong>real-time tools</strong> to monitor head motion and correlate it with eye movement behavior.</li>
        <li>Traditional systems are unable to detect early signs of balance disorders or neurological abnormalities in a precise manner.</li>
    </ul>
    </div>

    <div class='feature-card'>
    <h3>🧠 Spin Smart Check – Our Solution</h3>
    <p>Spin Smart Check is an intelligent AI-powered platform that detects head movement using a 6-axis IMU sensor and analyzes eye movement patterns to assess balance abnormalities or dizziness symptoms. The system features real-time dashboards for effective screening and diagnosis.</p>
    </div>

    <div class='feature-card'>
    <h3>🎯 Research Goals</h3>
    <ul>
        <li>Screen and analyze individuals with <strong>chronic dizziness</strong> or balance impairments</li>
        <li>Support <strong>neurological rehabilitation</strong> through precise motion tracking</li>
        <li>Enable <strong>Smart Rehabilitation Systems</strong> with AI-assisted diagnostics</li>
    </ul>
    </div>

    <div class='feature-card'>
    <h3>🧠 Technologies Used</h3>
    <ul>
        <li><strong>IMU Sensors</strong> (M5StickC, MPU6886) for head motion tracking</li>
        <li><strong>Machine Learning</strong> (LSTM, Random Forest) to predict eye gaze direction</li>
        <li><strong>Real-time Data Streaming</strong> (MQTT, Threading) for live sensor feedback</li>
        <li><strong>Interactive UI</strong> (Streamlit, Plotly 3D) for visualizing head movement</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    
    st.markdown("""
    <style>
    .logo-section {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 30px;
        margin-top: 40px;
        margin-bottom: 30px;
    }
    .logo-section img {
        height: 50px;
        transition: filter 0.3s ease;
    }
    
    </style>

    <h3 style='text-align: center;'>🌍 Built with Data and Tools from the World’s Leading AI Labs</h3>
    <div class="logo-section">
        <img src="https://www.svgrepo.com/show/306500/openai.svg">
        <img src="https://huggingface.co/front/assets/huggingface_logo.svg">
        <img src="https://www.svgrepo.com/show/353805/google-cloud.svg">
        <img src="https://upload.wikimedia.org/wikipedia/commons/7/7c/Kaggle_logo.png">
        <img src="https://www.svgrepo.com/show/303630/nvidia-logo.svg">
        <img src="https://www.svgrepo.com/show/105198/massachusetts-institute-of-technology-logotype.svg">
        <img src="https://www.svgrepo.com/show/341921/ibm.svg">
        <img src="https://www.svgrepo.com/show/303247/microsoft-azure-2-logo.svg">
        <img src="https://www.svgrepo.com/show/431122/meta.svg">
        <img src="https://www.svgrepo.com/show/448266/aws.svg">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Harvard_University_logo.svg/900px-Harvard_University_logo.svg.png?20240103220517">
        <img src="https://images.seeklogo.com/logo-png/44/1/streamlit-logo-png_seeklogo-441815.png">
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .carousel-container {
        width: 100%;
        overflow: hidden;
        position: relative;
        margin: 50px auto;
        max-width: 900px;
    }
    .carousel {
        display: flex;
        animation: scroll 24s linear infinite;
    }
    .testimonial {
        min-width: 100%;
        box-sizing: border-box;
        padding: 2rem;
        background: #f1f5f9;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        text-align: center;
        font-size: 1.1rem;
        font-style: italic;
        color: #1e293b;
    }
    .testimonial strong {
        display: block;
        margin-top: 1rem;
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a;
    }
    @keyframes scroll {
        0%   { transform: translateX(0); }
        25%  { transform: translateX(-100%); }
        50%  { transform: translateX(-200%); }
        75%  { transform: translateX(-300%); }
        100% { transform: translateX(-400%); }
    }
    </style>
    
    <h3 style='text-align: center;'>💬 What Our Users Say</h3>
    <div class="carousel-container">
        <div class="carousel">
            <div class="testimonial">
                “Spin Smart Check transforms how we monitor patient balance and eye coordination.”
                <strong>Dr. Nicha Wong, Neurologist</strong>
            </div>
            <div class="testimonial">
                “IMU and real-time visualization give us precise head movement tracking for rehabilitation.”
                <strong>Arthit R., Rehab Specialist</strong>
            </div>
            <div class="testimonial">
                “The integration with MQTT and machine learning makes it perfect for smart health apps.”
                <strong>Patcharaporn T., IoT Engineer</strong>
            </div>
            <div class="testimonial">
                “Our elderly care center uses Spin Smart Check to assess dizziness and prevent falls.”
                <strong>Siriporn M., Geriatric Nurse</strong>
            </div>
            <div class="testimonial">
                “Reliable, interactive, and medically relevant — it’s a breakthrough for assistive technology.”
                <strong>Assoc. Prof. Dr. Kittipong S., Biomedical Engineer</strong>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

   
    st.markdown("---")
    
    # หลัง CTA
    st.markdown("## 📊 Real-Time Stats")
    col1, col2, col3 = st.columns(3)

    with col1:
        stat_placeholder = st.empty()
        for i in range(0, 93, 5):
            stat_placeholder.metric("🧠 Detection Accuracy", f"{i}%")
            time.sleep(0.03)

    with col2:
        sample_placeholder = st.empty()
        for i in range(0, 1525, 50):
            sample_placeholder.metric("📦 Samples Detected", f"{i}")
            time.sleep(0.01)

    with col3:
        alert_placeholder = st.empty()
        for i in range(0, 38, 2):
            alert_placeholder.metric("🚨 Alerts Triggered", f"{i}")
            time.sleep(0.05)


    st.markdown("""
    <style>
    .timeline-container {
        width: 100%;
        max-width: 1000px;
        margin: 60px auto 40px auto;
        padding: 0 10px;
    }
    .timeline {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        position: relative;
        counter-reset: step;
    }
    .timeline::before {
        content: '';
        position: absolute;
        top: 30px;
        left: 0;
        width: 100%;
        height: 4px;
        background-color: #e2e8f0;
        z-index: 0;
    }
    .step {
        position: relative;
        text-align: center;
        flex: 1;
        z-index: 1;
    }
    .step::before {
        counter-increment: step;
        content: counter(step);
        position: relative;
        display: inline-block;
        background: #38bdf8;
        color: white;
        width: 50px;
        height: 50px;
        line-height: 50px;
        border-radius: 50%;
        font-weight: bold;
        font-size: 1.2rem;
        z-index: 2;
    }
    .step-label {
        margin-top: 12px;
        font-size: 0.95rem;
        color: #0f172a;
        font-weight: 600;
    }
    </style>

    <div class="timeline-container">
    <h3 style="text-align:center;">🧭 How FungalShield AI Works</h3>
    <div class="timeline">
        <div class="step">
            <div class="step-label">📡 IMU Sensor Streaming</div>
        </div>
        <div class="step">
            <div class="step-label">🔁 Real-time Signal Smoothing</div>
        </div>
        <div class="step">
            <div class="step-label">🧠 ML-based Head Movement Analysis</div>
        </div>
        <div class="step">
            <div class="step-label">👁️ Gaze Direction Prediction</div>
        </div>
        <div class="step">
            <div class="step-label">📊 Visual Dashboard Feedback</div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🚀 Key Features")
    st.markdown("""
    <div class='feature-card'>
    <ul>
        <li>📡 Real-time IMU data streaming from wearable sensors</li>
        <li>🔁 Signal smoothing for stable and reliable measurements</li>
        <li>🧠 AI-powered head motion analysis with LSTM/ML models</li>
        <li>👁️ Predict accurate eye-gaze direction based on head movement</li>
        <li>📊 Interactive dashboard for live visualization and data logging</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(
    "<span style='color:#b91c1c; font-size:1.5rem; font-weight:bold;'>🔻 หน้าถัดไปคือแบบกรอกข้อมูล กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 2: ข้อมูลพื้นฐาน</span>",
    unsafe_allow_html=True
)
    
    
with tab2:
    st.header("2. ข้อมูลพื้นฐาน")
    # ---------- Instruction Card : Tab 2 ----------
    st.markdown("""
    <style>
    .guide-card {
    background: rgba(255,255,255,0.25);
    border-radius:18px;
    box-shadow:0 8px 32px rgba(31,38,135,.15);
    backdrop-filter:blur(12px);
    -webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,0.18);
    padding:2.5rem;
    margin-bottom:32px;
    color:#0f172a;
    font-size:1.4rem !important;
    line-height:1.9rem;
    }
    .guide-card h1{
    font-size:2.8rem !important;
    margin-bottom:1.2rem;
    color:#0f172a;
    font-weight:800;
    }
    .guide-card ul{
    padding-left:2rem;
    margin:0;
    }
    .guide-card li{
    margin:10px 0;
    font-size:1.4rem;
    }
    .guide-card li::marker{
    color:#38bdf8;
    font-size:1.6rem;
    }
    </style>

    <div class="guide-card">
    <h1>📘 คู่มือการใช้งาน – ข้อมูลพื้นฐาน (Tab 2)</h1>
    <ul>
        <li>เลือก <strong>เพศ</strong> ของคุณ (หญิง / ชาย)</li>
        <li>กรอก <strong>อายุ</strong> (0–120 ปี) และ <strong>อาชีพ</strong></li>
        <li>เลือก <strong>โรคประจำตัว</strong> ถ้ามี; ถ้า “อื่นๆ” ให้พิมพ์ระบุ</li>
        <li>ระบุ <strong>ยาที่ใช้อยู่</strong> และ <strong>สารเสพติดหรือสารพิษ</strong> ที่สัมผัส</li>
        <li>ตอบว่าเคยมีอาการเวียนศีรษะมาก่อนหรือไม่ &nbsp;—&nbsp; หาก “เคย” ต้องกรอก <em>สาเหตุ</em> และ <em>ช่วงเวลา</em></li>
        <li>ตอบประวัติครอบครัว; ถ้ามีให้ระบุโรคที่เกี่ยวข้อง</li>
        <li>เลือก <strong>ประวัติเจ็บป่วย</strong> (เช่น ยาใหม่ วัคซีน อุบัติเหตุศีรษะ ฯลฯ)</li>
        <li><strong>เพศหญิง</strong> จะมีคำถามเสริมเรื่องสถานะประจำเดือนและวันที่รอบล่าสุด</li>
        <li>ติ๊ก <strong>อาการฉุกเฉิน</strong> (สายตาพร่า ชัก ฯลฯ) หากพบ เพื่อให้ระบบเตือนพบแพทย์ด่วน</li>
        <li>ข้อมูลทุกช่องจะถูกบันทึกอัตโนมัติ &nbsp;—&nbsp; สามารถย้อนกลับมาแก้ไขได้ตลอด</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("เพศ", ["หญิง", "ชาย"])
        age = st.number_input("อายุ (ปี)", min_value=0, max_value=120)
        occupation = st.text_input("อาชีพ")
        
    with col2:
        diseases = st.multiselect("โรคประจำตัว", ["ไม่มี", "เบาหวาน", "ความดันสูง", "ความดันต่ำ", "โรคหัวใจ", "ไมเกรน", "โรคทางสมอง", "โรคอื่นๆ"])
        disease_others = st.text_input("ระบุโรคทางสมอง / อื่นๆ (ถ้ามี)")
        medications = st.text_input("ยาที่ท่านใช้ / ระบุว่าไม่ได้ทานยาอะไร")
        substances = st.text_input("สารเสพติดหรือสารพิษที่สัมผัส (ถ้ามี)")

    st.markdown("**อาการเวียนศีรษะในอดีต**")
    prev_dizzy = st.radio("เคยเวียนศีรษะมาก่อนหรือไม่?", ["เคย", "ไม่เคย"])
    if prev_dizzy == "เคย":
        dizzy_disease = st.text_input("จากโรคอะไร?", key="dizzy_disease")
        dizzy_time = st.text_input("เมื่อไหร่?", key="dizzy_time")
        
    family_history = st.radio("ประวัติครอบครัวมีอาการเวียนศีรษะหรือไม่?", ["มี", "ไม่มี"])
    # history = st.multiselect("ประวัติการเจ็บป่วย", 
    #                         ["ไม่มี", "ได้รับยาชนิดใหม่", "ได้รับวัคซีน", "เคยผ่าตัด", "เคยได้รับการฉายรังสี", "เคยมีอุบัติเหตุที่ศีรษะ", "อื่นๆ"])
    # triggers = st.multiselect("สิ่งกระตุ้นที่ทำให้เกิดอาการเวียนศีรษะ", 
    #                         ["ไม่มี", "อาหาร", "การเคลื่อนไหว", "ความเครียด", "แสงสว่าง", "เสียงดัง", "อื่นๆ"])
    # symptoms = st.multiselect("อาการร่วมที่เกิดขึ้นพร้อมกับอาการเวียนศีรษะ", 
    #                         ["ไม่มี", "ปวดหัว", "คลื่นไส้", "อาเจียน", "หูอื้อ", "หูแว่ว", "มองเห็นภาพซ้อน", "มองเห็นภาพพร่า", "สูญเสียการทรงตัว", "อื่นๆ"])
    
    # กรณีมีหลายช่องใช้ label เดียวกัน "จากโรคอะไร?" ต้องแยก key
    # if prev_dizzy == "เคย":
    #     dizzy_disease = st.text_input("จากโรคอะไร?", key="dizzy_disease")
        

    if family_history == "มี":
        family_disease = st.text_input("จากโรคอะไร?", key="family_disease")

    # if "ได้รับยาชนิดใหม่" in history:
    #     new_drug = st.text_input("ระบุชื่อยา", key="new_drug")

    # if "อาหาร" in triggers:
    #     food_trigger = st.text_input("ระบุอาหาร", key="food_trigger1")

    # if "อื่นๆ" in symptoms:
    #     other_symptom = st.text_input("โปรดระบุอาการอื่นๆ", key="other_symptom")
        
        # เพศหญิง
    if gender == "หญิง":
        st.markdown("**กรณีเพศหญิง**")
        period_status = st.radio("สถานะประจำเดือน", ["มีประจำเดือน", "ขาดประจำเดือน"], key="period_status")
        if period_status == "มีประจำเดือน":
            period_date = st.date_input("ประจำเดือนรอบสุดท้ายเมื่อ", key="last_period_date")

    # อาการที่ต้องรีบไปโรงพยาบาล
    st.markdown("**อาการที่ควรรีบไปพบแพทย์**")
    urgent_symptoms = st.multiselect("คุณมีอาการร่วมดังต่อไปนี้หรือไม่?", [
        "สายตาพร่ามัว 5.10", "มองเห็นภาพซ้อน 5.10", "พูดไม่ชัด พูดติดขัด 5.10",
        "เสียงแหบ 5.10", "กลืนลำบาก 5.10", "แขนขาอ่อนแรง 5.10", "ชาแขนขา 5.10",
        "เดินเซ ทรงตัวไม่ได้ 5.17", "ไม่รู้สึกตัว 5.18", "ชักเกร็ง 5.19",
        "ใจสั่น ใจหวิว 5.20", "เจ็บหน้าอก 5.20"
    ], key="urgent_symptoms")
    
    st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อกรอกข้อมูลในหน้านี้เสร็จแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 3: ลักษณะอาการเวียนศีรษะ</span>",
    unsafe_allow_html=True
)
    
    with tab3:
        st.header("3. ลักษณะของอาการเวียนศีรษะ")
        st.markdown("""
        <style>
        .guide-card {
        background: rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{
        font-size:2.8rem !important;
        margin-bottom:1.2rem;
        color:#0f172a;
        font-weight:800;
        }
        .guide-card ul{
        padding-left:2rem;
        margin:0;
        }
        .guide-card li{
        margin:10px 0;
        font-size:1.4rem;
        }
        .guide-card li::marker{
        color:#38bdf8;
        font-size:1.6rem;
        }
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – ลักษณะอาการ (Tab 3)</h1>
        <ul>
            <li>เลือกอาการเวียนศีรษะที่ตรงกับความรู้สึกของคุณมากที่สุด</li>
            <ul>
            <li>🌪 <strong>เวียนศีรษะหมุน</strong> – เหมือนโลกหมุนหรือตัวคุณหมุน</li>
            <li>🌊 <strong>โคลงเคลง / ลอย</strong> – เหมือนยืนบนเรือหรือพื้นไม่มั่นคง</li>
            <li>🚶‍♂️ <strong>เดินโซเซ / เสียการทรงตัว</strong></li>
            <li>😵 <strong>หน้ามืด</strong> – คล้ายจะเป็นลม</li>
            <li>🤔 <strong>มึนศีรษะ</strong> – ไม่หมุนแต่รู้สึกงงงวย</li>
            </ul>
            <li>หากรายการข้างต้นไม่ตรง โปรดเลือก “<em>อื่นๆ</em>” แล้วพิมพ์อาการของคุณ</li>
            <li>คุณสามารถเลือกได้มากกว่า 1 ข้อ หากมีอาการหลายรูปแบบสลับกัน</li>
            <li>ข้อมูลนี้เป็นกุญแจสำคัญในการแยกแยะชนิดของเวียนศีรษะ (เช่น BPPV, Migraine)</li>
            <li>เมื่อเลือกครบแล้ว สามารถเลื่อนไป Tab ถัดไปเพื่อระบุ “การเริ่มต้นและระยะเวลา”</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        dizzy_types = st.multiselect("คุณรู้สึกเวียนศีรษะอย่างไรบ้าง (เลือกทั้งหมดที่ตรงกับคุณ)", [
            "เวียนศีรษะหมุน (โลกหมุน หรือตัวคุณหมุน) 2.1",
            "เหมือนลอย โคลงเคลง โยกไปมา 2.1",
            "เดินโซเซ เสียการทรงตัว 2.3",
            "หน้ามืด หรือรู้สึกจะเป็นลม 2.4",
            "แค่มึนเฉยๆ 2.5",
            "อื่นๆ"
        ], key="dizzy_types")
        if "อื่นๆ" in dizzy_types:
            dizzy_other = st.text_input("กรุณาระบุอาการอื่นๆ", key="dizzy_other")
            
        st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อเลือกอาการเสร็จแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 4: การเริ่มต้น & ระยะเวลา</span>",
    unsafe_allow_html=True
)

    with tab4:
        st.header("4. การเริ่มต้นและระยะเวลา")
        # ---------- Instruction Card : Tab 4 ----------
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{
        font-size:2.8rem !important;
        margin-bottom:1.2rem;
        font-weight:800;
        color:#0f172a;
        }
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – การเริ่มต้น & ระยะเวลา (Tab 4)</h1>
        <ul>
            <li>ระบุว่าอาการเวียนศีรษะ <strong>เริ่มขึ้นเมื่อไหร่</strong><br>
                ▸ ใส่จำนวน <em>ชั่วโมง / วัน / สัปดาห์ / เดือน</em> ที่ผ่านมา<br>
                ▸ หากไม่แน่ใจ ให้กรอกช่องที่ใกล้เคียงที่สุด (ใส่ 0 ในช่องที่ไม่ใช้)<br>
                ▸เลือก <strong>ลักษณะการเริ่มต้น</strong><br>
                ▸ <em>เป็นขึ้นมาทันทีทันใด</em> (เฉียบพลัน)<br>
                ▸ <em>ค่อย ๆ เวียนมากขึ้น</em> (ค่อยเป็นค่อยไป)<br>
                ▸ระบุ <strong>ระยะเวลาของอาการแต่ละครั้ง</strong><br>
                ▸ เลือกช่วงเวลา (วินาที / นาที / ชั่วโมง / วัน / เวียนตลอดเวลา)<br>
                ▸ หากเลือก “___ วินาที” หรือ “___ ชั่วโมง” ให้กรอกตัวเลขในช่องว่าง<br>
                ▸เลือก <strong>ความถี่ของการเกิดอาการ</strong><br>
                ▸ ทุกวัน → พิมพ์จำนวนครั้ง/วัน<br>
                ▸ หรือเลือก 1-3 ครั้ง/สัปดาห์, 4-6 ครั้ง/สัปดาห์, นาน ๆ ที<br>
                ▸<em>เคล็ดลับ:</em> การกรอกข้อมูลเวลา-ความถี่ครบถ้วนช่วยแพทย์แยกโรคเฉียบพลัน (เช่น Stroke) ออกจากโรคเวียนศีรษะชนิดอื่น 💡<br>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("อาการเวียนศีรษะครั้งนี้ เริ่มเมื่อไหร่?")
        col1, col2 = st.columns(2)
        with col1:
            hours_ago = st.number_input("___ ชั่วโมงก่อน 3.1", min_value=0, key="3_1_hours")
            days_ago = st.number_input("___ วันก่อน 3.2", min_value=0, key="3_2_days")
        with col2:
            weeks_ago = st.number_input("___ สัปดาห์ก่อน 3.3", min_value=0, key="3_3_weeks")
            months_ago = st.number_input("___ เดือนก่อน 3.4", min_value=0, key="3_4_months")

        st.subheader("อาการเวียนศีรษะเริ่มต้นแบบใด?")
        onset_type = st.radio("เลือก", [
            "เป็นขึ้นมาทันทีทันใด 3.5", 
            "ค่อยๆ เวียนทีละน้อย เวียนมากขึ้นเรื่อยๆ 3.6"
        ], key="onset_type")

        # st.subheader("อาการเวียนศีรษะแต่ละครั้งกินเวลานานเท่าไหร่?")
        # duration_type = st.selectbox("เลือกช่วงเวลา", [
        #     "___ วินาที (สูงสุด 180 วินาที) 3.7",
        #     "___ นาที (5 – 30) 3.8",
        #     "มากกว่า 30 นาที 3.9",
        #     "___ ชั่วโมง 3.9",
        #     "___ วัน 3.10",
        #     "มากกว่า 2 วัน เวียนตลอดเวลา ไม่มีช่วงหาย 3.11"
        # ], key="duration_type")
        
        st.subheader("อาการเวียนศีรษะแต่ละครั้งกินเวลานานเท่าไหร่?")

        # 1) ให้ผู้ใช้เลือกชนิดช่วงเวลา
        duration_kind = st.radio(
            "เลือกช่วงเวลา",
            (
                "วินาที (≤ 180)",        # 3.7
                "นาที (5 – 30)",        # 3.8
                "มากกว่า 30 นาที",      # 3.9
                "ชั่วโมง",              # 3.9 (ใช้รหัสเดียวกันกับ >30 นาที)
                "วัน",                   # 3.10
                "มากกว่า 2 วัน / เวียนตลอดเวลา"  # 3.11
            ),
            key="duration_kind"
        )

        # 2) ถ้าต้องใส่ตัวเลข ให้แสดง number_input
        duration_value = None
        if duration_kind.startswith("วินาที"):
            duration_value = st.number_input(
                "จำนวนวินาที", min_value=1, max_value=180, step=1, key="duration_sec"
            )
            duration_code = "3.7"

        elif duration_kind.startswith("นาที"):
            duration_value = st.number_input(
                "จำนวน ‘นาที’ (5–30)", min_value=5, max_value=30, step=1, key="duration_min"
            )
            duration_code = "3.8"

        elif duration_kind.startswith("ชั่วโมง"):
            duration_value = st.number_input(
                "จำนวนชั่วโมง (≥ 1)", min_value=1, max_value=24, step=1, key="duration_hr"
            )
            duration_code = "3.9"

        elif duration_kind.startswith("วัน"):
            duration_value = st.number_input(
                "จำนวนวัน (1–2)", min_value=1, max_value=2, step=1, key="duration_day"
            )
            duration_code = "3.10"

        elif duration_kind.startswith("มากกว่า 30 นาที"):
            duration_code = "3.9"   # ไม่ต้องกรอกตัวเลข

        else:  # มากกว่า 2 วัน / เวียนตลอดเวลา
            duration_code = "3.11"  # ไม่ต้องกรอกตัวเลข

        # 3) สรุปผลเป็นข้อความเดียว (ใช้เก็บหรือแสดงต่อ)
        if duration_value is not None:
            st.info(f"คุณเลือก: {duration_kind} — {duration_value} หน่วย  (รหัส {duration_code})")
        else:
            st.info(f"คุณเลือก: {duration_kind}  (รหัส {duration_code})")

        # === เก็บค่าไว้ใช้ภายหลัง ===
        st.session_state["duration_code"] = duration_code
        st.session_state["duration_value"] = duration_value

        # สร้างข้อความสรุปแบบเดิมให้โค้ดตอนท้ายใช้ได้
        duration_type = f"{duration_kind} {duration_value if duration_value is not None else ''}".strip()


        st.subheader("ความถี่ของอาการเวียนศีรษะ")
        freq_choice = st.radio(
            "คุณมีอาการบ่อยแค่ไหน?",
            (
                "ทุกวัน",               # daily
                "สัปดาห์ละ 1-3 ครั้ง",   # weekly (low)
                "สัปดาห์ละ 4-6 ครั้ง",   # weekly (high)
                "นานๆ ที"               # seldom
            ),
            key="freq_choice"
        )

        # ช่องให้กรอกตัวเลขตามตัวเลือก
        freq_value = None
        if freq_choice == "ทุกวัน":
            freq_value = st.number_input(
                "จำนวนครั้งต่อวัน", min_value=1, max_value=30, step=1,
                key="freq_per_day"
            )
            dizzy_frequency_text = f"ทุกวัน {freq_value} ครั้ง/วัน"

        elif freq_choice.startswith("สัปดาห์ละ 1-3"):
            freq_value = st.number_input(
                "จำนวนครั้งต่อสัปดาห์ (1-3)", min_value=1, max_value=3, step=1,
                key="freq_week_1_3"
            )
            dizzy_frequency_text = f"สัปดาห์ละ {freq_value} ครั้ง"

        elif freq_choice.startswith("สัปดาห์ละ 4-6"):
            freq_value = st.number_input(
                "จำนวนครั้งต่อสัปดาห์ (4-6)", min_value=4, max_value=6, step=1,
                key="freq_week_4_6"
            )
            dizzy_frequency_text = f"สัปดาห์ละ {freq_value} ครั้ง"

        else:            # นานๆ ที
            dizzy_frequency_text = "นานๆ ที"

        st.info(f"สรุปความถี่: {dizzy_frequency_text}")

        # เก็บไว้ใช้ตอนสร้าง report
        st.session_state["dizzy_frequency_text"] = dizzy_frequency_text
        st.session_state["dizzy_freq_value"] = freq_value
        
        
        
# --------------------------------------------------------------
#         dizzy_frequency = st.radio("คุณมีอาการบ่อยแค่ไหน?", [
#             "ทุกวัน วันละ ___ ครั้ง",
#             "1-3 ครั้ง/สัปดาห์",
#             "4-6 ครั้ง/สัปดาห์",
#             "นานๆ ที"
#         ], key="dizzy_frequency")
        
#         st.markdown(
#     "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อกรอกช่วงเวลาและความถี่ครบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 5 : สิ่งกระตุ้น</span>",
#     unsafe_allow_html=True
# )

        
    with tab5:
        st.header("5. สิ่งกระตุ้น")
        # ---------- Instruction Card : Tab 5 ----------
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{
        font-size:2.8rem !important;
        margin-bottom:1.2rem;
        font-weight:800;
        color:#0f172a;
        }
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – สิ่งกระตุ้น (Tab 5)</h1>
        <ul>
            <li>ติ๊กเครื่องหมายถูกใน <strong>ทุกข้อ</strong> ที่ทำให้เกิดหรือกระตุ้นอาการเวียนศีรษะของคุณ</li>
            <li>เลือกรายการได้มากกว่าหนึ่งข้อ เช่น<br>
                ▸ 🛌 พลิกตัวบนเตียง ▸ 🪜 ลุกขึ้นยืนเร็ว ▸ 🔊 เสียงดัง ▸ 💡 แสงวูบวาบ</li>
            <li>หากเลือก “เสียงดัง” หรือ “สิ่งเร้าทางสายตา” โปรแกรมจะบันทึกรหัสอาการให้อัตโนมัติ</li>
            <li>ถ้าเลือก “ขณะนอนแล้วพลิกตะแคงตัว” ระบบจะถาม “พลิกไปด้านใด” (ซ้าย/ขวา)</li>
            <li>ถ้าเลือก “อาหาร” จะมีช่อง <em>ระบุอาหาร</em> ปรากฏ ให้พิมพ์ชื่ออาหารหรือเครื่องดื่มที่สงสัย</li>
            <li>กรณี “ไม่มีสิ่งกระตุ้น” ให้ติ๊ก “ไม่มีสิ่งกระตุ้นที่ชัดเจน” เพื่อระบุว่าอาการเกิดขึ้นเอง</li>
            <li>ยิ่งระบุสิ่งกระตุ้นครบถ้วน ระบบจะยิ่งช่วยแยกโรคชนิด vestibular ได้ถูกต้องขึ้น</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("สิ่งที่ทำให้คุณเริ่มมีอาการเวียนศีรษะ? (เลือกทั้งหมดที่ตรงกับคุณ)")

        trigger_1 = st.checkbox("ตื่นนอนขณะยังไม่ได้ขยับตัว ก็มีอาการเวียนศีรษะเลย 4.1", key="trigger_1")
        trigger_2 = st.checkbox("ขณะนอนแล้วพลิกตะแคงตัว 4.2", key="trigger_2")
        if trigger_2:
            side = st.radio("พลิกไปด้านใด", ["ซ้าย", "ขวา"], key="turning_side")
        trigger_3 = st.checkbox("ล้มตัวลงนอน 4.2", key="trigger_3")
        trigger_4 = st.checkbox("ขณะลุกขึ้น (นั่ง หรือยืน) 4.3", key="trigger_4")
        trigger_5 = st.checkbox("การขยับศีรษะ 4.4", key="trigger_5")
        trigger_6 = st.checkbox("เป็นเอง ไม่สัมพันธ์กับการเปลี่ยนท่าทาง 4.5", key="trigger_6")
        trigger_7 = st.checkbox("เสียงดัง 4.6", key="trigger_7")
        trigger_8 = st.checkbox("สิ่งเร้าทางสายตา (เช่น หน้าจอ, แสงสี) 4.7", key="trigger_8")
        trigger_9 = st.checkbox("อาหาร 4.8", key="trigger_9")
        if trigger_9:
            food_trigger = st.text_input("ระบุอาหาร", key="food_trigger9")
        trigger_10 = st.checkbox("ความเครียด หรือเหนื่อยล้า 4.9", key="trigger_10")
        trigger_11 = st.checkbox("การเปลี่ยนแรงดันอากาศในหู เช่น ดำน้ำลึก ขึ้นที่สูง ลงที่ต่ำ 4.10", key="trigger_11")
        trigger_12 = st.checkbox("ไม่มีสิ่งกระตุ้นที่ชัดเจน", key="trigger_12")
        
        st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อเลือกสิ่งกระตุ้นครบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 6 : อาการร่วม</span>",
    unsafe_allow_html=True
)


    with tab6:
        st.header("6. อาการร่วม")
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{
        font-size:2.8rem !important;
        margin-bottom:1.2rem;
        font-weight:800;
        color:#0f172a;
        }
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – อาการร่วม (Tab 6)</h1>
        <ul>
            <li>ติ๊กเครื่องหมายถูกใน <strong>ทุกอาการ</strong> ที่เกิดขึ้นพร้อมกับเวียนศีรษะ เช่น<br>
                ▸ 🤢 <em>คลื่นไส้ / อาเจียน</em> ▸ 👂 <em>หูอื้อ / การได้ยินลดลง</em><br>
                ▸ 🤕 <em>ปวดหัว / ไมเกรน</em> ▸ 🤒 <em>มีไข้</em> ▸ 🦵 <em>แขนขาอ่อนแรง / ชา</em></li>
                ▸อาการที่มีเลข 5.10 (เช่น สายตาพร่า พูดไม่ชัด เดินเซ) เป็น <strong>สัญญาณอันตราย</strong><br>
                ▸ หากคุณมีมากกว่า 1 ข้อ แนะนำพบแพทย์ทันทีหลังทำแบบสอบถาม<br>
                ▸เลือกได้มากกว่าหนึ่งข้อ — ยิ่งให้รายละเอียดครบ ระบบจะจับคู่รหัสอาการได้แม่นยำมากขึ้น<br>
                ▸ถ้าไม่มีอาการอื่น ให้ติ๊ก “<em>การได้ยินปกติ ไม่มีอาการทางหู</em>” หรือ “<em>ไม่มี</em>” ตามจริง<br>
                ▸หากพบอาการพิเศษไม่อยู่ในรายการ ให้เลือก “อื่นๆ” แล้วพิมพ์อาการเพิ่มเติม<br>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("คุณมีอาการเหล่านี้ร่วมด้วยหรือไม่? (เลือกทั้งหมดที่ตรงกับคุณ)")

        symptom_1 = st.checkbox("คลื่นไส้ หรืออาเจียน", key="symptom_1")
        symptom_2 = st.checkbox("การได้ยินปกติ ไม่มีอาการทางหู 5.1", key="symptom_2")
        symptom_3 = st.checkbox("การได้ยินลดลง สูญเสียการได้ยิน 5.2", key="symptom_3")
        symptom_4 = st.checkbox("หูอื้อ มีเสียงในหู 5.3", key="symptom_4")
        symptom_5 = st.checkbox("รู้สึกแน่นในหู 5.4", key="symptom_5")
        symptom_6 = st.checkbox("มีไข้ 5.5", key="symptom_6")
        symptom_7 = st.checkbox("มีน้ำไหลจากหู 5.6", key="symptom_7")
        symptom_8 = st.checkbox("ปวดคอ หรือบ่าไหล่ 5.7", key="symptom_8")
        symptom_9 = st.checkbox("ปวดศีรษะ 5.8", key="symptom_9")
        symptom_10 = st.checkbox("ปวดไมเกรน 5.9", key="symptom_10")
        symptom_11 = st.checkbox("สายตาพร่ามัว 5.10", key="symptom_11")
        symptom_12 = st.checkbox("มองเห็นภาพซ้อน 5.10", key="symptom_12")
        symptom_13 = st.checkbox("พูดไม่ชัด พูดติดขัด 5.10", key="symptom_13")
        symptom_14 = st.checkbox("เสียงแหบ 5.10", key="symptom_14")
        symptom_15 = st.checkbox("กลืนลำบาก 5.10", key="symptom_15")
        symptom_16 = st.checkbox("ชาแขนขา 5.10", key="symptom_16")
        symptom_17 = st.checkbox("แขนขาอ่อนแรง 5.10", key="symptom_17")
        symptom_18 = st.checkbox("เดินเซ ทรงตัวไม่ได้ 5.17", key="symptom_18")
        symptom_19 = st.checkbox("ไม่รู้สึกตัว 5.18", key="symptom_19")
        symptom_20 = st.checkbox("ชักเกร็ง 5.19", key="symptom_20")
        symptom_21 = st.checkbox("ใจสั่น ใจหวิว 5.20", key="symptom_21")
        symptom_22 = st.checkbox("เจ็บหน้าอก 5.20", key="symptom_22")
        symptom_23 = st.checkbox("ชาปลายมือ หรือปลายเท้า 5.21", key="symptom_23")
        symptom_24 = st.checkbox("หน้าเบี้ยวหรือใบหน้าชา", key="symptom_24")
        
        st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อเลือกอาการร่วมครบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 7 : ประวัติทางการเจ็บป่วย</span>",
    unsafe_allow_html=True
)

    with tab7:
        st.header("7. ประวัติทางการเจ็บป่วย")
        # ---------- Instruction Card : Tab 7 ----------
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{
        font-size:2.8rem !important;
        margin-bottom:1.2rem;
        font-weight:800;
        color:#0f172a;
        }
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – ประวัติทางการเจ็บป่วย (Tab 7)</h1>
        <ul>
            <li>เลือกเหตุการณ์ที่เกิด <strong>ภายใน 1–3 เดือน</strong> ก่อนเริ่มเวียนศีรษะ เช่น</li>
            <ul>
            <li>🦻 <strong>การติดเชื้อในหู</strong> หรือมีน้ำจากหู (6.1)</li>
            <li>🧠 <strong>การบาดเจ็บที่ศีรษะ</strong> / อุบัติเหตุรถยนต์ ล้ม กระแทก (6.2)</li>
            <li>🤒 <strong>เป็นไข้หวัด</strong> หรือทางเดินหายใจอักเสบ (6.3)</li>
            <li>💧 <strong>ท้องเสีย เสียน้ำ หรืออาเจียนรุนแรง</strong> (6.4)</li>
            <li>💊 <strong>ได้รับยาชนิดใหม่</strong> (เช่น ยาปฏิชีวนะ ยากันชัก ฯลฯ) (6.5)<br>
                ▸ กรอกชื่อยาเมื่อเลือกข้อนี้ เพื่อให้ระบบตรวจ “ยาที่อาจทำลายหู”</li>
            </ul>

            
        </ul>
        </div>
        """, unsafe_allow_html=True)
        illness_1 = st.checkbox("การติดเชื้อในหูเมื่อเร็วๆ นี้ 6.1", key="illness_1")
        illness_2 = st.checkbox("การบาดเจ็บที่ศีรษะ 6.2", key="illness_2")
        illness_3 = st.checkbox("เป็นไข้และอาการหวัดเมื่อเร็วๆ นี้ 6.3", key="illness_3")
        illness_4 = st.checkbox("ท้องเสีย เสียน้ำ เสียเหงื่อมาก อาเจียนมาก เมื่อเร็วๆ นี้ 6.4", key="illness_4")
        illness_5 = st.checkbox("ได้รับยาชนิดใหม่เมื่อเร็วๆ นี้ 6.5", key="illness_5")
        if illness_5:
            new_drug = st.text_input("ชื่อยา", key="new_drug")
            
        st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อระบุประวัติทางการเจ็บป่วยครบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 8 : สิ่งที่ทำให้อาการแย่ลง</span>",
    unsafe_allow_html=True
)

    with tab8:
        st.header("8. สิ่งที่ทำให้อาการของคุณแย่ลง")
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{font-size:2.8rem !important;margin-bottom:1.2rem;font-weight:800;}
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – สิ่งที่ทำให้อาการแย่ลง (Tab 8)</h1>

        <ul>
            <li>
            เลือก <strong>ท่าทางหรือสถานการณ์</strong> ที่ทำให้อาการเวียนศีรษะแย่ลง
            <ul>
                <li>↕️ เปลี่ยนท่าทาง เช่น จากนอนเป็นนั่ง หรือยืนเร็ว</li>
                <li>🧍 เดินหรือยืนเฉย ๆ นาน ๆ</li>
                <li>📱 ใช้สายตาจ้องนาน เช่น ดูจอมือถือหรือคอมพิวเตอร์</li>
                <li>🔊 อยู่ในที่เสียงดัง หรือคนพลุกพล่าน</li>
                <li>🔄 หันหัวหรือเปลี่ยนมุมมองเร็ว ๆ</li>
            </ul>
            </li>

        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        worsen_1 = st.checkbox("ล้มตัวลงนอน 7.1", key="worsen_1")
        worsen_2 = st.checkbox("พลิกตัวบนเตียง 7.2", key="worsen_2")
        worsen_3 = st.checkbox("ลุกขึ้นเร็วเกินไป 7.3", key="worsen_3")
        worsen_4 = st.checkbox("เงยหน้า หรือก้มหน้า 7.4", key="worsen_4")
        worsen_5 = st.checkbox("หันศีรษะไปมาซ้ายขวา 7.5", key="worsen_5")
        worsen_6 = st.checkbox("ความเครียด เหนื่อยล้า พักผ่อนไม่เพียงพอ 7.6", key="worsen_6")
        
        st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อเลือกสาเหตุที่ทำให้อาการแย่ลงครบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 9 : ผลกระทบต่อชีวิตประจำวัน</span>",
    unsafe_allow_html=True
)

    with tab9:
        st.header("9. ผลกระทบต่อชีวิตประจำวัน")
        # ---------- Instruction Card : Tab 9 ----------
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;
        margin-bottom:32px;
        color:#0f172a;
        font-size:1.4rem !important;
        line-height:1.9rem;
        }
        .guide-card h1{
        font-size:2.8rem !important;
        margin-bottom:1.2rem;
        font-weight:800;
        color:#0f172a;
        }
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – ผลกระทบต่อชีวิตประจำวัน (Tab 9)</h1>
        <ul>
            <li>เลือก <strong>ระดับผลกระทบที่คุณได้รับจากอาการเวียนศีรษะ</strong> ต่อการใช้ชีวิตประจำวัน</li>
            <li>ระบบจะให้คุณเลือก 1 จาก 4 ระดับ:</li>
            <ul>
            <li>🟢 <strong>ไม่กระทบ</strong> – ใช้ชีวิตได้ตามปกติ</li>
            <li>🟡 <strong>กระทบบ้าง</strong> – ยังทำงานได้แต่ต้องปรับตัว</li>
            <li>🟠 <strong>กระทบมาก</strong> – ต้องหยุดพัก/ลางานบ่อย</li>
            <li>🔴 <strong>กระทบต่อคุณภาพชีวิตมาก</strong> – ไม่สามารถใช้ชีวิตได้ตามปกติ</li>
            </ul>
            <li>ข้อมูลนี้จะช่วยให้ระบบประเมิน <strong>ความเร่งด่วนในการพบแพทย์</strong> และแนะนำแนวทางเบื้องต้น</li>
            <li>กรุณาเลือกตามความเป็นจริง เพื่อผลการประเมินที่แม่นยำ</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        impact_level = st.radio("อาการเวียนศีรษะส่งผลต่อการใช้ชีวิตของคุณแค่ไหน?", [
            "ไม่กระทบ 8.1",
            "มีผลบ้างเล็กน้อย 8.2",
            "มีผลปานกลาง (กระทบงาน/การเรียน) 8.3",
            "มีผลรุนแรง (จำกัดการใช้ชีวิตประจำวัน) 8.4"
        ], key="life_impact")
        
        st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อประเมินผลกระทบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 10 : สรุปผลเบื้องต้น</span>",
    unsafe_allow_html=True
)
        
    # === รวบรวมข้อมูลจาก Tab 1-8 ===
    selected_codes = set()   
    # === รวบรวม selected_codes จากข้อมูลใน Tab 2-8 ===
if 'dizzy_types' in locals():
    if "เวียนศีรษะหมุน (โลกหมุน หรือตัวคุณหมุน) 2.1" in dizzy_types:
        selected_codes.add("2.1")
    if "เหมือนลอย โคลงเคลง โยกไปมา 2.1" in dizzy_types:
        selected_codes.add("2.1")
    if "หน้ามืด หรือรู้สึกจะเป็นลม 2.4" in dizzy_types:
        selected_codes.add("2.4")
    if "แค่มึนเฉยๆ 2.5" in dizzy_types:
        selected_codes.add("2.5")

if 'onset_type' in locals():
    if onset_type == "เป็นขึ้นมาทันทีทันใด 3.5":
        selected_codes.add("3.5")
    elif onset_type == "ค่อยๆ เวียนทีละน้อย เวียนมากขึ้นเรื่อยๆ 3.6":
        selected_codes.add("3.6")

if 'duration_type' in locals():
    for code in ["3.7", "3.8", "3.9", "3.10", "3.11", "3.4"]:
        if code in duration_type:
            selected_codes.add(code)

for i in range(1, 13):
    if f"trigger_{i}" in locals() and eval(f"trigger_{i}"):
        selected_codes.add(f"4.{i}")

symptom_map = {
    2: "5.1", 3: "5.2", 4: "5.3", 5: "5.4", 6: "5.5", 7: "5.6", 8: "5.7", 9: "5.8",
    10: "5.9", 11: "5.10", 12: "5.10", 13: "5.10", 14: "5.10", 15: "5.10",
    16: "5.10", 17: "5.10", 18: "5.17", 19: "5.18", 20: "5.19", 21: "5.20",
    22: "5.20", 23: "5.21"
}
for i, code in symptom_map.items():
    if f"symptom_{i}" in locals() and eval(f"symptom_{i}"):
        selected_codes.add(code)

for i in range(1, 6):
    if f"illness_{i}" in locals() and eval(f"illness_{i}"):
        selected_codes.add(f"6.{i}")

for i in range(1, 7):
    if f"worsen_{i}" in locals() and eval(f"worsen_{i}"):
        selected_codes.add(f"7.{i}")

# === TAB 10: วิเคราะห์ผล ====
with tab10:
    st.header("10. วิเคราะห์กลุ่มโรคเบื้องต้น")
    st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 หลังตรวจสอบสรุปโรคเบื้องต้นแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 11 : Eye Tracking</span>",
    unsafe_allow_html=True
)
    
    # ---------- Instruction Card : Tab 10 ----------
    st.markdown("""
    <style>
    .guide-card{
    background:rgba(255,255,255,0.25);
    border-radius:18px;
    box-shadow:0 8px 32px rgba(31,38,135,.15);
    backdrop-filter:blur(12px);
    -webkit-backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,0.18);
    padding:2.5rem;margin-bottom:32px;
    color:#0f172a;font-size:1.4rem !important;line-height:1.9rem;
    }
    .guide-card h1{font-size:2.8rem !important;margin-bottom:1.2rem;font-weight:800;}
    .guide-card ul{padding-left:2rem;margin:0;}
    .guide-card li{margin:10px 0;font-size:1.4rem;}
    .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
    </style>

    <div class="guide-card">
    <h1>📘 คู่มือการใช้งาน – สรุปผลเบื้องต้น (Tab 10)</h1>
    <ul>
        <li>ระบบคำนวณ <strong>คะแนนความใกล้เคียง</strong> ระหว่างรหัสอาการที่คุณเลือกกับกลุ่มโรคกว่า 20 กลุ่ม</li>
        <li>โรคที่เข้าเค้าจะถูกเรียงจากคะแนนสูง ➜ ต่ำ พร้อมเปอร์เซ็นต์</li>
        <li>ตารางด้านล่างแสดง <strong>กลุ่มโรค + คำอธิบายรหัสอาการ</strong> (แปลงตัวเลขเป็นภาษาไทยเพื่ออ่านง่าย)</li>
        <li>กดปุ่ม <em>ดาวน์โหลด CSV</em> หรือ <em>ดาวน์โหลด PDF</em> เพื่อเก็บรายงานส่งให้แพทย์</li>
        <li>🔍 หากมีอาการรุนแรง (เช่น 5.10 อาการทางระบบประสาทหลายข้อ) ควรพบแพทย์ทันที</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    # ---------- Mapping : รหัส → คำอธิบาย ----------
    code_desc = {
        "2.1":"เวียนศีรษะหมุน / โคลงเคลง", "2.4":"หน้ามืด", "2.5":"มึนศีรษะ",
        "3.4":"อาการเรื้อรังหลายเดือน", "3.5":"เป็นขึ้นมาทันที", "3.6":"ค่อย ๆ เป็นมากขึ้น",
        "3.7":"อาการสั้นเป็นวินาที", "3.8":"อาการนานเป็นนาที", "3.9":"อาการ > 30 นาที",
        "3.10":"อาการนานเป็นวัน", "3.11":"อาการนาน > 2 วัน / ต่อเนื่อง",
        "4.1":"ตื่นนอนแล้วยังไม่ขยับ", "4.2":"พลิกตะแคง", "4.3":"ลุกขึ้นยืน/นั่งเร็ว",
        "4.4":"ขยับศีรษะ", "4.5":"อาการเกิดเอง", "4.6":"เสียงดัง",
        "4.7":"สิ่งเร้าทางสายตา", "4.8":"อาหาร", "4.9":"ความเครียด", "4.10":"เปลี่ยนแรงดันอากาศ",
        "5.1":"คลื่นไส้/อาเจียน", "5.2":"การได้ยินลดลง", "5.3":"หูอื้อ", "5.4":"แน่นหู",
        "5.5":"มีไข้", "5.6":"น้ำไหลจากหู", "5.7":"ปวดคอ/บ่า", "5.8":"ปวดศีรษะ",
        "5.9":"ไมเกรน", "5.10":"อาการทางระบบประสาท", "5.17":"เดินเซ", "5.18":"ไม่รู้สึกตัว",
        "5.19":"ชักเกร็ง", "5.20":"ใจสั่น/เจ็บหน้าอก", "5.21":"ชาปลายมือ/เท้า",
        "6.1":"ติดเชื้อในหู", "6.2":"บาดเจ็บศีรษะ", "6.3":"ไข้หวัด/ติดเชื้อไวรัส",
        "6.4":"ท้องเสีย/ขาดน้ำ", "6.5":"ได้รับยาชนิดใหม่",
        "7.1":"ล้มตัวลงนอน", "7.2":"พลิกตัวบนเตียง", "7.3":"ลุกขึ้นเร็ว",
        "7.4":"เงยหน้า/ก้มหน้า", "7.5":"หันศีรษะซ้ายขวา", "7.6":"เครียด/พักผ่อนน้อย"
    }

    

    st.markdown("<h2 style='color:red;'>🚨 Critical Alert: ต้องพบแพทย์ด่วน</h2>", unsafe_allow_html=True)

    disease_mapping = {
        "BPPV": {"2.1", "3.5", "3.7", "4.2", "5.1", "6.2", "7.1", "7.2"},
        "Meniere’s disease": {"2.1", "3.5", "3.9", "4.5", "5.2", "5.3", "5.4"},
        "Labyrinthitis": {"2.1", "3.5", "3.10", "4.5", "5.2", "5.3", "5.5", "5.6", "6.1", "6.3"},
        "Perilymph fistular": {"2.1", "3.5", "3.11", "4.5", "4.10", "5.2", "5.3", "6.2"},
        "Vestibular neuritis": {"2.1", "3.5", "3.10", "4.5", "5.1", "6.3"},
        "Vestibulopathy": {"2.1", "3.5", "3.11", "4.5", "5.1"},
        "Acoustic neuroma": {"2.1", "3.6", "3.11", "4.5", "5.1", "5.10", "5.17"},
        "Ototoxic drug expose": {"2.1", "3.5", "3.11", "4.5", "5.2", "5.3", "6.5"},
        "TIA": {"3.5", "3.8", "5.1", "5.8", "5.10", "5.17", "5.18"},
        "VBI": {"2.1", "3.5", "3.7", "4.4", "5.1", "5.8", "5.10", "5.17", "5.18"},
        "PICA syndrome": {"3.5", "3.11", "5.2", "5.8", "5.10", "5.17"},
        "Cerebellar infarction": {"3.5", "3.11", "4.1", "5.8", "5.10", "5.17"},
        "Multiple sclerosis": {"3.4", "3.6", "3.11", "5.8", "5.10"},
        "Cerebellar abscess": {"3.11", "5.5", "5.8", "5.10", "5.17"},
        "Trauma": {"3.11", "5.10", "5.17", "6.2"},
        "Migrainous vertigo": {"3.9", "4.6", "4.7", "4.8", "5.1", "5.8", "5.9"},
        "Toxic drugs": {"3.5", "3.10", "4.5", "5.2", "5.3"},
        "Tumor (CPA/posterior fossa)": {"3.6", "3.11", "4.5", "5.1", "5.10", "5.17"},
        "Cardiac": {"2.4", "5.20"},
        "Cervicogenic": {"5.7", "7.4", "7.5"},
        "Orthostatic hypotension": {"4.3", "6.4", "7.3"},
        "Anemia": {"2.4", "2.5"},
        "Peripheral neuropathy": {"5.21"},
        "Phobic dizziness": {"2.5", "4.9", "7.6"}
    }

    possible_diseases = []
    for disease, codes in disease_mapping.items():
        match_score = len(codes.intersection(selected_codes)) / len(codes)
        if match_score >= 0.4:
            possible_diseases.append((disease, f"{match_score*100:.0f}%"))

    if possible_diseases:
        st.subheader("กลุ่มโรคที่อาจเกี่ยวข้อง")
        for disease, score in sorted(possible_diseases, key=lambda x: -float(x[1][:-1])):
            st.markdown(f"- {disease} ({score} ตรงกับอาการ)")
    else:
        st.warning("ไม่สามารถวิเคราะห์โรคเบื้องต้นได้จากข้อมูลที่ให้")
        
    # ---------- สร้าง DataFrame ใหม่ (โรค + คำอธิบายรหัส) ----------
    def codes_to_text(codes:set[str]):
        return ", ".join(code_desc.get(c, c) for c in sorted(codes))

    df_final = pd.DataFrame([
        {"กลุ่มโรค": disease,
        "อาการที่เกี่ยวข้อง": codes_to_text(codes)}
        for disease, codes in disease_mapping.items()
    ])

    st.subheader("กลุ่มโรคและอาการอ้างอิง")
    st.dataframe(df_final, use_container_width=True)

    st.markdown("---")
    st.subheader("กลุ่มโรคและรหัสอาการอ้างอิง (จากเอกสาร)")
    df_final = pd.DataFrame([
        {"กลุ่มโรค": disease, "รหัสที่เกี่ยวข้อง": ", ".join(sorted(codes))}
        for disease, codes in disease_mapping.items()
    ])
    st.dataframe(df_final)
    
        # เก็บโรคที่เข้าเค้า (ชื่อ) และรหัสอาการ
    matched_disease_names = [d[0] for d in possible_diseases]
    matched_disease_scores = [d[1] for d in possible_diseases]

    # เตรียมข้อมูลให้ครบถ้วน
    user_data = {
        # --- ข้อมูลพื้นฐาน ---
        "เพศ": gender,
        "อายุ": age,
        "อาชีพ": occupation,
        "โรคประจำตัว": ", ".join(diseases),
        "โรคอื่นๆ": disease_others,
        "ยา": medications,
        "สารเสพติด": substances,
        
        # --- ประวัติเวียนศีรษะ ---
        "เคยเวียนศีรษะ": prev_dizzy,
        "โรคเวียนศีรษะ": locals().get("dizzy_disease", ""),
        "ช่วงเวลาเคยเวียน": locals().get("dizzy_time", ""),
        "ครอบครัวเคยเวียนศีรษะ": family_history,
        "โรคของครอบครัว": locals().get("family_disease", ""),
        # "ประวัติเจ็บป่วย": ", ".join(history),
        # "สิ่งกระตุ้น": ", ".join(triggers),
        # "อาการร่วม": ", ".join(symptoms),
        "อาหารกระตุ้น (trigger9)": locals().get("food_trigger9", ""),
        "อาการอื่นๆ": locals().get("other_symptom", ""),

        # --- เพศหญิง ---
        "สถานะประจำเดือน": locals().get("period_status", ""),
        "วันที่มีประจำเดือนล่าสุด": str(locals().get("last_period_date", "")),

        # --- ลักษณะอาการเวียนศีรษะ ---
        "อาการเวียนศีรษะ": ", ".join(dizzy_types),
        "อาการเวียนศีรษะอื่นๆ": locals().get("dizzy_other", ""),
        "ช่วงเวลาเริ่มต้น": f"{hours_ago} ชม / {days_ago} วัน / {weeks_ago} สัปดาห์ / {months_ago} เดือน",
        "แบบการเริ่มต้น": onset_type,
        "ระยะเวลา": duration_type,
        "ความถี่": dizzy_frequency_text,

        # --- การวิเคราะห์โรค ---
        "กลุ่มโรคที่เข้าเค้า": ", ".join([f"{name} ({score})" for name, score in possible_diseases]),
        "รหัสอาการ": ", ".join(sorted(selected_codes)),
        
    }
    
    # # --- Export CSV แบบ UTF-8 with BOM ---
    df_user = pd.DataFrame([user_data])
    buffer = io.BytesIO()
    df_user.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)

    st.download_button(
        label="ดาวน์โหลดข้อมูลแบบสอบถาม (.csv)",
        data=buffer,
        file_name=f"dizzy_questionnaire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime='text/csv'
    )
    
    #  1. สมัครฟอนต์ภาษาไทย (ถ้าใช้ Windows)
    pdfmetrics.registerFont(TTFont('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'))
    
        # ---- 1. ฟังก์ชันสร้าง PDF ทุกข้อมูล ----
    def generate_full_pdf(data: dict, path: str):
        """
        สร้าง PDF จาก dict 'data' (key=หัวข้อ, value=ข้อความ)
        แสดงครบทุก field / รองรับหลายหน้า
        """
        c = canvas.Canvas(path, pagesize=A4)
        pdfmetrics.registerFont(TTFont('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'))
        c.setFont("Tahoma", 16)

        # margin + ตำแหน่งเริ่มต้น
        x_left = 50
        y = 800
        line_height = 22

        # หัวเรื่อง
        c.drawString(x_left, y, "สรุปผลแบบสอบถามอาการเวียนศีรษะ")
        y -= line_height * 2

        for k, v in data.items():
            # แปลงค่า None / ว่าง ให้เป็นขีด -
            if v is None or v == "":
                v = "-"

            # ตัดข้อความยาวเกิน 90 อักษร
            text = f"{k}: {v}"
            max_len = 90
            while len(text) > max_len:
                c.drawString(x_left, y, text[:max_len])
                text = text[max_len:]
                y -= line_height
                if y < 60:   # เหลือพื้นที่ไม่พอ -> ขึ้นหน้าใหม่
                    c.showPage()
                    c.setFont("Tahoma", 16)
                    y = 800

            c.drawString(x_left, y, text)
            y -= line_height

            # ถ้าพื้นที่คงเหลือน้อยให้ขึ้นหน้า
            if y < 60:
                c.showPage()
                c.setFont("Tahoma", 16)
                y = 800

        c.showPage()
        c.save()
        

    # ---- 2. เรียกใช้แทนที่ของเดิม ----
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        generate_full_pdf(user_data, tmp_pdf.name)   # ← เปลี่ยนชื่อฟังก์ชัน
        with open(tmp_pdf.name, "rb") as f:
            st.download_button(
                label="📄 ดาวน์โหลด PDF (ข้อมูลครบทุกช่อง)",
                data=f.read(),
                file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
    os.unlink(tmp_pdf.name)
    
    
    # ---- 1. ฟังก์ชันสร้าง PDF + ตารางโรค ----
def generate_disease_pdf(data: dict, table_df: pd.DataFrame, path: str):
    """
    • data      : dict  ← user_data (ข้อมูลที่กรอกทุกช่อง)
    • table_df  : DataFrame  ← df_final (กลุ่มโรค + อาการข้อความ)
    • path      : ไฟล์ปลายทาง .pdf
    """
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.pagesizes import A4

    pdfmetrics.registerFont(TTFont('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'))
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Tahoma", 16)

    x_left, y = 50, 800
    line_h = 22

    # ---------- 1. ส่วนข้อมูลที่กรอก ----------
    c.drawString(x_left, y, "สรุปผลแบบสอบถามอาการเวียนศีรษะ")
    y -= line_h * 2

    for k, v in data.items():
        v = "-" if (v is None or v == "") else str(v)
        text = f"{k}: {v}"
        # ห่อบรรทัดยาว > 90 อักษร
        while len(text) > 90:
            c.drawString(x_left, y, text[:90])
            text = text[90:]
            y -= line_h
            if y < 60:
                c.showPage(); c.setFont("Tahoma", 16); y = 800
        c.drawString(x_left, y, text)
        y -= line_h
        if y < 60:
            c.showPage(); c.setFont("Tahoma", 16); y = 800

    # ---------- 2. ส่วนตารางกลุ่มโรค ----------
    y -= line_h   # เว้นบรรทัด
    if y < 120:   # ถ้าใกล้ขอบให้ขึ้นหน้าใหม่
        c.showPage(); c.setFont("Tahoma", 16); y = 800
    c.drawString(x_left, y, "กลุ่มโรคและอาการอ้างอิง")
    y -= line_h * 1.5

    for _, row in table_df.iterrows():
        disease = row["กลุ่มโรค"]
        symptoms = row["อาการที่เกี่ยวข้อง"]
        for line in [disease] + symptoms.split(", "):
            # แสดงชื่อโรคตัวหนา
            if line == disease:
                c.setFont("Tahoma", 16)
                text = f"• {line}"
            else:
                c.setFont("Tahoma", 14)
                text = f"   - {line}"
            c.drawString(x_left, y, text)
            y -= line_h
            if y < 60:
                c.showPage(); c.setFont("Tahoma", 16); y = 800

    c.showPage()
    c.save()
    
    # ---- 2. เรียกใช้แทนที่ของเดิม ----
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        generate_disease_pdf(user_data, df_final, tmp_pdf.name)   # ← ส่ง df_final เข้าไป

        with open(tmp_pdf.name, "rb") as f:
            st.download_button(
                label="📄 ดาวน์โหลด PDF (แบบสรุปแนวโน้มของ(โรค))",
                data=f.read(),
                file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )
    os.unlink(tmp_pdf.name)



    # #  2. สร้าง PDF ด้วยฟอนต์ Tahoma
    # def generate_thai_pdf(path, gender, age, dizzy_types, selected_codes, possible_diseases):
    #     c = canvas.Canvas(path, pagesize=A4)
    #     c.setFont("Tahoma", 16)
        
    #     text = c.beginText(40, 800)
    #     text.textLine("สรุปผลแบบสอบถามอาการเวียนศีรษะ")
    #     text.textLine(f"เพศ: {gender}")
    #     text.textLine(f"อายุ: {age}")
    #     text.textLine("อาการเวียนศีรษะ: " + ", ".join(dizzy_types))
    #     text.textLine("รหัสอาการที่เลือก:")
    #     for code in sorted(selected_codes):
    #         text.textLine(f" - {code}")
    #     text.textLine("กลุ่มโรคที่เข้าเค้า:")
    #     for d, score in possible_diseases:
    #         text.textLine(f" - {d} ({score})")
        
    #     c.drawText(text)
    #     c.showPage()
    #     c.save()

    # #  3. สร้างและดาวน์โหลด PDF ผ่าน Streamlit
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
    #     generate_thai_pdf(tmp_pdf.name, gender, age, dizzy_types, selected_codes, possible_diseases)
    #     with open(tmp_pdf.name, "rb") as f:
    #         st.download_button(
    #             label="📄 ดาวน์โหลด PDF ภาษาไทย (ReportLab)",
    #             data=f.read(),
    #             file_name=f"summary_dizzy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
    #             mime="application/pdf"
    #         )
    # os.unlink(tmp_pdf.name)
    
    st.markdown(
    "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 หลังตรวจสอบสรุปโรคเบื้องต้นแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 11 : Eye Tracking</span>",
    unsafe_allow_html=True
)
    


with tab11:  
        st.title("👁️ Eye Movement Detection with Logs & Analytics")
        
                # ---------- Instruction Card : Tab 11 ----------
        st.markdown("""
        <style>
        .guide-card{
        background:rgba(255,255,255,0.25);
        border-radius:18px;
        box-shadow:0 8px 32px rgba(31,38,135,.15);
        backdrop-filter:blur(12px);
        -webkit-backdrop-filter:blur(12px);
        border:1px solid rgba(255,255,255,0.18);
        padding:2.5rem;margin-bottom:32px;
        color:#0f172a;font-size:1.4rem !important;line-height:1.9rem;
        }
        .guide-card h1{font-size:2.8rem !important;margin-bottom:1.2rem;font-weight:800;}
        .guide-card ul{padding-left:2rem;margin:0;}
        .guide-card li{margin:10px 0;font-size:1.4rem;}
        .guide-card li::marker{color:#38bdf8;font-size:1.6rem;}
        </style>

        <div class="guide-card">
        <h1>📘 คู่มือการใช้งาน – Eye Tracking (Tab 11)</h1>

        <ul>
            <li>กด “<strong>อนุญาต</strong>” ให้เบราว์เซอร์เข้าถึง <strong>เว็บแคม</strong> เมื่อมี Pop-up ถาม</li>
            <li>นั่งให้ใบหน้าอยู่ <strong>กึ่งกลางกล้อง</strong> ระยะประมาณ 30–50 ซม.</li>
            <li>หน้าจอฝั่งซ้ายจะแสดง <em>ภาพสดพร้อมกรอบตรวจตา</em><br>
                ▸ ข้อความใต้กรอบจะบอกทิศสายตา ⬅️ ➡️ ⬆️ ✅</li>
            <li>หน้าจอฝั่งขวาแสดง <strong>สรุปสถิติ</strong> & “<em>Eye Movement Log</em>”</li>
            <li>จุดสีแดงเคลื่อนที่บนภาพใช้เป็น <em>เป้าฝึกการเพ่งสายตา</em><br>
                ▸ ลองมองตามเพื่อทดสอบระบบ</li>
            <li>เมื่อเสร็จสิ้น สามารถ <strong>ดาวน์โหลด CSV</strong> บันทึกทิศทางสายตาทั้งหมด</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

        # ---------- Red Notice : ไป Tab 12 ----------
        st.markdown(
            "<span style='color:#b91c1c;font-size:1.6rem;font-weight:bold;'>🔻 เสร็จสิ้นการทดสอบกล้องแล้ว&nbsp;&nbsp;เลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 12 : Motion Tracking (IMU)</span>",
            unsafe_allow_html=True
        )


        # Always run camera (no checkbox)
        col1, col2 = st.columns(2)
        with col1:
            FRAME_WINDOW = st.image([])
        with col2:
            summary_container = st.empty()

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

        LEFT_EYE_IDX = [362, 385, 387, 263, 373, 380]
        RIGHT_EYE_IDX = [33, 160, 158, 133, 153, 144]

        cap = cv2.VideoCapture(0)
        eye_log = []
        direction_memory = ""
        direction_counter = 0

        def detect_pupil_direction(eye_img):
            gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                M = cv2.moments(c)
                if M['m00'] != 0:
                    cx = int(M['m10'] / M['m00'])
                    w = eye_img.shape[1]
                    ratio = cx / w
                    if ratio < 0.35:
                        return "👈 Looking Left"
                    elif ratio > 0.65:
                        return "👉 Looking Right"
                    else:
                        return "⬆️ Looking Center"
            return "Eye Detected"

        # Limit frame count to prevent overload
        frame_count = 0
        MAX_FRAMES = 500  # Adjust as needed (e.g., 1000)

        while cap.isOpened() and frame_count < MAX_FRAMES:
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(frame_rgb)

            direction_text = "No face detected"

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                h, w, _ = frame.shape

                left_eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in LEFT_EYE_IDX]
                right_eye = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in RIGHT_EYE_IDX]

                for pt in left_eye + right_eye:
                    cv2.circle(frame, pt, 2, (0, 255, 0), -1)

                def crop_eye(eye_points):
                    x_vals = [pt[0] for pt in eye_points]
                    y_vals = [pt[1] for pt in eye_points]
                    x_min, x_max = max(min(x_vals) - 5, 0), min(max(x_vals) + 5, w)
                    y_min, y_max = max(min(y_vals) - 5, 0), min(max(y_vals) + 5, h)
                    return frame[y_min:y_max, x_min:x_max]

                left_crop = crop_eye(left_eye)
                right_crop = crop_eye(right_eye)

                left_dir = detect_pupil_direction(left_crop) if left_crop.size > 0 else ""
                right_dir = detect_pupil_direction(right_crop) if right_crop.size > 0 else ""

                if left_dir == right_dir and left_dir != "":
                    direction_text = left_dir
                else:
                    direction_text = left_dir or right_dir or "No Eye Detected"

                if direction_text == direction_memory:
                    direction_counter += 1
                else:
                    direction_counter = 0
                direction_memory = direction_text

                if direction_counter > 20:
                    direction_text += " ✅ Action Triggered"

                eye_log.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "direction": direction_text
                })
                
                # เพิ่มตัวแปรตำแหน่งจุดแดง
                target_positions = [(100, 100), (500, 100), (300, 250), (100, 400), (500, 400)]
                current_target_index = frame_count // 100 % len(target_positions)  # เปลี่ยนตำแหน่งทุก 100 เฟรม
                target_pos = target_positions[current_target_index]

                # วาดจุดสีแดงแบบเลือน (ใช้วงกลมโปร่งใส)
                overlay = frame.copy()
                cv2.circle(overlay, target_pos, 20, (0, 0, 255), -1)
                alpha_overlay = 0.5
                frame = cv2.addWeighted(overlay, alpha_overlay, frame, 1 - alpha_overlay, 0)

            # Display live frame
            cv2.putText(frame, direction_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            frame_count += 1

        cap.release()
        st.success("✅ Camera Stopped")

        df = pd.DataFrame(eye_log)
        if not df.empty:
            st.subheader("📜 Eye Movement Log")
            st.dataframe(df.tail(50))

            st.subheader("📊 Summary of Eye Direction")
            counts = df["direction"].value_counts()
            fig, ax = plt.subplots()
            counts.plot(kind="bar", ax=ax, color='lightblue')
            ax.set_title("Summary of Eye Movements")
            ax.set_ylabel("Count")
            ax.set_xlabel("Direction")
            summary_container.pyplot(fig)

            csv = df.to_csv(index=False).encode()
            st.download_button("💾 Download Log as CSV", csv, "eye_log.csv", "text/csv")
            
            
with tab12:
    # ---------- PAGE HEADER ----------
    st.title("📈 Real-time Motion Tracking from IMU (M5StickC)")
    st.markdown("""
- ต่อไฟให้ **M5StickC** แล้วตั้งค่า MQTT  
  ▸ **Broker** : `broker.emqx.io`   ▸ **Topic** : `thammasat/aueaphum/sensor`  
- วางเซนเซอร์ไว้ที่ **ด้านข้างศีรษะ** หรือ **ข้อมือ**  
- หน้านี้จะแสดงกราฟ **AX AY AZ GX GY GZ** (Smooth α = 0.1)  
- กล่องด้านบนบอก **Pitch / Roll / Yaw** และ ทิศศีรษะ 👁  
""")

    # ---------- MQTT CONFIG ----------
    MQTT_BROKER = "broker.emqx.io"
    MQTT_PORT   = 1883
    MQTT_TOPIC  = "thammasat/aueaphum/sensor"

    # ---------- PARAMETERS ----------
    window_size = 150       # จุดที่แสดงในกราฟ
    alpha       = 0.1       # smoothing factor
    REFRESH_EVERY = 10      # กี่เฟรมอัปเดตตาราง+สรุป

    # ---------- DATA STRUCTURE ----------
    data_dict = {k: deque(maxlen=window_size) for k in
                 ['AX','AY','AZ','GX','GY','GZ','Time']}
    smoothed  = {k: 0.0 for k in ['AX','AY','AZ','GX','GY','GZ']}
    imu_log   = []                          # บันทึกทุกเฟรม

    # ---------- PLACEHOLDERS ----------
    cols = st.columns(2)
    chart_ph = {                           # plotly charts
        'AX': cols[0].empty(), 'AY': cols[0].empty(), 'AZ': cols[0].empty(),
        'GX': cols[1].empty(), 'GY': cols[1].empty(), 'GZ': cols[1].empty()
    }
    head_box            = st.empty()      # Pitch/Roll/Yaw + Direction
    log_ph              = st.empty()      # ตาราง 30 แถวล่าสุด
    summary_ph          = st.empty()      # Avg/Max/Min
    trend_ph            = st.empty()      # แนวโน้มโรค
    download_ph         = st.empty()      # ปุ่ม CSV (หลังจบสตรีม)

    # ---------- MQTT CALLBACK ----------
    def on_message(client, userdata, msg):
        try:
            parts = msg.payload.decode().split(',')
            parsed = {kv.split(':')[0]: float(kv.split(':')[1]) for kv in parts}
            now = time.time()
            for k in smoothed:
                smoothed[k] = alpha*parsed[k] + (1-alpha)*smoothed[k]
                data_dict[k].append(smoothed[k])
            data_dict['Time'].append(now)
        except Exception as e:
            print("Parse error:", e)

    def start_mqtt():
        client = mqtt.Client()
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        client.loop_start()

    if 'mqtt_started' not in st.session_state:
        threading.Thread(target=start_mqtt, daemon=True).start()
        st.session_state['mqtt_started'] = True

    # ---------- HELPER ----------
    def calc_angles(ax, ay, az, gx, gy, gz):
        pitch = math.degrees(math.atan2(ax, math.sqrt(ay**2+az**2)))
        roll  = math.degrees(math.atan2(ay, math.sqrt(ax**2+az**2)))
        yaw   = gz   # (ใช้ Gyro-Z แทน)
        return pitch, roll, yaw

    def head_dir(p, r, y, th=15):
        if y >  th: return "Looking Right"
        if y < -th: return "Looking Left"
        if p >  th: return "Looking Up"
        if p < -th: return "Looking Down"
        return "Looking Center"

    # ---------- MAIN LOOP ----------
    counter   = 0
    RUN_TIME  = 180          # วินาที (3 นาที) : จบสตรีมอัตโนมัติ
    start_ts  = time.time()

    while time.time() - start_ts < RUN_TIME:
        time.sleep(0.25)
        counter += 1

        # -- Plot 6 แกน --
        for k in chart_ph:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=list(data_dict['Time']),
                                     y=list(data_dict[k]),
                                     mode='lines'))
            fig.update_layout(title=f"{k} (α = {alpha})",
                              height=220, margin=dict(l=10,r=10,t=30,b=25),
                              uirevision=k)
            chart_ph[k].plotly_chart(fig, use_container_width=True,
                                     key=f"{k}_{counter}")

        # -- ถ้ายังไม่มีข้อมูลก็วนต่อ --
        if not data_dict['Time']:
            continue

        # -- ค่าเฟรมล่าสุด --
        ax,ay,az = data_dict['AX'][-1], data_dict['AY'][-1], data_dict['AZ'][-1]
        gx,gy,gz = data_dict['GX'][-1], data_dict['GY'][-1], data_dict['GZ'][-1]
        pitch, roll, yaw = calc_angles(ax,ay,az,gx,gy,gz)
        direction        = head_dir(pitch, roll, yaw)

        head_box.markdown(f"""
        <div style="font-size:28px;font-weight:bold;color:#336699;
             background:#f0f9ff;padding:10px;border-radius:10px;">
            🧠 Head Motion<br>
            👁 {direction}<br>
            <span style='font-size:16px;'>
            Pitch {pitch:.1f}° • Roll {roll:.1f}° • Yaw {yaw:.1f}°
            </span>
        </div>""", unsafe_allow_html=True)

        # -- LOG เฟรม --
        imu_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "pitch": pitch, "roll": roll, "yaw": yaw,
            "direction": direction.replace("Looking ","")
        })

        # -- ทุก REFRESH_EVERY เฟรม : อัปเดตตาราง/สรุป/แนวโน้ม --
        if counter % REFRESH_EVERY == 0:
            df = pd.DataFrame(imu_log)
            log_ph.dataframe(df.tail(30), use_container_width=True)

            stats = df[["pitch","roll","yaw"]].agg(["mean","max","min"]).round(2)
            summary_ph.markdown(f"""
|  | Pitch | Roll | Yaw |
|--|------:|-----:|----:|
|Avg| {stats.loc['mean','pitch']}° | {stats.loc['mean','roll']}° | {stats.loc['mean','yaw']}° |
|Max| {stats.loc['max','pitch']}° | {stats.loc['max','roll']}° | {stats.loc['max','yaw']}° |
|Min| {stats.loc['min','pitch']}° | {stats.loc['min','roll']}° | {stats.loc['min','yaw']}° |
""")

            # ---- แนวโน้มโรคอย่างหยาบ ----
            avg_p, avg_r, avg_y = stats.loc['mean','pitch'], stats.loc['mean','roll'], stats.loc['mean','yaw']
            trends = []
            if abs(avg_y) > 25:
                trends.append("◼️ *Vestibular neuritis* — เบี่ยงศีรษะซ้าย-ขวาชัด")
            if abs(avg_p) > 25:
                trends.append("◼️ *BPPV* — กระตุ้นเมื่อเปลี่ยนท่าทางศีรษะ")
            if avg_r > 20:
                trends.append("◼️ *Meniere’s disease* — เวียนหมุนด้านใดด้านหนึ่ง")
            if not trends:
                trends.append("◼️ *ยังไม่พบรูปแบบเฉพาะเจาะจง*")

            trend_ph.markdown("#### 🩺 แนวโน้มโรคจาก Motion (เบื้องต้น)")
            trend_ph.markdown("\n".join(trends))

    # ---------- END STREAM ----------
    st.success("✅ สตรีมจบแล้ว (ประมาณ 3 นาที)")

    # ---------- DOWNLOAD CSV ----------
    if imu_log:
        csv_bytes = pd.DataFrame(imu_log).to_csv(index=False).encode("utf-8-sig")
        download_ph.download_button(
            "💾 Download IMU Pitch-Roll-Yaw (CSV)",
            csv_bytes,
            file_name=f"imu_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("ยังไม่มีข้อมูลให้บันทึก (อาจไม่ได้รับแพ็กเก็ต MQTT)")
          
            
# with tab12:
#     st.title("📈 Real-time Motion Tracking from IMU (M5StickC)")
#     st.markdown("""
#     - ต่อไฟให้ **M5StickC** แล้วเปิดให้ส่งค่าผ่าน **MQTT**

#     ▸ **Broker** : `broker.emqx.io`  
#     ▸ **Topic** : `thammasat/aueaphum/sensor`

#     - ให้เซนเซอร์อยู่ในตำแหน่ง **ด้านข้างศีรษะหรือข้อมือ** (ตามที่ระบุในงานวิจัย)

#     - เมื่อเชื่อมต่อสำเร็จ จะเห็นกราฟ **AX AY AZ GX GY GZ** เคลื่อนไหวแบบเรียลไทม์

#     - ค่าทุกแกนจะแสดงแบบ **Smooth** (α = 0.1) เพื่อลดสัญญาณรบกวน

#     - แถบสรุปด้านบนจะแสดง **Pitch / Roll / Yaw** และบอกทิศทางศีรษะ  
#     ▸ “👁 Looking Left / Right / Up / Down / Center”

#     - หากไม่เห็นข้อมูล ให้ตรวจสอบว่า  
#     ▸ เซนเซอร์ออนไลน์อยู่หรือไม่  
#     ▸ Wi-Fi & MQTT ตั้งค่าถูกต้อง

#     - ⚙️ คุณสามารถปรับ `window_size` หรือ `alpha` ในโค้ดเพื่อให้กราฟนุ่มขึ้น/เร็วขึ้น
#     """)

#     # ข้อความสีแดงแจ้งสิ้นสุด
#     st.markdown(
#         "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>✅ เสร็จสิ้นขั้นตอนทั้งหมด หากต้องการกลับไปตรวจสอบข้อมูล สามารถคลิกที่ Tab ใดก็ได้ด้านบน</span>",
#         unsafe_allow_html=True
#     )

#     st.markdown("แสดงกราฟข้อมูลแบบเรียลไทม์ พร้อมคำนวณ Pitch, Roll, Yaw และแสดงทิศทางการมองศีรษะ")

#     # ---------- MQTT CONFIG ----------
#     MQTT_BROKER = "broker.emqx.io"
#     MQTT_PORT = 1883
#     MQTT_TOPIC = "thammasat/aueaphum/sensor"

#     # ---------- PARAMETERS ----------
#     window_size = 150
#     alpha = 0.1

#     data_dict = {
#         'AX': deque(maxlen=window_size),
#         'AY': deque(maxlen=window_size),
#         'AZ': deque(maxlen=window_size),
#         'GX': deque(maxlen=window_size),
#         'GY': deque(maxlen=window_size),
#         'GZ': deque(maxlen=window_size),
#         'Time': deque(maxlen=window_size)
#     }
#     smoothed = {k: 0.0 for k in ['AX', 'AY', 'AZ', 'GX', 'GY', 'GZ']}

#     # ---------- MQTT CALLBACK ----------
#     def on_message(client, userdata, msg):
#         try:
#             payload = msg.payload.decode()
#             parts = payload.split(',')
#             parsed = {kv.split(':')[0]: float(kv.split(':')[1]) for kv in parts}
#             now = time.time()
#             for k in smoothed:
#                 smoothed[k] = alpha * parsed[k] + (1 - alpha) * smoothed[k]
#                 data_dict[k].append(smoothed[k])
#             data_dict['Time'].append(now)
#         except Exception as e:
#             print("Parse error:", e)

#     # ---------- START MQTT THREAD ----------
#     def start_mqtt():
#         client = mqtt.Client()
#         client.on_message = on_message
#         client.connect(MQTT_BROKER, MQTT_PORT, 60)
#         client.subscribe(MQTT_TOPIC)
#         client.loop_start()

#     if 'mqtt_started' not in st.session_state:
#         threading.Thread(target=start_mqtt, daemon=True).start()
#         st.session_state['mqtt_started'] = True

#     # ---------- STREAMLIT UI ----------
#     st.set_page_config(page_title="Smooth IMU Viewer", layout="wide")
#     st.title("📡 Ultra Smooth Real-time IMU Sensor from M5StickC")

#     cols = st.columns(2)
#     placeholders = {
#         'AX': cols[0].empty(), 'AY': cols[0].empty(), 'AZ': cols[0].empty(),
#         'GX': cols[1].empty(), 'GY': cols[1].empty(), 'GZ': cols[1].empty()
#     }
#     eye_info_box = st.empty()

#     # ---------- HELPER FUNCTIONS ----------
#     def calculate_angles(ax, ay, az, gx, gy, gz):
#         pitch = math.atan2(ax, math.sqrt(ay ** 2 + az ** 2)) * (180.0 / math.pi)
#         roll = math.atan2(ay, math.sqrt(ax ** 2 + az ** 2)) * (180.0 / math.pi)
#         yaw = gz  # ใช้ gyroscope แทน (ต้องการ yaw จริงต้องใช้ sensor fusion)
#         return pitch, roll, yaw

#     def interpret_head_direction(pitch, roll, yaw, threshold=15):
#         if yaw > threshold:
#             return "👁 Looking Right"
#         elif yaw < -threshold:
#             return "👁 Looking Left"
#         elif pitch > threshold:
#             return "👁 Looking Up"
#         elif pitch < -threshold:
#             return "👁 Looking Down"
#         else:
#             return "👁 Looking Center"

#     # ---------- MAIN LOOP ----------
#     counter = 0
#     while True:
#         time.sleep(0.2)
#         counter += 1

#         for k in placeholders:
#             x = list(data_dict['Time'])
#             y = list(data_dict[k])

#             fig = go.Figure()
#             fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=k))
#             fig.update_layout(
#                 title=f"{k} (Smoothed α={alpha})",
#                 xaxis_title="Time",
#                 yaxis_title=k,
#                 height=250,
#                 margin=dict(l=20, r=20, t=30, b=30),
#                 uirevision=k
#             )

#             placeholders[k].plotly_chart(fig, use_container_width=True, key=f"{k}_chart_{counter}")

#         # คำนวณ pitch, roll, yaw และวิเคราะห์ทิศทาง
#         ax = data_dict['AX'][-1] if data_dict['AX'] else 0.0
#         ay = data_dict['AY'][-1] if data_dict['AY'] else 0.0
#         az = data_dict['AZ'][-1] if data_dict['AZ'] else 0.0
#         gx = data_dict['GX'][-1] if data_dict['GX'] else 0.0
#         gy = data_dict['GY'][-1] if data_dict['GY'] else 0.0
#         gz = data_dict['GZ'][-1] if data_dict['GZ'] else 0.0

#         pitch, roll, yaw = calculate_angles(ax, ay, az, gx, gy, gz)
#         direction = interpret_head_direction(pitch, roll, yaw)

#         eye_info_box.markdown(f"""
#         <div style="font-size:28px; font-weight:bold; color:#336699; padding:10px; background-color:#f0f9ff; border-radius:10px;">
#             🧠 Head Motion Analysis<br>
#             {direction}<br>
#             <span style='font-size:16px;'>Pitch = {pitch:.2f}°, Roll = {roll:.2f}°, Yaw = {yaw:.2f}</span>
#         </div>
#         """, unsafe_allow_html=True)
        
        
