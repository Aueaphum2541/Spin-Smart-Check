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



st.set_page_config(page_title="แบบสอบถามอาการเวียนศรีษะ", layout="wide")
st.title("แบบสอบถามอาการเวียนศรีษะ")
st.markdown("กรณีผู้ป่วยไม่สามารถทำแบบสอบถามเองได้ ให้ผู้ดูแลช่วยทำให้ได้")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
    "1.ข้อมูลพื้นฐาน", "2.ลักษณะของอาการเวียนศรีษะ คุณรู้สึกเวียนศรีษะอย่างไรบ้าง? (เลือกทั้งหมดที่ตรงกับคุณ)", 
    "3.การเริ่มต้นและระยะเวลา", "4.สิ่งกระตุ้น",
    "5.อาการร่วม คุณมีอาการเหล่านี้ร่วมด้วยหรือไม่? (เลือกทั้งหมดที่ตรงกับคุณ)", "6.ประวัติทางการป่วย", 
    "7.สิ่งที่ทำให้อาการของคุณแย่ลง?", "8.ผลกระทบต่อชีวิตประจำวัน", "9.สรุปผลเบื้องต้น", "10.Eye Tracking","11.Motion Tracking"
])

with tab1:
    st.header("1. ข้อมูลพื้นฐาน")
    col1, col2 = st.columns(2)
    with col1:
        gender = st.radio("เพศ", ["หญิง", "ชาย", "LGBTQ+", "ไม่ระบุ"])
        age = st.number_input("อายุ (ปี)", min_value=0, max_value=120)
        occupation = st.text_input("อาชีพ")
        
    with col2:
        diseases = st.multiselect("โรคประจำตัว", ["ไม่มี", "เบาหวาน", "ความดันสูง", "ความดันต่ำ", "โรคหัวใจ", "ไมเกรน", "โรคทางสมอง", "โรคอื่นๆ"])
        disease_others = st.text_input("ระบุโรคทางสมอง / อื่นๆ (ถ้ามี)")
        medications = st.text_input("ยาที่ท่านใช้ / ระบุว่าไม่ได้ทานยาอะไร")
        substances = st.text_input("สารเสพติดหรือสารพิษที่สัมผัส (ถ้ามี)")

    st.markdown("**อาการเวียนศีรษะในอดีต**")
    prev_dizzy = st.radio("เคยเวียนศีรษะมาก่อนหรือไม่?", ["เคย", "ไม่เคย"])
    family_history = st.radio("ประวัติครอบครัวมีอาการเวียนศีรษะหรือไม่?", ["มี", "ไม่มี"])
    history = st.multiselect("ประวัติการเจ็บป่วย", 
                            ["ไม่มี", "ได้รับยาชนิดใหม่", "ได้รับวัคซีน", "เคยผ่าตัด", "เคยได้รับการฉายรังสี", "เคยมีอุบัติเหตุที่ศีรษะ", "อื่นๆ"])
    triggers = st.multiselect("สิ่งกระตุ้นที่ทำให้เกิดอาการเวียนศีรษะ", 
                            ["ไม่มี", "อาหาร", "การเคลื่อนไหว", "ความเครียด", "แสงสว่าง", "เสียงดัง", "อื่นๆ"])
    symptoms = st.multiselect("อาการร่วมที่เกิดขึ้นพร้อมกับอาการเวียนศีรษะ", 
                            ["ไม่มี", "ปวดหัว", "คลื่นไส้", "อาเจียน", "หูอื้อ", "หูแว่ว", "มองเห็นภาพซ้อน", "มองเห็นภาพพร่า", "สูญเสียการทรงตัว", "อื่นๆ"])
    
    # กรณีมีหลายช่องใช้ label เดียวกัน "จากโรคอะไร?" ต้องแยก key
    if prev_dizzy == "เคย":
        dizzy_disease = st.text_input("จากโรคอะไร?", key="dizzy_disease")
        dizzy_time = st.text_input("เมื่อไหร่?", key="dizzy_time")

    if family_history == "มี":
        family_disease = st.text_input("จากโรคอะไร?", key="family_disease")

    if "ได้รับยาชนิดใหม่" in history:
        new_drug = st.text_input("ระบุชื่อยา", key="new_drug")

    if "อาหาร" in triggers:
        food_trigger = st.text_input("ระบุอาหาร", key="food_trigger1")

    if "อื่นๆ" in symptoms:
        other_symptom = st.text_input("โปรดระบุอาการอื่นๆ", key="other_symptom")
        
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
    
    with tab2:
        st.header("2. ลักษณะของอาการเวียนศีรษะ")
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

    with tab3:
        st.header("3. การเริ่มต้นและระยะเวลา")

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

        st.subheader("อาการเวียนศีรษะแต่ละครั้งกินเวลานานเท่าไหร่?")
        duration_type = st.selectbox("เลือกช่วงเวลา", [
            "___ วินาที (สูงสุด 180 วินาที) 3.7",
            "___ นาที (5 – 30) 3.8",
            "มากกว่า 30 นาที 3.9",
            "___ ชั่วโมง 3.9",
            "___ วัน 3.10",
            "มากกว่า 2 วัน เวียนตลอดเวลา ไม่มีช่วงหาย 3.11"
        ], key="duration_type")

        st.subheader("ความถี่ของอาการเวียนศีรษะ")
        dizzy_frequency = st.radio("คุณมีอาการบ่อยแค่ไหน?", [
            "ทุกวัน วันละ ___ ครั้ง",
            "1-3 ครั้ง/สัปดาห์",
            "4-6 ครั้ง/สัปดาห์",
            "นานๆ ที"
        ], key="dizzy_frequency")
        
        
    with tab4:
        st.header("4. สิ่งกระตุ้น")
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
        trigger_11 = st.checkbox("การเปลี่ยนแรงดันอากาศในหู เช่น ดำน้ำลึก ขึ้นที่สูง 4.10", key="trigger_11")
        trigger_12 = st.checkbox("ไม่มีสิ่งกระตุ้นที่ชัดเจน", key="trigger_12")


    with tab5:
        st.header("5. อาการร่วม")
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

    with tab6:
        st.header("6. ประวัติทางการเจ็บป่วย")
        illness_1 = st.checkbox("การติดเชื้อในหูเมื่อเร็วๆ นี้ 6.1", key="illness_1")
        illness_2 = st.checkbox("การบาดเจ็บที่ศีรษะ 6.2", key="illness_2")
        illness_3 = st.checkbox("เป็นไข้และอาการหวัดเมื่อเร็วๆ นี้ 6.3", key="illness_3")
        illness_4 = st.checkbox("ท้องเสีย เสียน้ำ เสียเหงื่อมาก อาเจียนมาก เมื่อเร็วๆ นี้ 6.4", key="illness_4")
        illness_5 = st.checkbox("ได้รับยาชนิดใหม่เมื่อเร็วๆ นี้ 6.5", key="illness_5")
        if illness_5:
            new_drug = st.text_input("ชื่อยา", key="new_drug")

    with tab7:
        st.header("7. สิ่งที่ทำให้อาการของคุณแย่ลง")
        worsen_1 = st.checkbox("ล้มตัวลงนอน 7.1", key="worsen_1")
        worsen_2 = st.checkbox("พลิกตัวบนเตียง 7.2", key="worsen_2")
        worsen_3 = st.checkbox("ลุกขึ้นเร็วเกินไป 7.3", key="worsen_3")
        worsen_4 = st.checkbox("เงยหน้า หรือก้มหน้า 7.4", key="worsen_4")
        worsen_5 = st.checkbox("หันศีรษะไปมาซ้ายขวา 7.5", key="worsen_5")
        worsen_6 = st.checkbox("ความเครียด เหนื่อยล้า พักผ่อนไม่เพียงพอ 7.6", key="worsen_6")

    with tab8:
        st.header("8. ผลกระทบต่อชีวิตประจำวัน")
        impact_level = st.radio("อาการเวียนศีรษะส่งผลต่อการใช้ชีวิตของคุณแค่ไหน?", [
            "ไม่กระทบ 8.1",
            "มีผลบ้างเล็กน้อย 8.2",
            "มีผลปานกลาง (กระทบงาน/การเรียน) 8.3",
            "มีผลรุนแรง (จำกัดการใช้ชีวิตประจำวัน) 8.4"
        ], key="life_impact")
        
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

# === TAB 9: วิเคราะห์ผล ===
with tab9:
    st.header("9. วิเคราะห์กลุ่มโรคเบื้องต้น")

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
    "ประวัติเจ็บป่วย": ", ".join(history),
    "สิ่งกระตุ้น": ", ".join(triggers),
    "อาการร่วม": ", ".join(symptoms),
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
    "ความถี่": dizzy_frequency,

    # --- การวิเคราะห์โรค ---
    "กลุ่มโรคที่เข้าเค้า": ", ".join([f"{name} ({score})" for name, score in possible_diseases]),
    "รหัสอาการ": ", ".join(sorted(selected_codes)),
}

# --- Export CSV แบบ UTF-8 with BOM ---
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


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import streamlit as st
import tempfile
import os

#  1. สมัครฟอนต์ภาษาไทย (ถ้าใช้ Windows)
pdfmetrics.registerFont(TTFont('Tahoma', 'C:/Windows/Fonts/tahoma.ttf'))

#  2. สร้าง PDF ด้วยฟอนต์ Tahoma
def generate_thai_pdf(path, gender, age, dizzy_types, selected_codes, possible_diseases):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Tahoma", 16)
    
    text = c.beginText(40, 800)
    text.textLine("สรุปผลแบบสอบถามอาการเวียนศีรษะ")
    text.textLine(f"เพศ: {gender}")
    text.textLine(f"อายุ: {age}")
    text.textLine("อาการเวียนศีรษะ: " + ", ".join(dizzy_types))
    text.textLine("รหัสอาการที่เลือก:")
    for code in sorted(selected_codes):
        text.textLine(f" - {code}")
    text.textLine("กลุ่มโรคที่เข้าเค้า:")
    for d, score in possible_diseases:
        text.textLine(f" - {d} ({score})")
    
    c.drawText(text)
    c.showPage()
    c.save()

#  3. สร้างและดาวน์โหลด PDF ผ่าน Streamlit
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
    generate_thai_pdf(tmp_pdf.name, gender, age, dizzy_types, selected_codes, possible_diseases)
    with open(tmp_pdf.name, "rb") as f:
        st.download_button(
            label="📄 ดาวน์โหลด PDF ภาษาไทย (ReportLab)",
            data=f.read(),
            file_name=f"summary_dizzy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
os.unlink(tmp_pdf.name)

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
    st.title("📈 Real-time Motion Tracking from IMU (M5StickC)")
    st.markdown("แสดงกราฟข้อมูลแบบเรียลไทม์ พร้อมคำนวณ Pitch, Roll, Yaw และแสดงทิศทางการมองศีรษะ")

    # ---------- MQTT CONFIG ----------
    MQTT_BROKER = "broker.emqx.io"
    MQTT_PORT = 1883
    MQTT_TOPIC = "thammasat/aueaphum/sensor"

    # ---------- PARAMETERS ----------
    window_size = 150
    alpha = 0.1

    data_dict = {
        'AX': deque(maxlen=window_size),
        'AY': deque(maxlen=window_size),
        'AZ': deque(maxlen=window_size),
        'GX': deque(maxlen=window_size),
        'GY': deque(maxlen=window_size),
        'GZ': deque(maxlen=window_size),
        'Time': deque(maxlen=window_size)
    }
    smoothed = {k: 0.0 for k in ['AX', 'AY', 'AZ', 'GX', 'GY', 'GZ']}

    # ---------- MQTT CALLBACK ----------
    def on_message(client, userdata, msg):
        try:
            payload = msg.payload.decode()
            parts = payload.split(',')
            parsed = {kv.split(':')[0]: float(kv.split(':')[1]) for kv in parts}
            now = time.time()
            for k in smoothed:
                smoothed[k] = alpha * parsed[k] + (1 - alpha) * smoothed[k]
                data_dict[k].append(smoothed[k])
            data_dict['Time'].append(now)
        except Exception as e:
            print("Parse error:", e)

    # ---------- START MQTT THREAD ----------
    def start_mqtt():
        client = mqtt.Client()
        client.on_message = on_message
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        client.loop_start()

    if 'mqtt_started' not in st.session_state:
        threading.Thread(target=start_mqtt, daemon=True).start()
        st.session_state['mqtt_started'] = True

    # ---------- STREAMLIT UI ----------
    st.set_page_config(page_title="Smooth IMU Viewer", layout="wide")
    st.title("📡 Ultra Smooth Real-time IMU Sensor from M5StickC")

    cols = st.columns(2)
    placeholders = {
        'AX': cols[0].empty(), 'AY': cols[0].empty(), 'AZ': cols[0].empty(),
        'GX': cols[1].empty(), 'GY': cols[1].empty(), 'GZ': cols[1].empty()
    }
    eye_info_box = st.empty()

    # ---------- HELPER FUNCTIONS ----------
    def calculate_angles(ax, ay, az, gx, gy, gz):
        pitch = math.atan2(ax, math.sqrt(ay ** 2 + az ** 2)) * (180.0 / math.pi)
        roll = math.atan2(ay, math.sqrt(ax ** 2 + az ** 2)) * (180.0 / math.pi)
        yaw = gz  # ใช้ gyroscope แทน (ต้องการ yaw จริงต้องใช้ sensor fusion)
        return pitch, roll, yaw

    def interpret_head_direction(pitch, roll, yaw, threshold=15):
        if yaw > threshold:
            return "👁 Looking Right"
        elif yaw < -threshold:
            return "👁 Looking Left"
        elif pitch > threshold:
            return "👁 Looking Up"
        elif pitch < -threshold:
            return "👁 Looking Down"
        else:
            return "👁 Looking Center"

    # ---------- MAIN LOOP ----------
    counter = 0
    while True:
        time.sleep(0.2)
        counter += 1

        for k in placeholders:
            x = list(data_dict['Time'])
            y = list(data_dict[k])

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=k))
            fig.update_layout(
                title=f"{k} (Smoothed α={alpha})",
                xaxis_title="Time",
                yaxis_title=k,
                height=250,
                margin=dict(l=20, r=20, t=30, b=30),
                uirevision=k
            )

            placeholders[k].plotly_chart(fig, use_container_width=True, key=f"{k}_chart_{counter}")

        # คำนวณ pitch, roll, yaw และวิเคราะห์ทิศทาง
        ax = data_dict['AX'][-1] if data_dict['AX'] else 0.0
        ay = data_dict['AY'][-1] if data_dict['AY'] else 0.0
        az = data_dict['AZ'][-1] if data_dict['AZ'] else 0.0
        gx = data_dict['GX'][-1] if data_dict['GX'] else 0.0
        gy = data_dict['GY'][-1] if data_dict['GY'] else 0.0
        gz = data_dict['GZ'][-1] if data_dict['GZ'] else 0.0

        pitch, roll, yaw = calculate_angles(ax, ay, az, gx, gy, gz)
        direction = interpret_head_direction(pitch, roll, yaw)

        eye_info_box.markdown(f"""
        <div style="font-size:28px; font-weight:bold; color:#336699; padding:10px; background-color:#f0f9ff; border-radius:10px;">
            🧠 Head Motion Analysis<br>
            {direction}<br>
            <span style='font-size:16px;'>Pitch = {pitch:.2f}°, Roll = {roll:.2f}°, Yaw = {yaw:.2f}</span>
        </div>
        """, unsafe_allow_html=True)
