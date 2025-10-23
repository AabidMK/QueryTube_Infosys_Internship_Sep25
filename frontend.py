import streamlit as st
import requests
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="Video Search Engine",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 40px 0 20px 0;
        color: white;
    }
    
    .main-title {
        font-size: 56px;
        font-weight: bold;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-subtitle {
        font-size: 22px;
        opacity: 0.95;
        margin-bottom: 30px;
    }
    
    /* Search input styling */
    .stTextInput > div > div > input {
        font-size: 18px;
        padding: 15px 20px;
        border-radius: 30px;
        border: 3px solid rgba(255,255,255,0.3);
        background: rgba(255,255,255,0.95);
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #764ba2;
        box-shadow: 0 0 20px rgba(118, 75, 162, 0.5);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px 40px;
        border-radius: 30px;
        border: none;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(245, 87, 108, 0.6);
    }
    
    /* Video card styling */
    .video-card {
        background: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
        margin-bottom: 25px;
        transition: all 0.3s;
    }
    
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
    }
    
    /* Badge styling */
    .rank-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        margin-right: 10px;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    .match-score {
        display: inline-block;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        box-shadow: 0 2px 10px rgba(245, 87, 108, 0.3);
    }
    
    /* Thumbnail styling */
    .thumbnail-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Link button styling */
    .stLinkButton > a {
        background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);
    }
    
    .stLinkButton > a:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 0, 0.5);
    }
    
    /* Success message */
    .success-message {
        background: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #2ecc71;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: white;
    }
    
    .empty-state-icon {
        font-size: 80px;
        margin-bottom: 20px;
        opacity: 0.8;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "http://localhost:8000/search"

def search_videos(query: str, top_k: int = 5) -> Dict:
    """Search videos using the FastAPI backend"""
    try:
        response = requests.post(
            API_URL,
            json={"query": query, "top_k": top_k},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to the backend. Make sure the FastAPI server is running on http://localhost:8000")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def get_youtube_url(video_id: str) -> str:
    """Generate YouTube URL from video ID"""
    return f"https://www.youtube.com/watch?v={video_id}"

def get_thumbnail_url(video_id: str) -> str:
    """Generate YouTube thumbnail URL"""
    return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

def display_video_result(result: Dict):
    """Display a single video result with enhanced styling"""
    with st.container():
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display thumbnail with container
            st.markdown('<div class="thumbnail-container">', unsafe_allow_html=True)
            thumbnail_url = get_thumbnail_url(result['video_id'])
            st.image(thumbnail_url, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Badges
            st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <span class="rank-badge">#{result['rank']}</span>
                    <span class="match-score">🎯 {int(result['similarity_score'] * 100)}% Match</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Video title
            st.markdown(f"### 🎬 {result['title']}")
            
            # Channel name
            st.markdown(f"**👤 Channel:** {result['channel']}")
            
            # Transcript preview
            if result.get('transcript'):
                with st.expander("📝 View Transcript Preview"):
                    st.write(result['transcript'])
            
            # YouTube link
            youtube_url = get_youtube_url(result['video_id'])
            st.link_button("▶️ Watch on YouTube", youtube_url, use_container_width=True)
        
        st.markdown("<hr style='margin: 30px 0; border: 1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <div class="main-title">🎥 Video Search Engine</div>
            <div class="main-subtitle">Find relevant YouTube videos using AI-powered semantic search</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Search interface
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col2:
        query = st.text_input(
            "Search",
            placeholder="🔍 Search for videos... (e.g., 'machine learning tutorials', 'cooking recipes', 'travel vlogs')",
            label_visibility="collapsed"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            search_button = st.button("🚀 Search Videos", use_container_width=True, type="primary")
    
    # Sidebar for settings
    with st.sidebar:
        st.markdown("### ⚙️ Search Settings")
        top_k = st.slider("📊 Number of results", min_value=1, max_value=10, value=5)
        
        st.markdown("---")
        st.markdown("### 💡 Search Tips")
        st.info("""
        • Use descriptive keywords
        • Try different phrasings
        • Be specific about topics
        • Include context words
        """)
        
        st.markdown("---")
        st.markdown("### 🔌 Backend Status")
        try:
            response = requests.get("http://localhost:8000/", timeout=2)
            if response.status_code == 200:
                st.success("✅ Connected")
            else:
                st.warning("⚠️ Backend responding with errors")
        except:
            st.error("❌ Backend offline")
    
    # Perform search
    if search_button and query:
        with st.spinner("🔎 Searching for videos... Please wait"):
            results_data = search_videos(query, top_k)
        
        if results_data:
            results = results_data.get('results', [])
            
            if results:
                st.markdown(f"""
                    <div class="success-message">
                        ✅ Found {len(results)} relevant video{"s" if len(results) != 1 else ""}
                    </div>
                """, unsafe_allow_html=True)
                
                # Display results with enhanced styling
                for result in results:
                    st.markdown('<div class="video-card">', unsafe_allow_html=True)
                    display_video_result(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            else:
                st.markdown("""
                    <div class="empty-state">
                        <div class="empty-state-icon">😕</div>
                        <h3>No videos found</h3>
                        <p>Try different keywords or broaden your search</p>
                    </div>
                """, unsafe_allow_html=True)
    
    elif search_button and not query:
        st.warning("⚠️ Please enter a search query")
    
    # Initial state message
    if not search_button:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <h2>Start Your Video Search</h2>
                <p style='font-size: 18px; margin-top: 20px; line-height: 1.6;'>
                    Enter a query above to discover relevant YouTube videos<br>
                    Our AI-powered semantic search understands context and meaning<br>
                    to bring you the most relevant results
                </p>
            </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
