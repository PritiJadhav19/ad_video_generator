import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.title("Text-to-Ad Video Generator (MVP)")

brand = st.text_input("Brand Name", "GlowCare")
product = st.text_input("Product", "Vitamin C Face Serum")
benefits = st.text_area("Benefits (one per line)", "Brighter skin\nLightweight\nVisible glow")
audience = st.text_input("Audience", "India, 18-35")
offer = st.text_input("Offer (optional)", "Flat 30% Off")
cta = st.text_input("CTA", "Order Now")
tone = st.selectbox("Tone", ["Relatable, punchy", "Premium", "Funny", "Emotional", "GenZ"])
language = st.selectbox("Language", ["Hinglish", "Hindi", "English"])
duration = st.selectbox("Duration (seconds)", [15, 30])

if st.button("Generate Ad Video"):
    payload = {
        "brand": brand,
        "product": product,
        "benefits": [b.strip() for b in benefits.splitlines() if b.strip()],
        "audience": audience,
        "offer": offer if offer.strip() else None,
        "cta": cta,
        "tone": tone,
        "language": language,
        "duration_sec": duration
    }

    r = requests.post(API + "/generate", json=payload)

    st.write("Status:", r.status_code)
    st.write("Raw response (first 2000 chars):")
    st.code(r.text[:2000])

    if r.ok and (r.text.strip().startswith("{") or r.text.strip().startswith("[")):
        data = r.json()
        st.json(data)

        # ✅ Play video via backend URL (recommended)
        if "download_url" in data:
            st.success("Video created!")
            video_url = API + data["download_url"]
            st.video(video_url)

            # ✅ Optional: download link/button
            st.markdown(f"[Download video]({video_url})")

        else:
            st.warning("No download_url found in response. Check backend main.py return JSON.")
    else:
        st.error("Backend did not return JSON. Check the raw response above.")