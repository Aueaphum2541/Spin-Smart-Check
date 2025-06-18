import streamlit as st
from datetime import datetime
import pandas as pd
import io
from xhtml2pdf import pisa
import tempfile
import os
import base64

st.set_page_config(page_title="แบบสอบถามอาการเวียนศรีษะ", layout="wide")
st.title("แบบสอบถามอาการเวียนศรีษะ")
st.markdown("กรณีผู้ป่วยไม่สามารถทำแบบสอบถามเองได้ ให้ผู้ดูแลช่วยทำให้ได้")

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "1.ข้อมูลพื้นฐาน", "2.ลักษณะของอาการเวียนศรีษะ คุณรู้สึกเวียนศรีษะอย่างไรบ้าง? (เลือกทั้งหมดที่ตรงกับคุณ)", 
    "3.การเริ่มต้นและระยะเวลา", "4.สิ่งกระตุ้น",
    "5.อาการร่วม คุณมีอาการเหล่านี้ร่วมด้วยหรือไม่? (เลือกทั้งหมดที่ตรงกับคุณ)", "6.ประวัติทางการป่วย", 
    "7.สิ่งที่ทำให้อาการของคุณแย่ลง?", "8.ผลกระทบต่อชีวิตประจำวัน", "9.สรุปผลเบื้องต้น"
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