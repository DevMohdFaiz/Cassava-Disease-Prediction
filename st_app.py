import torch
import io
import streamlit as st
import torchvision.transforms as transforms
from datetime import datetime
from PIL import Image
from pathlib import Path
from helper_functions import predict_disease
from ai_bot import load_system_prompt, build_context, groq_chat

st.set_page_config(page_title="CassavaVision", page_icon="cv_icon.png", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(120deg,#0f0c29,#302b63);
    }.logo{
        width:50px;
        height:45px;
        border-radius:12px;
        background: linear-gradient(135deg,#6a11cb,#2575fc);
        display:flex;align-items:center;justify-content:center;color:white;font-weight:800;
        font-family:'Poppins',sans-serif;font-size:20px; flex-shrink:0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }
    </style>
""", unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'predictions' not in st.session_state:
    st.session_state.predictions = []

disease_dict =  {
    "cbb": "Cassava Bacterial Blight",
    "cbsd": "Cassava Brown Streak Disease",
    "cgm": "Cassava Green Mite",
    "cmd": "Cassava Mosaic Disease",
    "healthy": "Healthy (No Disease)"
}



img_path = "cv_icon.png"
st.markdown(f"""<nav class="logo">CV</nav><br>""", unsafe_allow_html=True)
    
    # st.markdown(f"### Instant cassava plant disease detection\n ##### Upload a cassava leaf for disease detection")



hour = datetime.now().hour
if hour < 12:
    greeting = "Good morning 👋"
elif hour < 18:
    greeting = "Good afternoon 👋"
else:
    greeting = "Good evening 👋"

st.markdown(f"""## {greeting}""")
st.markdown("*Smart. Fast. Explainable. Try a clear photo for best results.*")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(['Image Analyzer', 'AI Assistant'])
with tab1:
    col_upload, col_status = st.columns([2, 1])

    with col_upload:
        st.markdown("### Upload an Image for Detection")
        
        uploaded_file = st.file_uploader("Choose Image", type=['png', 'jpg', 'jpeg'], help="Upload a clear photo of a cassava leaf")
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=False, width=300)
            
            if st.button("Analyze Image", type="primary", use_container_width=True):
                with st.spinner("Analyzing image..."):
                    confidence, short_pred, long_pred= predict_disease(image)               
                    
                    st.session_state.predictions.append({
                        'time': datetime.now().strftime("%H:%M:%S"),
                        'prediction': long_pred,
                        'confidence': confidence
                    })
                    
                    if short_pred=='cbb':
                        st.error(f"⚠️ **Oops, your cassava plant is infected with {long_pred}. {confidence:.2f}%**")
                        st.markdown(f"[Learn more about {long_pred}](https://en.wikipedia.org/wiki/Bacterial_blight_of_cassava)")
                    elif short_pred == 'cbsd':
                        st.error(f"⚠️ **Oops, your cassava plant is infected with {long_pred}. {confidence:.2f}%**")
                        st.markdown(f"[Learn more about {long_pred}](https://en.wikipedia.org/wiki/Cassava_brown_streak_virus_disease)")
                    elif short_pred =='cgm':
                        st.error(f"⚠️ **Oops, your cassava plant is infected with {long_pred}. {confidence:.2f}%**")
                        st.markdown(f"[Learn more about {long_pred}](https://en.wikipedia.org/wiki/Cassava_mosaic_viruses)")
                    elif short_pred == 'cmd':
                        st.error(f"⚠️ **Oops, your cassava plant is infected with {long_pred}. {confidence:.2f}%**")
                        st.markdown(f"[Learn more about {long_pred}](https://en.wikipedia.org/wiki/Cassava_mosaic_viruses)")
                    else:                    
                        st.success(f"✅ **Great news!** Your cassava plant appears to be **{long_pred} {confidence:.2f}%**")


                    

    with col_status:
        st.markdown("## 📊 Status")
        
        if uploaded_file:
            st.success("✅ Ready to analyze")
        else:
            st.info("📋 Ready to upload")
        
        st.markdown("### 🕒 Recent")
        if len(st.session_state.predictions)>0:
            for pred in st.session_state.predictions[-3:]:
                st.markdown(f"**{pred['time']}** - {pred['prediction']} ({pred['confidence']:.2f}%)")
        else:
            st.markdown("*No recent uploads*")
        
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    system_prompt = load_system_prompt('simple_prompt.md')
    # st.text()
    st.subheader("Your AI Assistant :)")
    if st.button('Clear chat'):
        st.session_state.chat_history = []
        st.rerun()
    if len(st.session_state.chat_history)>0:
        for history in st.session_state.chat_history:                
            if history['role'] == 'user':
                with st.chat_message('user'):
                        st.markdown(history['content'], unsafe_allow_html=True)
            elif history['role']=='assistant':
                with st.chat_message('assistant'):
                    st.markdown(history['content'], unsafe_allow_html=True)
    else:
        st.info('History is empty')

    user_query = st.chat_input()
    if user_query:
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_query
        })        
        # st.rerun()    
        context = build_context(user_query, system_prompt=system_prompt, 
                          predictions_history=st.session_state.predictions,
                            chat_history=st.session_state.chat_history, max_history_len=5)
        with st.spinner("Thinking...", show_time=True):
            response = groq_chat(messages=context)['response']
        if response:
            st.session_state.chat_history.append({
                'role':'assistant',  'content': response
            })

        st.rerun()


with st.sidebar:
    st.markdown("## 📖 About")
    st.markdown("""
    **CassavaVision** uses deep learning to detect diseases in cassava plants.
    
    ### How to use:
    1. Upload a clear photo of a cassava leaf
    2. Click 'Analyze Image'
    3. Get instant results
    
    ### Diseases detected:
    - Cassava Bacterial Blight (CBB)
    - Cassava Brown Streak Disease (CBSD)
    - Cassava Green Mottle (CGM)
    - Cassava Mosaic Disease (CMD)
    - Healthy plants
    
    ### Tips for best results:
    - Use good lighting
    - Clear, focused images
    - Single leaf in frame
    - No excessive shadows
    """)
    
    st.markdown("---")
    
    if st.button("Clear History"):
        st.session_state.predictions = []
        st.rerun()