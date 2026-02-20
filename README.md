# SafeSpace AI

**SafeSpace AI** is an AI-powered personal mental health companion that provides therapist-style conversations, mood tracking, and emergency support. It listens, responds empathetically, and guides users through difficult emotions, offering advice, coping strategies, and support in real time.

---

## Features

- **Therapist-like Conversations**  
  Engages in empathetic, detailed, and reflective dialogue based on the user’s emotional state.

- **Mood Tracker**  
  Tracks and visualizes mood over time using a dynamic line graph, helping users monitor emotional patterns.

- **Emergency Alerts**  
  Detects crisis keywords (e.g., thoughts of self-harm) and can trigger an SOS call to a pre-configured emergency contact using Twilio.

- **Collapsible Chat History**  
  Sidebar allows users to view recent chat history without cluttering the main interface.

- **Advice & Support**  
  Provides practical guidance and step-by-step advice for coping with sadness, anxiety, or stress.

- **Interactive Frontend**  
  Built with Streamlit for a clean, intuitive, and responsive user experience.

---

## Tech Stack

- **Backend:** Python, FastAPI  
- **Frontend:** Streamlit, Plotly  
- **Messaging & Alerts:** Twilio API  
- **Environment Management:** `.env` file for secure API keys and personal numbers

---

## Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/SafeSpaceAI.git
cd SafeSpaceAI