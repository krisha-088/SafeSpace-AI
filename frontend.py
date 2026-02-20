import streamlit as st
import requests
import plotly.graph_objects as go
import time

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="SafeSpace AI - Dr. Emily", layout="wide")

# ---------------- SESSION ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🩺 Dr. Emily")

    # -------- GRAPH --------
    st.subheader("Health Mood Tracker")
    graph_box = st.empty()

    def draw_graph():
        try:
            moods = requests.get(f"{BACKEND_URL}/moods", timeout=3).json()

            if moods:
                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    y=moods,
                    mode="lines+markers",
                    line=dict(width=2),      # thin line
                    marker=dict(size=5)      # small dots
                ))

                fig.update_layout(
                    height=200,
                    margin=dict(l=5,r=5,t=5,b=5),
                    yaxis=dict(range=[0,8], showgrid=True),
                    xaxis=dict(showgrid=False),
                    showlegend=False
                )

                graph_box.plotly_chart(fig, use_container_width=True)
            else:
                graph_box.caption("Start chatting to generate health graph")

        except:
            graph_box.caption("Connecting to backend...")

    draw_graph()

    st.divider()

    # -------- EMERGENCY BUTTON --------
    if st.button("🚨 EMERGENCY CALL"):
        try:
            # Fixed: POST request to backend endpoint
            requests.post(f"{BACKEND_URL}/emergency_call", timeout=5)
            st.success("Calling your phone... 📞 Emily is on it!")
        except:
            st.error("Backend not connected")

    st.divider()

    # -------- HISTORY --------
    with st.expander("Recent History"):
        for role, msg in st.session_state.messages[-6:]:
            icon = "👤" if role=="user" else "👩‍⚕️"
            st.caption(f"{icon} {msg[:45]}")

# ---------------- MAIN CHAT ----------------
st.title("SafeSpace AI : Dr. Emily")

for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(msg)

# ---------------- INPUT ----------------
user_input = st.chat_input("Describe your symptoms...")

if user_input:
    # user message
    st.session_state.messages.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # assistant reply
    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            res = requests.post(f"{BACKEND_URL}/ask",
                                json={"question": user_input},
                                timeout=30)

            reply = res.json()["reply"]

            # typing effect
            text=""
            for word in reply.split():
                text += word+" "
                placeholder.markdown(text+"▌")
                time.sleep(0.02)

            placeholder.markdown(text)
            st.session_state.messages.append(("assistant", text))

        except:
            st.error("⚠️ Backend connection error")

    # IMPORTANT → refresh page so graph updates
    st.rerun()
