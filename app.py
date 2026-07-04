import streamlit as st
import os
import yt_dlp
from google import genai
import requests

# Web Page ခေါင်းစဉ်နှင့် ပုံစံ သတ်မှတ်ခြင်း
st.set_page_config(page_title="Zack D. Films Myanmar AI Voicer", page_icon="🎬", layout="centered")
st.title("🎬 Zack D. Films - မြန်မာ AI အသံသွင်းစနစ်")
st.write("YouTube Short Link ကို ထည့်ရုံဖြင့် မြန်မာလို အလိုအလျောက် ပြန်ပေးပါမည်။")

# API Keys များကို Web ဘေးဘောင်တွင် ထည့်ခိုင်းခြင်း
with st.sidebar:
    st.header("⚙️ AI ဆက်တင်များ")
    gemini_key = st.text_input("Google Gemini API Key", type="password")
    eleven_key = st.text_input("ElevenLabs API Key", type="password")

# YouTube Link တောင်းသည့်နေရာ
video_url = st.text_input("Zack D. Films YouTube Short Link ကို ဤနေရာတွင် ထည့်ပါ:", placeholder="https://youtube.com/shorts/...")

if st.button("ဗီဒီယို စတင်ပြုလုပ်မည်"):
    if not gemini_key or not eleven_key:
        st.error("⚠️ ကျေးဇူးပြု၍ Sidebar တွင် API Keys များ အရင်ထည့်ပေးပါ။")
    elif not video_url:
        st.error("⚠️ YouTube Link ထည့်ပေးရန် လိုအပ်ပါသည်။")
    else:
        with st.spinner("⏳ အဆင့် (၁) - ဗီဒီယိုနှင့် စာသားများကို ဒေါင်းလုဒ်ဆွဲနေသည်..."):
            try:
                # 1. yt-dlp အသုံးပြုပြီး Video သတင်းအချက်အလက်နှင့် Transcript ဆွဲခြင်း
                ydl_opts = {'skip_download': True, 'writeinfojson': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    eng_text = info.get('description', '') or info.get('title', '')
                
                st.success("✅ မူရင်းစာသားများကို ရရှိပါပြီ။")
                st.text_area("မူရင်း အင်္ဂလိပ်စာသား:", eng_text, height=100)

                # 2. Gemini API ဖြင့် မြန်မာလို ဘာသာပြန်ခြင်း
                with st.spinner("⏳ အဆင့် (၂) - AI ဖြင့် မြန်မာလို စကားပြောဟန် ဘာသာပြန်နေသည်..."):
                    # Gemini Client Setup (2026 standard `google-genai` SDK)
                    client = genai.Client(api_key=gemini_key)
                    prompt = f"Translate the following text into natural, spoken Burmese for a voiceover. Provide ONLY the final Burmese translation text. Do not include any introductory notes, explanations, or multiple options. Output only the plain Burmese words."
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                    )
                    mm_text = response.text
                    st.success("✅ မြန်မာလို ဘာသာပြန်ပြီးပါပြီ။")
                    st.text_area("မြန်မာ ပြန်ဆိုချက်:", mm_text, height=100)

                # 3. ElevenLabs API ဖြင့် မြန်မာ AI အသံပြောင်းခြင်း
                with st.spinner("⏳ အဆင့် (၃) - AI မြန်မာအသံဖိုင် ဖန်တီးနေသည်..."):
                    tts_url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" # Rachel Voice ID (မြန်မာလို ရပါတယ်)
                    headers = {
                        "Accept": "audio/mpeg",
                        "Content-Type": "application/json",
                        "xi-api-key": eleven_key
                    }
                    data = {
                        "text": mm_text,
                        "model_id": "eleven_multilingual_v2", # မြန်မာဘာသာစကားရသော Model
                        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                    }
                    
                    audio_response = requests.post(tts_url, json=data, headers=headers)
                    
                    if audio_response.status_code == 200:
                        st.success("✅ AI မြန်မာအသံဖိုင် အောင်မြင်စွာ ထွက်လာပါပြီ။")
                        # အသံဖိုင်ကို Web ပေါ်တွင် ဖွင့်ပြခြင်း/ဒေါင်းခိုင်းခြင်း
                        st.audio(audio_response.content, format="audio/mp3")
                        st.download_button(label="🎵 မြန်မာအသံဖိုင်ကို ဒေါင်းလုဒ်ဆွဲရန်", data=audio_response.content, file_name="myanmar_voice.mp3", mime="audio/mp3")
                        
                        st.info("💡 ပြီးပြည့်စုံသော ဗီဒီယိုရရန် ဤအသံဖိုင်ကို ဒေါင်းပြီး CapCut ထဲတွင် မူရင်းဗီဒီယိုနှင့် တွဲပေးလိုက်ရုံပါပဲ။")
                    else:
                        st.error("⚠️ ElevenLabs အသံထုတ်ယူမှု မအောင်မြင်ပါ။ API Key သို့မဟုတ် Credit စစ်ဆေးပါ။")

            except Exception as e:
                st.error(f"❌ အမှားအယွင်းတစ်ခု ရှိသွားပါသည်- {str(e)}")
