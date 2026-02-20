# ================= BACKEND : main.py =================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import os
import threading
from twilio.rest import Client
from dotenv import load_dotenv   # ✅ added
load_dotenv()                    # ✅ added

app = FastAPI()

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- TWILIO ENV VARIABLES --------
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE")
MY_PHONE_NUMBER = os.getenv("MY_PHONE")

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ----- ASYNC FUNCTIONS -----
def send_sms_async(message: str, to_number=None):
    if not twilio_client or not TWILIO_PHONE_NUMBER or not (to_number or MY_PHONE_NUMBER):
        return
    number = to_number if to_number else MY_PHONE_NUMBER

    def task():
        try:
            twilio_client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=number)
        except Exception as e:
            print("SMS Error:", e)

    threading.Thread(target=task).start()


def make_call_async(to_number=None):
    if not twilio_client or not TWILIO_PHONE_NUMBER or not (to_number or MY_PHONE_NUMBER):
        return
    number = to_number if to_number else MY_PHONE_NUMBER

    def task():
        try:
            twilio_client.calls.create(
                twiml='<Response><Say voice="alice">Emergency detected. Please seek help immediately.</Say></Response>',
                from_=TWILIO_PHONE_NUMBER,
                to=number
            )
        except Exception as e:
            print("Call Error:", e)

    threading.Thread(target=task).start()

# -------- DATABASE --------
def init_db():
    conn = sqlite3.connect("safespace.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS moods(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT
        )
    """)
    conn.execute("DELETE FROM moods")
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

def get_conn():
    return sqlite3.connect("safespace.db", check_same_thread=False)

# -------- MODEL --------
class Question(BaseModel):
    question: str

def greeting():
    return "Hello 👋 I am Dr. Emily — your virtual health assistant. Tell me what health problem you are facing."

# -------- AI LOGIC --------
def medical_response(text: str):
    msg = text.lower().strip()

    if msg in ["hi","hello","hey"]:
        return greeting(),"Neutral"

    # EMERGENCY CONDITIONS
    cardiac_combo = ("chest" in msg and ("left arm" in msg or "numb" in msg or "sweating" in msg))
    breathing_combo = ("cant breathe" in msg or "can't breathe" in msg) and ("faint" in msg or "dizzy" in msg)
    self_harm = any(w in msg for w in ["suicide","kill myself","want to die"])
    severe = any(w in msg for w in ["unconscious","accident","bleeding heavily"])

    if cardiac_combo or breathing_combo or self_harm or severe:
        send_sms_async("⚠️ ALERT: Emergency detected by SafeSpace AI")
        make_call_async()
        return "⚠️ Emergency detected! Please go to the nearest hospital immediately or call someone nearby.","Critical"

    # MOOD
    if any(w in msg for w in ["sad","depressed","crying"]):
        return "Emotional stress can affect health. Rest, hydrate, and talk to someone you trust. Seek help if unsafe thoughts occur.","Low"

    # ACIDITY
    if any(w in msg for w in ["acidity","heartburn","burning chest","after spicy"]):
        return "Likely acidity. Avoid spicy food at night, don't lie down after meals, and take an antacid if needed.","Sick"

    # COMMON
    if "fever" in msg:
        return "Take paracetamol, fluids, and rest. See doctor if >3 days.","Sick"

    if "period" in msg or "cramps" in msg:
        return "Yes — mild cramps on first day of periods are normal. Use heating pad and warm fluids. Consult doctor if severe pain or vomiting.","Women Health"

    return f"Based on your symptom '{text}', rest, hydration and monitoring advised. Consult doctor if worsening.","Neutral"

# -------- CHAT --------
@app.post("/ask")
async def ask(q: Question):
    reply,mood=medical_response(q.question)

    mood_map={"Critical":1,"Low":2,"Neutral":3,"Sick":7,"Women Health":8}
    mood_val=mood_map.get(mood,3)

    conn=get_conn()
    conn.execute("INSERT INTO moods (mood) VALUES (?)",(mood_val,))
    conn.commit()
    conn.close()
    return {"reply":reply,"mood":mood_val}

@app.get("/")
def root():
    return {"status":"running"}