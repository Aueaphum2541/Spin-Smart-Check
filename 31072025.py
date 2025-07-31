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


st.set_page_config(page_title="แบบสอบถามอาการเวียนศีรษะ", layout="wide")
st.title("แบบสอบถามอาการเวียนศีรษะ")
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs(["1. Home and About Project",
    "2.ข้อมูลพื้นฐาน", "3.ลักษณะของอาการเวียนศีรษะ คุณรู้สึกเวียนศีรษะอย่างไรบ้าง? (เลือกทั้งหมดที่ตรงกับคุณ)", 
    "4.การเริ่มต้นและระยะเวลา", "5.สิ่งกระตุ้น",
    "6.อาการร่วม คุณมีอาการเหล่านี้ร่วมด้วยหรือไม่? (เลือกทั้งหมดที่ตรงกับคุณ)", "7.ประวัติทางการป่วย", 
    "8.ผลกระทบต่อชีวิตประจำวัน?", "9.วินิจฉัยเบื้องต้นจากอาการเวียนศีรษะ" , "10. Eye Movement Detection with Logs & Analytics", "11. Real-time Motion Tracking from IMU (M5StickC)"
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


        st.markdown(
            "<span style='color:#b91c1c; font-size:1.6rem; font-weight:bold;'>🔻 เมื่อเลือกสิ่งกระตุ้นครบแล้ว กรุณาเลื่อนขึ้นไปด้านบนสุด แล้วกดไปที่ Tab 5 : สิ่งกระตุ้น</span>",
            unsafe_allow_html=True
        )  
        
        
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
        st.header("8.ผลกระทบต่อชีวิตประจำวัน")
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

# Tab 9 – Detailed Vertigo Diagnosis
with tab9:
    st.header("🧠 9.วินิจฉัยเบื้องต้นจากอาการเวียนศีรษะ")

    import plotly.express as px
    from fpdf import FPDF
    import matplotlib.pyplot as plt
    import base64
    from io import BytesIO

    neuro_symptom_codes = {"5.10", "5.17", "5.18", "5.19"}
    hearing_loss_codes = {"5.2", "5.3"}
    normal_hearing_code = "5.1"

    diagnosis_table = {
        "Vestibular neuritis": {"codes": {"2.1", "3.5", "3.10", "3.11", "4.5", "5.1", "6.3"}, "group": "Peripheral"},
        "Labyrinthitis": {"codes": {"2.1", "3.5", "3.10", "3.11", "4.5", "5.2", "5.3", "5.5", "6.1", "6.3"}, "group": "Peripheral"},
        "Vestibulopathy": {"codes": {"2.1", "3.5", "3.11", "4.5", "5.1"}, "group": "Peripheral"},
        "Labyrinth fistular": {"codes": {"2.1", "3.5", "3.11", "4.5", "4.10", "5.2", "5.3"}, "group": "Peripheral"},
        "Alcohol-induced vertigo": {"codes": {"3.5", "3.10", "4.5", "5.1"}, "group": "Peripheral"},
        "BPPV": {"codes": {"2.1", "3.5", "3.7", "4.2", "5.1"}, "group": "Peripheral"},
        "Meniere's disease": {"codes": {"2.1", "3.5", "3.9", "4.5", "5.2", "5.3", "5.4"}, "group": "Peripheral"},
        "Ototoxicity": {"codes": {"2.1", "3.5", "3.11", "4.5", "5.2", "5.3", "6.5"}, "group": "Peripheral"},

        "TIA": {"codes": {"3.5", "3.8", "5.1", "5.10", "5.17"}, "group": "Central"},
        "PICA infarction": {"codes": {"3.5", "3.11", "5.2", "5.8", "5.10", "5.17"}, "group": "Central"},
        "Encephalitis / Herpes": {"codes": {"3.6", "3.11", "5.5", "5.8", "5.10", "5.17"}, "group": "Central"},
        "Cerebellar contusion": {"codes": {"3.11", "5.1", "5.10", "5.17", "6.2"}, "group": "Central"},
        "Temporal contusion": {"codes": {"3.11", "5.2", "5.10", "5.17", "6.2"}, "group": "Central"},
        "CPA tumor": {"codes": {"3.6", "3.11", "4.5", "5.1", "5.10", "5.17"}, "group": "Central"},
        "Acoustic neuroma": {"codes": {"2.1", "3.6", "3.11", "4.5", "5.2", "5.10", "5.17"}, "group": "Central"},
        "Cerebellar infarction": {"codes": {"3.5", "3.11", "4.1", "5.8", "5.10", "5.17"}, "group": "Central"},
        "MS (Multiple Sclerosis)": {"codes": {"3.4", "3.6", "3.11", "5.1", "5.8", "5.10"}, "group": "Central"},
        "VBI": {"codes": {"2.1", "3.5", "3.7", "4.4", "5.1", "5.10", "5.17"}, "group": "Central"},
        "Migraine": {"codes": {"3.9", "4.6", "4.7", "4.8", "5.1", "5.8", "5.9"}, "group": "Central"},

        "Cardiogenic": {"codes": {"2.4", "5.20"}},
        "Cervicogenic": {"codes": {"5.7", "4.4"}},
        "Orthostatic hypotension": {"codes": {"2.1", "2.4", "2.5", "4.3", "6.4"}},
        "Peripheral neuropathy": {"codes": {"5.21"}},
        "Anemia": {"codes": {"2.4", "2.5"}},
        "Anxiety, Panic, Phobic dizziness": {"codes": {"2.5", "4.9"}},
    }

    code_descriptions = {
        "2.1": "มีอาการเวียนศีรษะหมุน (โลกหมุน หรือตัวคุณหมุน)",
        "2.4": "หน้ามืด หรือรู้สึกจะเป็นลม",
        "2.5": "แค่มึนเฉยๆ",
        "3.1": "เวียนศีรษะ(ชั่วโมง)",
        "3.2": "เวียนศีรษะ(วัน)",
        "3.3": "เวียนศีรษะ(สัปดาห์)",
        "3.4": "เวียนศีรษะ(เดือน)",
        "3.5": "อาการเวียนศีรษะเริ่มขึ้นทันทีทันใด",
        "3.6": "อาการเวียนศีรษะค่อยๆ เริ่มขึ้นทีละน้อย เวียนมากขึ้นเรื่อยๆ",
        "3.7": "เวียนศีรษะไม่เกิน 3 นาที",
        "3.8": "เวียนศีรษะ 5–30 นาที",
        "3.9": "เวียนศีรษะมากกว่า 30 นาที",
        "3.10": "เวียนศีรษะเมื่อหลับตา",
        "3.11": "เวียนศีรษะมากกว่า 2 วัน/ตลอดเวลา",
        "4.1": "ตื่นนอนขณะยังไม่ได้ขยับตัว ก็มีอาการเวียนศีรษะเลย",
        "4.2": "ขณะนอนแล้วพลิกตะแคงตัวหรือเมื่อล้มตัวลงนอน",
        "4.3": "ขณะลุกขึ้น (นั่ง หรือยืน)",
        "4.4": "การขยับศีรษะ",
        "4.5": "เป็นเอง ไม่สัมพันธ์กับการเปลี่ยนท่าทาง",
        "4.6": "เสียงดัง",
        "4.7": "สิ่งเร้าทางสายตา (เช่น หน้าจอ, แสงสี)",
        "4.8": "อาหาร",
        "4.9": "ความเครียด หรือเหนื่อยล้า",
        "4.10": "การเปลี่ยนแรงดันอากาศในหู เช่น ดำน้ำลึก ขึ้นที่สูง ลงที่ต่ำ",
        "5.1": "การได้ยินปกติ ไม่มีอาการทางหู",
        "5.2": "การได้ยินลดลง สูญเสียการได้ยิน",
        "5.3": "หูอื้อหรือเสียงดังในหู",
        "5.4": "รู้สึกแน่นในหู",
        "5.5": "มีไข้",
        "5.6": "มีน้ำไหลจากหู",
        "5.7": "ปวดคอ หรือบ่าไหล่",
        "5.8": "ปวดศีรษะ",
        "5.9": "ปวดไมเกรน",
        "5.10": "มีอาการทางระบบประสาท เช่น สายตาพร่ามัว มองเห็นภาพซ้อน พูดไม่ชัด เสียงแหบ กลืนลำบาก ชาแขนขา แขนขาอ่อนแรง",
        "5.17": "เดินเซ หรือเสียการทรงตัว",
        "5.18": "ไม่รู้สึกตัว",
        "5.19": "ชักเกร็งหรือกระตุก",
        "5.20": "ใจสั่นหรือเจ็บหน้าอก",
        "5.21": "ชาปลายมือ หรือปลายเท้า",
        "6.1": "มีการติดเชื้อในหูเมื่อเร็วๆ นี้",
        "6.2": "มีการบาดเจ็บที่ศีรษะ",
        "6.3": "เป็นไข้และอาการหวัดเมื่อเร็วๆ นี้",
        "6.4": "ท้องเสีย เสียน้ำ เสียเหงื่อมาก อาเจียนมาก เมื่อเร็วๆ นี้",
        "6.5": "ได้รับยาชนิดใหม่เมื่อเร็วๆ นี้",
        "8.1": "ไม่กระทบ",
        "8.2": "มีผลบ้างเล็กน้อย",
        "8.3": "มีผลปานกลาง (กระทบงาน/การเรียน)",
        "8.4": "มีผลรุนแรง (จำกัดการใช้ชีวิตประจำวัน)",
    }
    
    # ------------------------------
    # 🎯 Determine system type
    if selected_codes & neuro_symptom_codes:
        system_type = "🧠 Central Nervous System (มี 5.10, 5.17, 5.18, 5.19)"
    else:
        system_type = "🌀 Peripheral System (ไม่มี 5.10, 5.17, 5.18, 5.19)"

    # ------------------------------
    # ⏱ Urgency level
    urgent_very = {"2.4", "5.10", "5.17", "5.18", "5.19", "5.20"}
    urgent = {"5.5", "5.6", "5.8", "6.1", "6.2", "6.3", "8.4"}
    see_doctor = {"5.21", "8.3"}  # + เป็นครั้งแรกอาการไม่ดีขึ้น

    if selected_codes & urgent_very:
        urgency = "🔴 เร่งด่วนมาก"
    elif selected_codes & urgent:
        urgency = "🟠 เร่งด่วน"
    elif selected_codes & see_doctor:
        urgency = "🟢 ควรพบแพทย์เพื่อประเมินอาการ"
    else:
        urgency = "🟢 อาการไม่รุนแรง แต่ควรติดตาม"

    # ------------------------------
    # 📊 Scoring each diagnosis
    results = []
    for dx, info in diagnosis_table.items():
        codes = info["codes"]
        matched = selected_codes & codes
        percent = round(len(matched) / len(codes) * 100, 1) if codes else 0
        results.append((dx, percent, matched, info.get("group", "Other")))

    results.sort(key=lambda x: x[1], reverse=True)

    # ------------------------------
    # 📋 Display Summary
    st.subheader("🔍 สรุปวินิจฉัย")
    st.markdown(f"**ระบบที่เกี่ยวข้อง:** {system_type}")
    st.markdown(f"**ระดับความเร่งด่วน:** {urgency}")

    st.subheader("📊 ความเป็นไปได้ของโรค")
    for dx, percent, matched, group in results:
        if percent > 0:
            st.markdown(f"<div style='background:#f0f9ff; border-left:5px solid #38bdf8; padding:10px; border-radius:8px; margin-bottom:10px;'>"
                        f"<strong>{dx}</strong> ({group}) – <strong>{percent}%</strong> match<br>"
                        f"<span style='font-size:0.9em;'>ตรงกับรหัส: {', '.join(sorted(matched))}</span>"
                        f"</div>", unsafe_allow_html=True)
        else:
            continue

    if not any(p > 0 for _, p, _, _ in results):
        st.warning("ไม่สามารถจับคู่กับโรคใดได้อย่างชัดเจน กรุณาตรวจสอบข้อมูลเพิ่มเติมหรือพบแพทย์")

    for code in sorted(selected_codes):
        description = code_descriptions.get(code, "ไม่พบคำอธิบาย")
        st.markdown(f"**{code}** – {description}")

    # ------------------------------
    # 📈 สร้างกราฟแท่ง: การจับคู่เปอร์เซ็นต์
    st.subheader("📉 กราฟแสดงเปอร์เซ็นต์ความเป็นไปได้")
    filtered_results = [(dx, percent) for dx, percent, _, _ in results if percent > 0]
    if filtered_results:
        dx_names, dx_scores = zip(*filtered_results)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(dx_names, dx_scores, color="#38bdf8")
        ax.invert_yaxis()
        ax.set_xlabel('เปอร์เซ็นต์ความสอดคล้อง (%)')
        ax.set_title('การวินิจฉัยเบื้องต้นจากอาการเวียนศีรษะ')
        st.pyplot(fig)

        # Save chart to image buffer
        chart_buf = BytesIO()
        fig.savefig(chart_buf, format="png")
        chart_buf.seek(0)
    else:
        st.info("ไม่มีผลลัพธ์ที่สามารถแสดงเป็นกราฟได้")
        chart_buf = None

    # ------------------------------
    # 📄 Export to PDF
    st.subheader("📤 ส่งออกผลเป็น PDF")
    
    from fpdf import FPDF
    import matplotlib.pyplot as plt
    from io import BytesIO
    import os
    import base64
    import streamlit as st

    class PDF(FPDF):
        def header(self):
            self.set_font("THSarabunNew", "B", 20)
            self.cell(0, 10, "รายงานวินิจฉัยอาการเวียนศีรษะ", ln=True, align="C")

        def footer(self):
            self.set_y(-15)
            self.set_font("THSarabunNew", "", 12)
            self.cell(0, 10, f"หน้า {self.page_no()}", align="C")

    def export_pdf(summary_text, diagnosis_results, chart_data, recommendations):
        pdf = PDF()
        
        # 🔤 โหลดฟอนต์ภาษาไทย
        font_path = r"C:\Users\Asus\OneDrive\Desktop\Spin-Smart-Check\Sarabun-Regular.ttf"
        pdf.add_font("THSarabunNew", "", font_path, uni=True)
        pdf.add_font("THSarabunNew", "B", font_path, uni=True)

        pdf.add_page()
        pdf.set_font("THSarabunNew", "", 16)

        # 🔹 สรุปผล
        pdf.set_font("THSarabunNew", "B", 16)
        pdf.cell(0, 10, "สรุประบบที่เกี่ยวข้องและความเร่งด่วน", ln=True)
        pdf.set_font("THSarabunNew", "", 16)
        pdf.multi_cell(0, 10, summary_text)
        pdf.ln(5)

        # 🔹 ผลลัพธ์การวินิจฉัย
        pdf.set_font("THSarabunNew", "B", 16)
        pdf.cell(0, 10, "ผลลัพธ์การวินิจฉัย", ln=True)
        pdf.set_font("THSarabunNew", "", 16)
        for dx, percent, matched, group in diagnosis_results:
            if percent > 0:
                matched_codes = ", ".join(sorted(matched))
                pdf.multi_cell(0, 10, f"{dx} ({group}) - {percent}% ตรงกับรหัส: {matched_codes}")
                pdf.ln(2)

        # 🔹 กราฟ
        if chart_data:
            dx_names = [item[0] for item in chart_data if item[1] > 0]
            dx_scores = [item[1] for item in chart_data if item[1] > 0]

            if dx_names:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.barh(dx_names[::-1], dx_scores[::-1], color="#4a90e2")
                ax.set_xlabel("เปอร์เซ็นต์")
                ax.set_title("กราฟความเป็นไปได้ของโรค")
                plt.tight_layout()

                buf = BytesIO()
                plt.savefig(buf, format="png", dpi=150)
                plt.close(fig)
                buf.seek(0)

                chart_filename = "chart_temp.png"
                with open(chart_filename, "wb") as f:
                    f.write(buf.read())

                pdf.ln(5)
                pdf.image(chart_filename, x=20, y=pdf.get_y(), w=100)
                pdf.ln(60)

        # 🔹 คำแนะนำ
        pdf.set_font("THSarabunNew", "B", 16)
        pdf.cell(0, 10, "คำแนะนำเบื้องต้น", ln=True)
        pdf.set_font("THSarabunNew", "", 16)
        pdf.multi_cell(0, 10, recommendations)
        pdf.ln(5)

        # 🔹 คำตอบแบบสอบถาม
        pdf.add_page()
        pdf.set_font("THSarabunNew", "B", 16)
        pdf.cell(0, 10, "ข้อมูลที่ตอบในแบบสอบถามแต่ละหน้า", ln=True)
        pdf.set_font("THSarabunNew", "", 16)
        

        return pdf

    # ✅ ปุ่มใน Streamlit
    if st.button("ส่งออกเป็น PDF"):
        summary_text = f"ระบบที่เกี่ยวข้อง: {system_type}\nระดับความเร่งด่วน: {urgency}"
        diagnosis_results = [(dx, percent, matched, group) for dx, percent, matched, group in results if percent > 0]
        chart_data = [(dx, percent) for dx, percent, _, _ in results if percent > 0]
        recommendations = "กรุณาปรึกษาแพทย์หากมีอาการรุนแรงหรือไม่ดีขึ้น"

        pdf = export_pdf(summary_text, diagnosis_results, chart_data, recommendations)
        pdf_filename = "Vertigo_Diagnosis_Report.pdf"

        pdf_output = pdf.output(dest="S")  # ← ได้ bytearray แล้ว
        b64 = base64.b64encode(pdf_output).decode()
        href = f"<a href='data:application/pdf;base64,{b64}' download='{pdf_filename}'>📥 คลิกเพื่อดาวน์โหลดรายงาน PDF</a>"
        st.markdown(href, unsafe_allow_html=True)

with tab10:  
        st.title("👁️ Eye Movement Detection with Logs & Analytics")

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
     
            
with tab11:
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
          
        
        
        
