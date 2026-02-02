import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ---------- Google Sheet Connection ----------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open("JMP_SYSTEM").worksheet("JMP_DATA")

# ---------- App ----------
st.title("Journey Management Plan (JMP)")

role = st.selectbox("Login as", ["Driver", "Supervisor", "Safety"])

# ---------- DRIVER ----------
if role == "Driver":
    st.subheader("Submit Journey")

    driver = st.text_input("Driver Name")
    company = st.text_input("Company")
    section = st.text_input("Section")
    vehicle = st.text_input("Vehicle Number")
    purpose = st.text_input("Trip Purpose")
    passengers = st.text_input("Passengers")
    from_loc = st.text_input("From")
    to_loc = st.text_input("To")
    dep = st.time_input("Departure Time")
    arr = st.time_input("Arrival Time")
    email = st.text_input("Your Email")

    if st.button("Submit JMP"):
        sheet.append_row([
            int(datetime.now().timestamp()),
            driver, company, section, vehicle,
            purpose, passengers,
            from_loc, to_loc,
            dep.strftime("%H:%M"),
            arr.strftime("%H:%M"),
            "Pending",
            email,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            "", "", "", ""
        ])
        st.success("Journey Submitted")

# ---------- SUPERVISOR / SAFETY ----------
if role in ["Supervisor", "Safety"]:
    st.subheader("Pending Journeys")

    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    pending = df[df["Status"] == "Pending"]

    for i, row in pending.iterrows():
        st.write(row)

        remark = st.text_input(f"Remark {i}")
        col1, col2 = st.columns(2)

        if col1.button(f"Approve {i}"):
            sheet.update_cell(i+2, 12, "Approved")
            sheet.update_cell(i+2, 15, role)
            sheet.update_cell(i+2, 16, remark)
            sheet.update_cell(i+2, 17, datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.success("Approved")

        if col2.button(f"Reject {i}"):
            sheet.update_cell(i+2, 12, "Rejected")
            sheet.update_cell(i+2, 15, role)
            sheet.update_cell(i+2, 16, remark)
            sheet.update_cell(i+2, 17, datetime.now().strftime("%Y-%m-%d %H:%M"))
            st.error("Rejected")
