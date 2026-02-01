import streamlit as st
import requests
import os
from io import BytesIO

# Page config
st.set_page_config(
    page_title="Video to MP3 Converter",
    page_icon="🎵",
    layout="centered"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    h1, h2, h3 {
        color: white !important;
    }
    label, .stMarkdown {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Get Gateway URL from environment or default to localhost
# Use localhost with port-forwarding: kubectl port-forward svc/gateway 30002:8080
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "localhost")
GATEWAY_PORT = os.getenv("GATEWAY_PORT", "30002")
GATEWAY_URL = f"http://{GATEWAY_HOST}:{GATEWAY_PORT}"

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'file_id' not in st.session_state:
    st.session_state.file_id = None

# Title and description
st.title("🎵 Video to MP3 Converter")
st.markdown("### Transform your videos into audio files effortlessly!")

# Login Section
if not st.session_state.token:
    st.markdown("## 🔐 Login")
    
    with st.form("login_form"):
        email = st.text_input("Email", placeholder="admin@test.com")
        password = st.text_input("Password", type="password", placeholder="admin123")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            try:
                response = requests.post(
                    f"{GATEWAY_URL}/login",
                    auth=(email, password),
                    timeout=10
                )
                
                if response.status_code == 200:
                    st.session_state.token = response.text
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error(f"❌ Login failed: {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Connection error: {str(e)}")
                st.info(f"💡 Make sure gateway service is running at {GATEWAY_URL}")
    
    # Helper text
    st.info("💡 Default credentials: admin@test.com / admin123")
    st.warning("""
    ⚠️ **Port Forwarding Required on macOS**
    
    Open a new terminal and run:
    ```
    kubectl port-forward svc/gateway 30002:8080
    ```
    Keep this terminal running while using the app.
    """)
    st.markdown(f"**Current Gateway URL:** `{GATEWAY_URL}`")

else:
    # Logged in view
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success("✅ You are logged in!")
    with col2:
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.file_id = None
            st.rerun()
    
    st.markdown("---")
    
    # Upload Section
    st.markdown("## 📤 Upload Video")
    
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Select a video file to convert to MP3"
    )
    
    if uploaded_file is not None:
        st.video(uploaded_file)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎵 Convert to MP3", use_container_width=True):
                with st.spinner("Uploading and converting your video..."):
                    try:
                        # Reset file pointer
                        uploaded_file.seek(0)
                        
                        files = {'file': (uploaded_file.name, uploaded_file, 'video/mp4')}
                        headers = {'Authorization': f'Bearer {st.session_state.token}'}
                        
                        response = requests.post(
                            f"{GATEWAY_URL}/upload",
                            files=files,
                            headers=headers,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Video uploaded successfully!")
                            
                            # Try to parse JSON response for file ID
                            try:
                                result = response.json()
                                if 'video_fid' in result:
                                    video_fid = result['video_fid']
                                    st.session_state.video_fid = video_fid
                                    
                                    st.info(f"""
                                    📝 **Video File ID:** `{video_fid}`
                                    
                                    Your video is being converted to MP3. Checking conversion status...
                                    """)
                                    
                                    # Poll for MP3 file ID
                                    with st.spinner("⏳ Waiting for conversion to complete (this may take 10-30 seconds)..."):
                                        import time
                                        max_attempts = 15
                                        for attempt in range(max_attempts):
                                            time.sleep(2)  # Wait 2 seconds between checks
                                            
                                            status_response = requests.get(
                                                f"{GATEWAY_URL}/status",
                                                params={'video_fid': video_fid},
                                                headers=headers,
                                                timeout=10
                                            )
                                            
                                            if status_response.status_code == 200:
                                                status_data = status_response.json()
                                                if status_data.get('status') == 'completed':
                                                    mp3_fid = status_data.get('mp3_fid')
                                                    st.session_state.mp3_fid = mp3_fid
                                                    
                                                    st.success("🎉 Conversion complete!")
                                                    st.info(f"""
                                                    **MP3 File ID:** `{mp3_fid}`
                                                    
                                                    Copy the ID below and paste it in the Download section!
                                                    """)
                                                    st.code(mp3_fid, language=None)
                                                    st.balloons()
                                                    break
                                        else:
                                            st.warning("⏰ Conversion is taking longer than expected. Try checking back in a moment and use the most recent MP3 file ID.")
                                            # Show the video ID as fallback
                                            st.code(video_fid, language=None)
                                            st.caption("Video File ID (conversion may still be in progress)")
                                else:
                                    st.info("📧 Check the converter logs for the file ID")
                            except Exception as e:
                                st.warning(f"Could not fetch MP3 file ID automatically: {str(e)}")
                                st.info("Check the Download section below - the MP3 should be ready soon")
                            
                        else:
                            st.error(f"❌ Upload failed: {response.text}")
                    
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Upload error: {str(e)}")

    
    st.markdown("---")
    
    # Download Section
    st.markdown("## 📥 Download MP3")
    
    # Use text input without form
    file_id = st.text_input(
        "File ID",
        placeholder="Enter the MP3 file ID",
        help="You'll see this ID after conversion completes",
        key="download_file_id"
    )
    
    if st.button("Fetch MP3", use_container_width=True):
        if file_id:
            st.session_state.pending_download_id = file_id
        else:
            st.error("Please enter a file ID")
    
    # Handle download outside of form/button context
    if 'pending_download_id' in st.session_state and st.session_state.pending_download_id:
        download_fid = st.session_state.pending_download_id
        
        with st.spinner("Fetching your MP3..."):
            try:
                headers = {'Authorization': f'Bearer {st.session_state.token}'}
                response = requests.get(
                    f"{GATEWAY_URL}/download",
                    params={'fid': download_fid},
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    st.success("✅ MP3 ready for download!")
                    
                    # Use download button outside form
                    st.download_button(
                        label="💾 Download MP3 File",
                        data=response.content,
                        file_name=f"{download_fid}.mp3",
                        mime="audio/mpeg",
                        use_container_width=True
                    )
                    
                    # Clear the pending download after showing button
                    if st.button("Download Another", use_container_width=True):
                        del st.session_state.pending_download_id
                        st.rerun()
                else:
                    st.error(f"❌ Download failed: {response.text}")
                    if st.button("Try Again"):
                        del st.session_state.pending_download_id
                        st.rerun()
            
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Download error: {str(e)}")
                if st.button("Try Again"):
                    del st.session_state.pending_download_id
                    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: white; opacity: 0.7;'>
    <p>🚀 Powered by Microservices Architecture</p>
    <p>Built with Streamlit | Deployed on Minikube</p>
</div>
""", unsafe_allow_html=True)
