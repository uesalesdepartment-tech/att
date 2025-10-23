import streamlit as st
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import geocoder
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Attendance with Location", page_icon="📍")
st.title("📍 Attendance with Location Check")

# --- Admin Location ---
ADMIN_LAT = 21.2333
ADMIN_LON = 81.6333
ALLOWED_RADIUS = 0.1  # km (100 meters)

# --- Haversine Distance ---
def distance_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

# --- Google Sheets Setup ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)
spreadsheet = client.open("Attendance")
worksheet = spreadsheet.worksheet("AT DATA")

# --- User Input ---
name = st.text_input("Enter your name:")

# --- Buttons ---
col1, col2 = st.columns(2)

def mark_attendance(status):
    if not name.strip():
        st.warning("Please enter your name!")
        return

    # Get user's approximate location (IP-based)
    g = geocoder.ip('me')
    if not g.ok:
        st.error("⚠️ Could not fetch location. Check internet or permissions.")
        return

    user_lat, user_lon = g.latlng
    dist = distance_km(user_lat, user_lon, ADMIN_LAT, ADMIN_LON)
    st.write(f"📍 Your Location: {user_lat:.5f}, {user_lon:.5f}")
    st.write(f"📏 Distance from Office: {dist*1000:.1f} meters")

    if dist <= ALLOWED_RADIUS:
        worksheet.append_row([name, str(datetime.now()), status])
        st.success(f"✅ Attendance marked {status} for {name} at {datetime.now()}")
    else:
        st.error("❌ You are outside the allowed area. Attendance not marked.")

with col1:
    if st.button("✅ IN"):
        mark_attendance("IN")

with col2:
    if st.button("❌ OUT"):
        mark_attendance("OUT")
