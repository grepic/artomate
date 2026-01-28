"""Streamlit UI for Artomate with real-time console logging."""

import streamlit as st
import sys
from io import StringIO
from pathlib import Path
from datetime import datetime
from PIL import Image
import time
import json
import pickle
from loguru import logger

from artomate.core.config import get_config

# Configure page
st.set_page_config(
    page_title="Artomate - Content to Commerce",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Enhanced for dark theme readability
st.markdown("""
<style>
    /* Global improvements for dark theme */
    .main {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e0e0e0;
    }
    
    /* Main header - bright and visible */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #ffffff !important;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 1rem;
    }
    
    /* Improve headings - bright colors for dark theme */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 1.5rem !important;
        margin-bottom: 1rem !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }
    
    h1 { font-size: 2.5rem !important; }
    h2 { 
        font-size: 2rem !important; 
        color: #60a5fa !important;
        border-bottom: 2px solid #60a5fa;
        padding-bottom: 0.5rem;
    }
    h3 { 
        font-size: 1.5rem !important; 
        color: #93c5fd !important;
    }
    
    /* Better text colors */
    p, span, div, label {
        color: #e0e0e0 !important;
    }
    
    /* Better spacing for sections */
    .stMarkdown {
        margin-bottom: 1rem;
    }
    
    /* Log container */
    .log-container {
        background-color: #1a1a1a;
        color: #00ff00;
        padding: 1.5rem;
        border-radius: 0.75rem;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        max-height: 500px;
        overflow-y: auto;
        border: 2px solid #60a5fa;
    }
    
    /* Success box - bright green */
    .success-box {
        background-color: #065f46;
        border: 2px solid #10b981;
        color: #d1fae5;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1.5rem 0;
        font-size: 1.05rem;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    /* Error box - bright red */
    .error-box {
        background-color: #7f1d1d;
        border: 2px solid #ef4444;
        color: #fecaca;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1.5rem 0;
        font-size: 1.05rem;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
    }
    
    /* Better button styling */
    .stButton button {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.5rem !important;
        transition: all 0.3s ease !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(96, 165, 250, 0.4) !important;
        border-color: #60a5fa !important;
    }
    
    /* Better input fields - visible borders */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        font-size: 1.05rem !important;
        padding: 0.75rem !important;
        border-radius: 0.5rem !important;
        background-color: #1f2937 !important;
        border: 2px solid #374151 !important;
        color: #e0e0e0 !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.2) !important;
    }
    
    /* Better metrics - white text */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        color: #93c5fd !important;
    }
    
    /* Better info/warning/error boxes - proper colors */
    .stAlert {
        padding: 1.25rem !important;
        font-size: 1.05rem !important;
        border-radius: 0.75rem !important;
        margin: 1rem 0 !important;
    }
    
    /* Info boxes - blue */
    div[data-baseweb="notification"] {
        background-color: #1e3a8a !important;
        border-left: 4px solid #60a5fa !important;
        color: #dbeafe !important;
    }
    
    /* Success boxes - green */
    div[data-baseweb="notification"].success {
        background-color: #065f46 !important;
        border-left: 4px solid #10b981 !important;
        color: #d1fae5 !important;
    }
    
    /* Warning boxes - yellow */
    div[data-baseweb="notification"].warning {
        background-color: #78350f !important;
        border-left: 4px solid #fbbf24 !important;
        color: #fef3c7 !important;
    }
    
    /* Error boxes - red */
    div[data-baseweb="notification"].error {
        background-color: #7f1d1d !important;
        border-left: 4px solid #ef4444 !important;
        color: #fecaca !important;
    }
    
    /* Better sidebar */
    [data-testid="stSidebar"] {
        background-color: #111827 !important;
        padding: 1.5rem 1rem;
        border-right: 1px solid #374151;
    }
    
    [data-testid="stSidebar"] h2 {
        color: #ffffff !important;
        font-size: 1.5rem !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1.05rem !important;
        padding: 0.5rem !important;
        color: #e0e0e0 !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #1f2937 !important;
        border-radius: 0.5rem;
    }
    
    /* Better expander - visible text */
    .streamlit-expanderHeader {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        color: #ffffff !important;
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 0.5rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #374151 !important;
        border-color: #60a5fa !important;
    }
    
    /* Better checkbox/radio - white text */
    .stCheckbox label, .stRadio label {
        font-size: 1.05rem !important;
        line-height: 1.5 !important;
        color: #e0e0e0 !important;
    }
    
    /* Progress bars - bright blue */
    .stProgress > div > div {
        height: 1.5rem !important;
        border-radius: 0.75rem !important;
        background-color: #60a5fa !important;
    }
    
    .stProgress > div {
        background-color: #1f2937 !important;
        border-radius: 0.75rem !important;
    }
    
    /* Pipeline stage indicators - bright and clear */
    .stButton[data-testid*="stage_"] button {
        justify-content: flex-start !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        background-color: #1f2937 !important;
        border: 2px solid #374151 !important;
    }
    
    .stButton[data-testid*="stage_"] button:hover {
        background-color: #374151 !important;
        border-color: #60a5fa !important;
    }
    
    /* Multiselect - better visibility */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #60a5fa !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        padding: 0.5rem 0.75rem !important;
        margin: 0.25rem !important;
    }
    
    /* Better selectbox dropdown */
    [data-baseweb="select"] {
        background-color: #1f2937 !important;
    }
    
    [data-baseweb="popover"] {
        background-color: #1f2937 !important;
        border: 1px solid #374151 !important;
    }
    
    /* Disable fullscreen image expansion */
    button[title="View fullscreen"] {
        display: none !important;
    }
    
    .stImage button {
        display: none !important;
    }
    
    /* Better code blocks */
    code {
        font-size: 1rem !important;
        padding: 0.25rem 0.5rem !important;
        background-color: #1f2937 !important;
        border-radius: 0.25rem !important;
        color: #93c5fd !important;
        border: 1px solid #374151 !important;
    }
    
    /* Better dividers */
    hr {
        margin: 2rem 0 !important;
        border-color: #374151 !important;
        border-width: 2px !important;
    }
    
    /* Better captions */
    .caption, small {
        color: #9ca3af !important;
        font-size: 0.95rem !important;
    }
</style>
""", unsafe_allow_html=True)


# Helper function to display images with A/B test modes
def display_image_safe(image_source, caption=None, width=None, mode=None):
    """Display image with A/B test support for fullscreen behavior.
    
    Args:
        image_source: Can be a file path (str/Path), PIL Image, or bytes
        caption: Optional caption text
        width: Optional width in pixels
        mode: 'native' (st.image with fullscreen) or 'safe' (HTML without fullscreen)
              If None, uses session state setting
    """
    import base64
    from pathlib import Path
    from PIL import Image
    import io
    
    # Get mode from session state if not specified
    if mode is None:
        mode = st.session_state.get('image_display_mode', 'safe')
    
    # MODE A: Native st.image (can fullscreen)
    if mode == 'native':
        try:
            if isinstance(image_source, (str, Path)):
                img = Image.open(image_source)
            elif isinstance(image_source, Image.Image):
                img = image_source
            elif isinstance(image_source, bytes):
                img = Image.open(io.BytesIO(image_source))
            else:
                st.error(f"Nepodporovaný typ obrázku: {type(image_source)}")
                return False
            
            if width:
                st.image(img, caption=caption, width=width)
            else:
                st.image(img, caption=caption, use_container_width=True)
            return True
        except Exception as e:
            st.error(f"Nepodařilo se načíst obrázek: {e}")
            return False
    
    # MODE B: Safe HTML (no fullscreen)
    else:
        try:
            # Convert to bytes based on input type
            if isinstance(image_source, (str, Path)):
                # File path
                with open(image_source, "rb") as img_file:
                    img_bytes = img_file.read()
                # Determine image format from extension
                ext = Path(image_source).suffix.lower()
                mime_type = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }.get(ext, 'image/png')
            elif isinstance(image_source, Image.Image):
                # PIL Image
                img_byte_arr = io.BytesIO()
                image_source.save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                mime_type = 'image/png'
            elif isinstance(image_source, bytes):
                # Already bytes
                img_bytes = image_source
                mime_type = 'image/png'
            else:
                st.error(f"Nepodporovaný typ obrázku: {type(image_source)}")
                return False
            
            # Convert to base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Create HTML using background-image instead of img tag to prevent fullscreen
            width_style = f"width: {width}px;" if width else "width: 100%; max-width: 800px;"
            caption_html = f'<p style="text-align: center; color: #888; font-size: 0.9em; margin-top: 0.5em;">{caption}</p>' if caption else ''
            
            # Get image dimensions if possible
            if isinstance(image_source, Image.Image):
                aspect_ratio = image_source.height / image_source.width
            else:
                aspect_ratio = 1  # Default square
            
            html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; margin: 1em 0;">
                <div style="{width_style} padding-bottom: {aspect_ratio * 100}%; background-image: url('data:{mime_type};base64,{img_base64}'); background-size: contain; background-repeat: no-repeat; background-position: center; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: relative;">
                </div>
                {caption_html}
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)
            return True
        except Exception as e:
            st.error(f"Nepodařilo se načíst obrázek: {e}")
            return False


class StreamlitLogger:
    """Capture logs for Streamlit display."""

    def __init__(self):
        self.logs = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        return log_entry


# Session persistence functions
SESSION_FILE = Path("data/.ui_session.pkl")

def save_session():
    """Save current session state to file."""
    try:
        SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Save serializable session data
        session_data = {
            'job_id': st.session_state.get('job_id'),
            'assets': st.session_state.get('assets', []),
            'products': st.session_state.get('products', []),
            'current_page': st.session_state.get('current_page', '🎨 Create Job'),
            'generated_prompts': st.session_state.get('generated_prompts', []),
            'auto_generate_prompts': st.session_state.get('auto_generate_prompts', False),
            # Save form values
            'animals_per_image': st.session_state.get('animals_per_image', 2),
            # Logger logs
            'logger_logs': st.session_state.logger.logs if hasattr(st.session_state, 'logger') else []
        }
        
        with open(SESSION_FILE, 'wb') as f:
            pickle.dump(session_data, f)
    except Exception as e:
        print(f"Failed to save session: {e}")

def load_session():
    """Load session state from file."""
    if SESSION_FILE.exists():
        try:
            with open(SESSION_FILE, 'rb') as f:
                session_data = pickle.load(f)
            
            # Restore session state
            st.session_state.job_id = session_data.get('job_id')
            st.session_state.assets = session_data.get('assets', [])
            st.session_state.products = session_data.get('products', [])
            st.session_state.current_page = session_data.get('current_page', '🎨 Create Job')
            st.session_state.generated_prompts = session_data.get('generated_prompts', [])
            st.session_state.auto_generate_prompts = session_data.get('auto_generate_prompts', False)
            st.session_state.animals_per_image = session_data.get('animals_per_image', 2)
            
            # Restore logger logs
            if 'logger_logs' in session_data and hasattr(st.session_state, 'logger'):
                st.session_state.logger.logs = session_data['logger_logs']
                
            return True
        except Exception as e:
            print(f"Failed to load session: {e}")
            return False
    return False

def clear_saved_session():
    """Clear saved session file."""
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()

# Initialize session state
if 'session_loaded' not in st.session_state:
    st.session_state.session_loaded = False
    
if not st.session_state.session_loaded:
    # Try to load saved session first
    load_session()
    st.session_state.session_loaded = True

if 'logger' not in st.session_state:
    st.session_state.logger = StreamlitLogger()
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'assets' not in st.session_state:
    st.session_state.assets = []
if 'products' not in st.session_state:
    st.session_state.products = []


def display_console():
    """Display console log."""
    st.markdown("### 📟 Console Log")
    log_text = "\n".join(st.session_state.logger.logs[-50:])  # Last 50 logs
    st.markdown(f'<div class="log-container">{log_text}</div>', unsafe_allow_html=True)


def create_job_ui():
    """Job creation UI."""
    st.markdown("## 🎨 Create New Job")

    # Constants from n8n workflow
    ANIMALS = [
        "Ant", "Antelope", "Arctic Fox", "Bat", "Bear", "Beaver", "Bee",
        "Beetle", "Betta Fish", "Boar", "Buffalo", "Butterfly", "Camel",
        "Canary", "Cat", "Chameleon", "Cheetah", "Chicken", "Coral Fish",
        "Cow", "Crab", "Crocodile", "Crow", "Deer", "Dog", "Dolphin",
        "Donkey", "Dove", "Dragon", "Dragonfly", "Duck", "Eagle", "Elephant",
        "Fairy", "Flamingo", "Fox", "Frog", "Gazelle", "Giraffe", "Goat",
        "Goldfish", "Gorilla", "Griffin", "Guinea Pig", "Hamster", "Hawk",
        "Hedgehog", "Hippo", "Horse", "Hummingbird", "Hyena", "Iguana",
        "Jellyfish", "Kangaroo", "Koala", "Ladybug", "Lemur", "Leopard",
        "Lion", "Lizard", "Lynx", "Meerkat", "Mermaid", "Monkey", "Moose",
        "Moth", "Octopus", "Orca", "Otter", "Owl", "Panda", "Parrot",
        "Peacock", "Pegasus", "Pelican", "Penguin", "Phoenix", "Pig",
        "Polar Bear", "Puma", "Rabbit", "Raccoon", "Reindeer", "Rhino",
        "Rooster", "Sea Turtle", "Seahorse", "Seal", "Shark", "Sheep",
        "Skunk", "Snake", "Spider", "Spirit Animal", "Squirrel", "Starfish",
        "Stingray", "Swan", "Tiger", "Turtle", "Unicorn", "Walrus", "Whale",
        "Wolf", "Zebra"
    ]

    STYLES = [
        "Realistic", "Watercolor", "Line Art", "Pop Art", "Abstract", "Boho",
        "Cute", "Anime", "Fantasy", "Minimalist", "Geometric", "Japandi",
        "Vintage", "Cyberpunk", "Neon", "Vaporwave", "Art Deco", "Cartoon",
        "Low Poly", "3D Render", "Ink Painting", "Pencil Sketch",
        "Pastel Illustrative", "Botanical", "Retro", "Modern Poster"
    ]

    THEMES = [
        "Christmas", "Valentine", "Halloween", "Easter", "Spring Blossom",
        "Summer Beach", "Fall Harvest", "Winter Snow", "Independence Day",
        "Memorial Day", "Pride Month", "St. Patrick's Day", "Lunar New Year",
        "Thanksgiving", "Horror Spooky", "Forest", "Ocean", "Space", "Desert",
        "Mountain", "Rainy Mood", "Snowy Night", "Aurora", "Japanese Spring",
        "Autumn Leaves", "Baby Nursery", "Wedding", "Cottagecore",
        "Coastal Aesthetic"
    ]

    # Initialize widget keys directly (not separate variables!)
    if 'animals_select' not in st.session_state:
        st.session_state.animals_select = ["Cat", "Dog"]
    if 'styles_select' not in st.session_state:
        st.session_state.styles_select = ["Minimalist", "Japandi"]
    if 'themes_select' not in st.session_state:
        st.session_state.themes_select = ["Christmas", "Winter Snow"]
    if 'animals_per_image' not in st.session_state:
        st.session_state.animals_per_image = 1

    # Description at the top
    description = st.text_area(
        "📝 Description", 
        placeholder="e.g., cute animals in nature, fantasy creatures, modern pets...",
        help="Brief description of what the images should be about"
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🐾 Animals")
        col_animal1, col_animal2 = st.columns([3, 1])
        with col_animal2:
            if st.button("🎲", key="random_animals", help="Random animals"):
                import random
                count = random.randint(3, 7)
                st.session_state.animals_select = random.sample(ANIMALS, count)
        with col_animal1:
            animals = st.multiselect(
                "Select animals",
                ANIMALS,
                help="Choose one or more animals",
                key="animals_select"
            )
        
        st.markdown("### 🎨 Styles")
        col_style1, col_style2 = st.columns([3, 1])
        with col_style2:
            if st.button("🎲", key="random_styles", help="Random styles"):
                import random
                count = random.randint(2, 5)
                st.session_state.styles_select = random.sample(STYLES, count)
        with col_style1:
            styles = st.multiselect(
                "Select styles",
                STYLES,
                help="Choose one or more styles",
                key="styles_select"
            )

        
    with col2:
        st.markdown("### 🌄 Themes")
        col_theme1, col_theme2 = st.columns([3, 1])
        with col_theme2:
            if st.button("🎲", key="random_themes", help="Random themes"):
                import random
                count = random.randint(2, 5)
                st.session_state.themes_select = random.sample(THEMES, count)
        with col_theme1:
            themes = st.multiselect(
                "Select themes",
                THEMES,
                help="Choose one or more themes",
                key="themes_select"
            )

        st.markdown("### ⚙️ Settings")
        st.info("💡 Always generates 12 images (one for each calendar month)")
        
        col_setting1, col_setting2 = st.columns([3, 1])
        with col_setting2:
            if st.button("🎲", key="random_animals_per_image", help="Random count"):
                import random
                st.session_state.animals_per_image = random.randint(1, 5)
        with col_setting1:
            animals_per_image = st.slider(
                "Animals per image", 
                1, 5,
                key="animals_per_image"
            )

    # Summary
    if animals and styles and themes:
        st.markdown("---")
        st.markdown("### 📋 Summary")
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        with col_sum1:
            st.write(f"**Animals:** {', '.join(animals[:2])}{'...' if len(animals) > 2 else ''}")
        with col_sum2:
            st.write(f"**Styles:** {', '.join(styles[:2])}{'...' if len(styles) > 2 else ''}")
        with col_sum3:
            st.write(f"**Themes:** {', '.join(themes[:2])}{'...' if len(themes) > 2 else ''}")
        with col_sum4:
            st.write(f"**Per image:** {st.session_state.animals_per_image} animals")
            st.write(f"**Total:** 12 images")

    create_btn = st.button("🚀 Create Job", type="primary", use_container_width=True)

    if create_btn and animals and styles and themes:
        with st.status("🚀 Vytváření jobu...", expanded=True) as status:
            try:
                st.write("📝 Příprava parametrů...")
                from artomate.core.job_manager import JobManager

                # Create combined theme from selections
                theme = f"{', '.join(animals)} in {', '.join(themes)} style"
                style = ', '.join(styles)
                
                st.write(f"✓ Zvířata: {', '.join(animals[:3])}{'...' if len(animals) > 3 else ''}")
                st.write(f"✓ Styly: {', '.join(styles[:3])}{'...' if len(styles) > 3 else ''}")
                st.write(f"✓ Témata: {', '.join(themes[:3])}{'...' if len(themes) > 3 else ''}")
                
                st.session_state.logger.log(f"Creating job with {len(animals)} animals, {len(styles)} styles, {len(themes)} themes", "INFO")

                st.write("\n🔧 Vytváření jobu v databázi...")
                manager = JobManager()
                keywords_list = animals + styles + themes
                if description:
                    keywords_list.append(description)

                job = manager.create_job(
                    theme=theme,
                    style=style,
                    niche="multi-product",  # Will be determined in product creation
                    keywords=keywords_list,
                    priority=5
                )
                st.write(f"✓ Job #{job.id} vytvořen")

                st.session_state.job_id = job.id
                st.session_state.logger.log(f"✓ Job {job.id} created successfully", "SUCCESS")
                
                st.write("\n⚙️ Nastavování automatického generování...")
                # Set flag to auto-generate prompts
                st.session_state.auto_generate_prompts = True
                st.write("✓ Auto-generování aktivováno")
                
                # Save session
                st.write("\n💾 Ukládání session...")
                save_session()
                st.write("✓ Session uložena")
                
                status.update(label=f"✅ Job #{job.id} úspěšně vytvořen!", state="complete")
                
                # Auto-redirect to Generate Variants page
                st.session_state.current_page = "🖼️ Generate Variants"
                save_session()  # Save after page change
                st.rerun()

            except Exception as e:
                status.update(label="❌ Chyba při vytváření jobu", state="error")
                st.session_state.logger.log(f"✗ Job creation failed: {e}", "ERROR")
                st.markdown(f'<div class="error-box">✗ Error: {e}</div>',
                           unsafe_allow_html=True)


def generate_variants_ui():
    """Generate AI prompts for 12 calendar months."""
    st.markdown("## 🎨 Generate Monthly Prompts")

    if not st.session_state.job_id:
        st.warning("⚠️ Create a job first!")
        return

    # Initialize prompts in session state
    if 'generated_prompts' not in st.session_state:
        st.session_state.generated_prompts = []
    
    # Auto-generate prompts if flag is set
    if 'auto_generate_prompts' not in st.session_state:
        st.session_state.auto_generate_prompts = False

    try:
        from artomate.core.job_manager import JobManager
        manager = JobManager()
        job = manager.get_job(st.session_state.job_id)
        
        st.info(f"**Job ID:** {st.session_state.job_id}")
        
        # Display job details
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Theme:**", job.theme)
            st.write("**Style:**", job.style)
        with col2:
            st.write("**Selected Animals:**")
            animals = [k for k in job.keywords if not any(x in k.lower() for x in ['style', 'minimal', 'boho', 'winter', 'christmas'])][:10]
            st.write(", ".join(animals) if animals else "All keywords")
        
        st.markdown("---")
        
        # Show existing prompts if any
        if st.session_state.generated_prompts:
            st.success(f"✅ {len(st.session_state.generated_prompts)} prompts generated!")
            
            with st.expander("📝 View Generated Prompts", expanded=False):
                for idx, prompt_data in enumerate(st.session_state.generated_prompts):
                    st.markdown(f"### {idx+1}. {prompt_data['month']} - {prompt_data.get('season', '')}")
                    
                    # Highlight animals in the prompt
                    prompt_text = prompt_data['prompt']
                    animals = [k for k in job.keywords if not any(x in k.lower() for x in ['style', 'minimal', 'boho', 'winter', 'christmas'])][:10]
                    
                    st.markdown(f"**🐾 Animals featured:** {', '.join([a for a in animals if a.lower() in prompt_text.lower()])}")
                    
                    st.text_area(
                        f"Prompt {idx+1}",
                        prompt_text,
                        height=100,
                        key=f"prompt_display_{idx}",
                        label_visibility="collapsed"
                    )
            
            # Button to proceed to image generation
            if st.button("➡️ Next: Generate Images", type="primary", use_container_width=True):
                st.session_state.current_page = "👀 View Assets"
                save_session()  # Save after page change
                st.info("➡️ Proceeding to image generation...")
                time.sleep(1)
                st.rerun()
        else:
            st.info("💡 Generate 12 unique prompts (one for each month) considering:\n- Seasonal animal behavior\n- Geographic habitat conditions\n- Monthly weather and environment")
        
        generate_btn = st.button(
            "🚀 Generate 12 Monthly Prompts" if not st.session_state.generated_prompts else "🔄 Regenerate Prompts",
            type="primary" if not st.session_state.generated_prompts else "secondary",
            use_container_width=True
        )

        # Auto-generate if flag is set (after job creation)
        should_generate = generate_btn or (st.session_state.auto_generate_prompts and not st.session_state.generated_prompts)
        
        if should_generate:
            # Reset the auto-generate flag
            st.session_state.auto_generate_prompts = False
            
            # Progress tracking with st.status
            with st.status("🤖 Generování AI promptů...", expanded=True) as status:
                st.write("📋 Příprava kontextu...")
                st.session_state.logger.log("Starting AI prompt generation for 12 months", "INFO")
                
                # Prepare context for AI
                animals_str = ', '.join(job.keywords[:10])  # First 10 are animals
                styles_str = job.style
                st.write(f"✓ Zvířata: {animals_str[:50]}...")
                st.write(f"✓ Styl: {styles_str}")
                
                # Call OpenAI to generate prompts
                try:
                    st.write("🔌 Připojování k OpenAI API...")
                    from openai import OpenAI
                    
                    config = get_config()
                    client = OpenAI(api_key=config.openai_api_key)
                    st.write("✓ Připojeno k OpenAI")
                    
                    prompt_instruction = f"""Generate 12 calendar image prompts in JSON format.

Context:
- Animals: {animals_str}
- Styles: {styles_str}
- Theme: {job.theme}

CRITICAL RULE: Use the SAME EXACT animals with SAME EXACT appearance in ALL 12 months!

STEP 1: First, define the specific animals (example format):
- If "Cat" is selected → choose ONE specific cat: "a fluffy orange tabby cat with green eyes"
- If "Dog" is selected → choose ONE specific dog: "a golden retriever with a red collar"
Keep these EXACT descriptions for all 12 months!

STEP 2: Create 12 unique prompts (one for each month: January to December).
Each prompt should:
1. Feature the SAME animals with SAME appearance doing behaviors typical for that month
2. Include geographic/habitat details relevant to the season
3. Reflect weather and environmental conditions of that month
4. Be detailed (100+ words describing the scene)
5. NEVER change animal colors, breeds, or physical features between months

Example: If January has "a fluffy orange tabby cat", then ALL 12 months must have "a fluffy orange tabby cat" (not black cat, not white cat, not calico cat - always orange tabby).

Return ONLY a JSON array (no markdown, no explanations):
[
  {{"prompt": "detailed 100+ word image prompt for January", "month": "January", "season": "Winter"}},
  {{"prompt": "detailed 100+ word image prompt for February", "month": "February", "season": "Winter"}},
  ...12 total
]

CRITICAL: Start response with [ and end with ]"""

                    st.write("🚀 Generování 12 unikátních promptů...")
                    st.session_state.logger.log("Calling OpenAI API...", "INFO")
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an expert at creating detailed, seasonal image prompts for calendar illustrations."},
                            {"role": "user", "content": prompt_instruction}
                        ],
                        temperature=0.8
                    )
                    st.write("✓ Odpověď od AI přijata")
                    
                    # Parse response
                    st.write("📝 Parsování a validace promptů...")
                    raw_content = response.choices[0].message.content.strip()
                    
                    # Clean markdown if present
                    if raw_content.startswith("```"):
                        raw_content = raw_content.split("```")[1]
                        if raw_content.startswith("json"):
                            raw_content = raw_content[4:]
                        raw_content = raw_content.strip()
                    
                    import json
                    prompts = json.loads(raw_content)
                    st.write(f"✓ Validováno {len(prompts)} promptů")
                    
                    st.write("💾 Ukládání do session...")
                    st.session_state.generated_prompts = prompts
                    st.session_state.logger.log(f"✓ Generated {len(prompts)} monthly prompts", "SUCCESS")
                    
                    # Save session after generating prompts
                    save_session()
                    st.write("✓ Session uložena")
                    
                    status.update(label="✅ Prompty úspěšně vygenerovány!", state="complete")
                    st.success(f"✅ Vygenerováno {len(prompts)} unikátních měsíčních promptů!")
                    st.rerun()
                    
                except Exception as e:
                    status.update(label="❌ Chyba při generování", state="error")
                    st.session_state.logger.log(f"✗ AI generation failed: {e}", "ERROR")
                    st.error(f"❌ Error: {e}")

    except Exception as e:
        st.error(f"❌ Error loading job: {e}")


def generate_mock_images(status=None):
    """Generate 12 mock placeholder images for testing.
    
    Args:
        status: Optional st.status object for progress tracking
    """
    from PIL import Image, ImageDraw, ImageFont
    import random
    from pathlib import Path
    
    config = get_config()
    mock_dir = config.assets_dir / "images" / "mock"
    mock_dir.mkdir(parents=True, exist_ok=True)
    
    if status:
        st.write("✓ Složka připravena")
    
    st.session_state.logger.log("Generating 12 mock images...", "INFO")
    
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    
    colors = [
        (52, 152, 219),   # Blue
        (231, 76, 60),    # Red
        (46, 204, 113),   # Green
        (241, 196, 15),   # Yellow
        (155, 89, 182),   # Purple
        (230, 126, 34),   # Orange
        (26, 188, 156),   # Turquoise
        (149, 165, 166),  # Gray
        (192, 57, 43),    # Dark Red
        (39, 174, 96),    # Dark Green
        (142, 68, 173),   # Dark Purple
        (211, 84, 0)      # Dark Orange
    ]
    
    mock_assets = []
    
    if status:
        st.write(f"\n📊 Celkem obrázků k vytvoření: {len(months)}")
        progress_bar = st.progress(0)
    
    try:
        from artomate.core.job_manager import JobManager
        from artomate.db.models import Asset, AssetType
        
        manager = JobManager()
        job = manager.get_job(st.session_state.job_id)
        
        for idx, month in enumerate(months):
            if status:
                st.write(f"  ⏳ {month} ({idx+1}/{len(months)})")
            
            # Create image
            img = Image.new('RGB', (1024, 1024), color=colors[idx])
            draw = ImageDraw.Draw(img)
            
            # Draw text
            try:
                # Try to use a decent font
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
            except:
                # Fallback to default
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw month name
            text = month
            bbox = draw.textbbox((0, 0), text, font=font_large)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (1024 - text_width) // 2
            y = 400
            
            # Draw text with shadow
            draw.text((x+3, y+3), text, fill=(0, 0, 0), font=font_large)
            draw.text((x, y), text, fill=(255, 255, 255), font=font_large)
            
            # Draw prompt info if available
            if st.session_state.generated_prompts and idx < len(st.session_state.generated_prompts):
                prompt_preview = st.session_state.generated_prompts[idx]['prompt'][:60] + "..."
                y2 = 550
                draw.text((100, y2), prompt_preview, fill=(255, 255, 255), font=font_small)
            
            # Save image
            filename = f"mock_{month.lower()}_{idx+1}.png"
            filepath = mock_dir / filename
            img.save(filepath)
            
            # Create asset record using SQLAlchemy
            asset = Asset(
                job_id=job.id,
                asset_type=AssetType.HERO,
                storage_path=str(filepath),
                file_size_bytes=filepath.stat().st_size,
                width=1024,
                height=1024,
                format="PNG",
                generator="mock",
                prompt=st.session_state.generated_prompts[idx]['prompt'] if st.session_state.generated_prompts and idx < len(st.session_state.generated_prompts) else f"Mock image for {month}",
                generation_params={
                    "month": month,
                    "mock": True,
                    "prompt_index": idx,
                    "color": list(colors[idx])
                },
                compliance_checked=False
            )
            
            # Save to database
            with manager.db.session_scope() as session:
                session.add(asset)
                session.flush()
                # Access id to load it before session closes
                asset_id = asset.id
                mock_assets.append(asset_id)
            
            if status:
                st.write(f"  ✓ {month} vytvořen")
                progress_bar.progress((idx + 1) / len(months))
            
            st.session_state.logger.log(f"✓ Generated mock image for {month}", "SUCCESS")
        
        # Store asset IDs in session
        if status:
            st.write("\n💾 Ukládání do session...")
        st.session_state.assets = mock_assets
        st.session_state.logger.log(f"✓ Generated {len(mock_assets)} mock images", "SUCCESS")
        
        # Save session
        save_session()
        if status:
            st.write("✓ Session uložena")
        
        if status:
            status.update(label=f"✅ Vytvořeno {len(mock_assets)} mock obrázků!", state="complete")
        
        return True
        
    except Exception as e:
        if status:
            status.update(label="❌ Chyba při generování mock obrázků", state="error")
        st.session_state.logger.log(f"✗ Mock image generation failed: {e}", "ERROR")
        import traceback
        st.error(f"Error: {e}")
        st.code(traceback.format_exc())
        return False


def display_assets_ui():
    """Display generated assets."""
    st.markdown("## 🖼️ Generated Assets")

    if not st.session_state.job_id:
        st.warning("⚠️ Create a job first!")
        return
    
    # Check if we have prompts but no assets - offer to generate mock images
    if st.session_state.generated_prompts and not st.session_state.assets:
        st.info("📸 Ready to generate images!")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎨 Generate Mock Images (Testing)", type="primary", use_container_width=True):
                with st.status("🎨 Generování mock obrázků...", expanded=True) as status:
                    st.write("📁 Příprava složky pro obrázky...")
                    if generate_mock_images(status):
                        st.success("✅ Mock images generated!")
                        time.sleep(1)
                        st.rerun()
        
        with col2:
            if st.button("🤖 Generate Real Images (OpenAI)", type="secondary", use_container_width=True, disabled=True):
                st.warning("🚧 Real image generation coming soon!")
        
        return

    if not st.session_state.assets:
        st.info("💡 No assets generated yet. Generate variants first, then come back here to generate images!")
        return

    # Load assets from database
    from artomate.core.job_manager import JobManager
    manager = JobManager()
    
    # Get asset data from IDs - convert to dict to avoid detached instance issues
    asset_data_list = []
    with manager.db.session_scope() as session:
        from artomate.db.models import Asset
        asset_objects = session.query(Asset).filter(
            Asset.id.in_(st.session_state.assets[:12])
        ).all()
        
        # Extract all needed data while in session
        for asset in asset_objects:
            asset_data_list.append({
                'id': asset.id,
                'storage_path': asset.storage_path,
                'width': asset.width,
                'height': asset.height
            })
    
    st.info("💡 **Tip:** Klikněte na obrázek pro zvětšení. Pro zavření klikněte mimo obrázek nebo stiskněte ESC.")
    
    cols = st.columns(4)

    for idx, asset_data in enumerate(asset_data_list):  # Show first 12
        with cols[idx % 4]:
            try:
                # Přidáme expander pro lepší ovládání
                with st.expander(f"🖼️ Variant {idx+1}", expanded=False):
                    display_image_safe(asset_data['storage_path'])
                    st.caption(f"📐 Rozměry: {asset_data['width']}x{asset_data['height']} px")
            except Exception as e:
                st.error(f"Failed to load asset: {str(e)}")
    
    # Add action buttons
    st.markdown("---")
    st.markdown("### ✅ Assets Generated Successfully!")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("➡️ Continue to Create Products", type="primary", use_container_width=True):
            st.session_state.current_page = "📦 Create Products"
            save_session()
            st.rerun()


def create_products_ui():
    """Create Printify products UI."""
    st.markdown("## 🏭 Create Products")

    if not st.session_state.assets:
        st.warning("⚠️ Generate assets first!")
        return

    # Import product catalog
    from artomate.workers.printify_product_catalog import PRODUCT_CATEGORIES, PRINTIFY_PRODUCTS

    # Initialize selected products in session state
    if 'selected_products' not in st.session_state:
        st.session_state.selected_products = set()
    
    # Initialize custom design uploader
    if 'custom_design_path' not in st.session_state:
        st.session_state.custom_design_path = None
    
    # === CUSTOM DESIGN UPLOADER ===
    st.markdown("### 🎨 Nahrajte vlastní design nebo logo")
    st.info("💡 Nahrajte vlastní obrázek a uvidíte ho na všech produktech v reálném čase - stejně jako v Printify!")
    
    col_upload, col_clear = st.columns([4, 1])
    with col_upload:
        uploaded_file = st.file_uploader(
            "Vyberte obrázek (PNG, JPG)",
            type=['png', 'jpg', 'jpeg'],
            key='design_uploader',
            help="Nahrajte své logo, vzor nebo design, který chcete použít na produkty"
        )
    
    with col_clear:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗑️ Smazat", use_container_width=True, disabled=st.session_state.custom_design_path is None):
            st.session_state.custom_design_path = None
            st.rerun()
    
    # Save uploaded file
    if uploaded_file is not None:
        config = get_config()
        uploads_dir = config.assets_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        upload_path = uploads_dir / uploaded_file.name
        with open(upload_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.session_state.custom_design_path = str(upload_path)
        st.success(f"✅ Design nahrán: {uploaded_file.name}")
        
        # Show preview
        col_preview1, col_preview2, col_preview3 = st.columns([1, 2, 1])
        with col_preview2:
            display_image_safe(upload_path, caption="Váš design")
    
    elif st.session_state.custom_design_path:
        # Show existing custom design
        st.info(f"📌 Aktuální design: {Path(st.session_state.custom_design_path).name}")
        col_preview1, col_preview2, col_preview3 = st.columns([1, 2, 1])
        with col_preview2:
            try:
                display_image_safe(st.session_state.custom_design_path, caption="Váš design")
            except:
                st.warning("⚠️ Design nebyl nalezen")
                st.session_state.custom_design_path = None
    else:
        # Show asset selector if we have generated assets
        if st.session_state.assets and len(st.session_state.assets) > 1:
            st.markdown("**Nebo vyberte z vygenerovaných obrázků:**")
            st.info("💡 Klikněte na tlačítko pod obrázkem pro výběr designu")
            
            # Get asset data
            from artomate.core.job_manager import JobManager
            manager = JobManager()
            asset_previews = []
            
            with manager.db.session_scope() as session:
                from artomate.db.models import Asset
                for asset_id in st.session_state.assets[:12]:  # Max 12
                    asset = session.query(Asset).filter(Asset.id == asset_id).first()
                    if asset:
                        asset_previews.append({
                            'id': asset.id,
                            'path': asset.storage_path
                        })
            
            # Asset selector with thumbnails
            cols = st.columns(min(6, len(asset_previews)))
            for idx, asset_data in enumerate(asset_previews):
                with cols[idx % 6]:
                    try:
                        # Show thumbnail without fullscreen capability
                        display_image_safe(asset_data['path'])
                        # Create clickable button below
                        if st.button(f"✅ Vybrat #{idx+1}", key=f"asset_select_{idx}", use_container_width=True, help="Klikněte pro výběr tohoto designu"):
                            st.session_state.custom_design_path = asset_data['path']
                            st.rerun()
                    except:
                        pass
    
    st.markdown("---")
    
    st.markdown("### 📦 Vyberte produkty")
    st.info("💡 Vyberte produkty, které chcete vytvořit. Náhledy ukazují, jak bude váš design vypadat na každém produktu.")

    # Helper function to composite design on mockup
    def composite_design_on_mockup(mockup_path, design_image_path, product_spec):
        """Composite a design image onto a product mockup with proper cropping and placement."""
        from PIL import Image
        import io
        from artomate.workers.render_engine import RenderEngine
        
        try:
            # Load mockup
            mockup = Image.open(mockup_path).convert('RGBA')
            mockup_w, mockup_h = mockup.size
            
            # Get print area from product spec
            print_area = product_spec['print_area']
            coverage = product_spec['coverage_type']
            product_name = product_spec.get('name', '').lower()
            
            # Initialize render engine for proper cropping
            renderer = RenderEngine()
            
            # Define mockup-specific positioning and sizing
            # Based on actual Printify mockup dimensions and print areas
            mockup_configs = {
                # Apparel - designs go on chest area, typically 30-35% from top
                'tshirt': {'scale': 0.20, 'pos_x': 0.5, 'pos_y': 0.40},
                'hoodie': {'scale': 0.18, 'pos_x': 0.5, 'pos_y': 0.42},
                'sweatshirt': {'scale': 0.19, 'pos_x': 0.5, 'pos_y': 0.41},
                'tank': {'scale': 0.18, 'pos_x': 0.5, 'pos_y': 0.38},
                'long_sleeve': {'scale': 0.19, 'pos_x': 0.5, 'pos_y': 0.40},
                
                # Wall art - designs should fill the visible frame area
                'poster': {'scale': 0.65, 'pos_x': 0.5, 'pos_y': 0.5},
                'canvas': {'scale': 0.60, 'pos_x': 0.5, 'pos_y': 0.5},
                'framed': {'scale': 0.55, 'pos_x': 0.5, 'pos_y': 0.5},
                
                # Drinkware - designs wrap around, show on front
                'mug': {'scale': 0.22, 'pos_x': 0.42, 'pos_y': 0.45},
                'tumbler': {'scale': 0.20, 'pos_x': 0.45, 'pos_y': 0.48},
                'bottle': {'scale': 0.18, 'pos_x': 0.48, 'pos_y': 0.50},
                
                # Home decor - centered designs
                'pillow': {'scale': 0.50, 'pos_x': 0.5, 'pos_y': 0.5},
                'blanket': {'scale': 0.45, 'pos_x': 0.5, 'pos_y': 0.5},
                'towel': {'scale': 0.35, 'pos_x': 0.5, 'pos_y': 0.48},
                'curtain': {'scale': 0.40, 'pos_x': 0.5, 'pos_y': 0.5},
                'rug': {'scale': 0.50, 'pos_x': 0.5, 'pos_y': 0.5},
                'doormat': {'scale': 0.55, 'pos_x': 0.5, 'pos_y': 0.5},
                'duvet': {'scale': 0.40, 'pos_x': 0.5, 'pos_y': 0.48},
                
                # Accessories
                'phone': {'scale': 0.35, 'pos_x': 0.5, 'pos_y': 0.45},
                'tote': {'scale': 0.30, 'pos_x': 0.5, 'pos_y': 0.45},
                'bag': {'scale': 0.30, 'pos_x': 0.5, 'pos_y': 0.45},
                'sticker': {'scale': 0.70, 'pos_x': 0.5, 'pos_y': 0.5},
                'notebook': {'scale': 0.45, 'pos_x': 0.5, 'pos_y': 0.5},
            }
            
            # Find matching config
            config = None
            for key, cfg in mockup_configs.items():
                if key in product_name:
                    config = cfg
                    break
            
            # Default config if no match
            if not config:
                config = {'scale': 0.25, 'pos_x': 0.5, 'pos_y': 0.45}
            
            # Calculate target dimensions based on mockup size and config
            # Use aspect ratio from print area
            print_ratio = print_area['width'] / print_area['height']
            
            # Target size based on mockup dimensions
            target_width = int(mockup_w * config['scale'])
            target_height = int(target_width / print_ratio)
            
            # Ensure design fits within mockup
            if target_height > mockup_h * 0.7:
                target_height = int(mockup_h * 0.7)
                target_width = int(target_height * print_ratio)
            
            # Render design at correct dimensions with smart cropping
            design = renderer.render_image(
                source_path=design_image_path,
                target_width=target_width,
                target_height=target_height,
                mode='cover',  # Fill entire area with smart cropping
                transparent_background=(coverage == 'transparent')
            )
            
            design_w, design_h = design.size
            
            # Position based on config
            x = int(mockup_w * config['pos_x']) - (design_w // 2)
            y = int(mockup_h * config['pos_y']) - (design_h // 2)
            
            # Ensure design is within bounds
            x = max(0, min(x, mockup_w - design_w))
            y = max(0, min(y, mockup_h - design_h))
            
            # Composite design onto mockup
            if design.mode == 'RGBA':
                mockup.paste(design, (x, y), design)
            else:
                mockup.paste(design, (x, y))
            
            # Convert to bytes for base64 encoding
            buffer = io.BytesIO()
            mockup.convert('RGB').save(buffer, format='PNG', optimize=True, quality=85)
            return buffer.getvalue()
            
        except Exception as e:
            from loguru import logger
            logger.error(f"Failed to composite design on mockup: {e}")
            return None
    
    # Product preview function
    def render_product_preview(product_id, product_spec, design_image_path=None):
        """Render visual product preview with real Printify mockup images and optional design."""
        import base64
        from pathlib import Path
        
        coverage = product_spec['coverage_type']
        
        # Use real Printify mockup images from data/mockups/
        mockup_dir = Path(__file__).parent.parent / "data" / "mockups"
        
        # Map product_id to mockup filename
        # Extract base product type (e.g., "tshirt_unisex" from "tshirt_unisex_001")
        product_base = product_id.rsplit('_', 1)[0] if '_' in product_id and product_id.split('_')[-1].isdigit() else product_id
        
        mockup_path = mockup_dir / f"{product_base}.png"
        
        # If exact match not found, try fallback mapping
        if not mockup_path.exists():
            fallback_mapping = {
                "tshirt": "tshirt_unisex",
                "hoodie": "hoodie_unisex",
                "sweatshirt": "sweatshirt",
                "poster": "poster_18x24",
                "canvas": "canvas_16x20",
                "mug": "mug_11oz",
                "pillow": "throw_pillow_16x16",
                "blanket": "blanket_medium",
                "bag": "tote_bag",
                "phone": "phone_case_iphone",
                "sticker": "sticker_4x4",
                "notebook": "notebook_spiral",
            }
            
            for key, value in fallback_mapping.items():
                if key in product_id.lower():
                    mockup_path = mockup_dir / f"{value}.png"
                    break
        
        # Generate preview HTML
        if mockup_path.exists():
            # Use real mockup image - with design composited if provided
            try:
                if design_image_path and Path(design_image_path).exists():
                    # Composite design onto mockup
                    img_bytes = composite_design_on_mockup(mockup_path, design_image_path, product_spec)
                    if img_bytes:
                        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                        img_src = f"data:image/png;base64,{img_base64}"
                    else:
                        # Fallback to plain mockup
                        with open(mockup_path, "rb") as img_file:
                            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                            img_src = f"data:image/png;base64,{img_base64}"
                else:
                    # No design provided, show plain mockup (this is the key fix!)
                    with open(mockup_path, "rb") as img_file:
                        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
                        img_src = f"data:image/png;base64,{img_base64}"
            except Exception as e:
                from loguru import logger
                logger.error(f"Failed to load mockup {mockup_path}: {e}")
                # Fallback to placeholder if image can't be read
                img_src = ""
        else:
            # Mockup file doesn't exist - use SVG fallback
            img_src = ""
        
        if img_src:
            preview_html = f"""
            <div style="display: flex; flex-direction: column; align-items: center; margin: 0.5rem 0;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                    <img src="{img_src}" style="display: block; max-width: 280px; max-height: 280px; object-fit: contain;"/>
                </div>
                <div style="margin-top: 0.3rem; font-size: 0.7rem; color: #7f8c8d;">{"Průhledný design" if coverage == "transparent" else "Celoplošný tisk"}</div>
            </div>
            """
            return preview_html
        
        # SVG fallback for products without mockups
        if "tshirt" in product_id:
            svg = """<svg width="120" height="140" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
                <path d="M30,40 L20,50 L20,140 L100,140 L100,50 L90,40" fill="#ecf0f1" stroke="#95a5a6" stroke-width="2"/>
                <rect x="30" y="40" width="60" height="100" fill="#ecf0f1"/>
                <path d="M20,50 L10,60 L10,80 L20,75" fill="#ecf0f1" stroke="#95a5a6" stroke-width="2"/>
                <path d="M100,50 L110,60 L110,80 L100,75" fill="#ecf0f1" stroke="#95a5a6" stroke-width="2"/>
                <ellipse cx="60" cy="35" rx="10" ry="8" fill="#bdc3c7"/>
                <rect x="45" y="60" width="30" height="36" fill="#e74c3c" opacity="0.8" rx="2"/>
                <text x="60" y="82" font-size="20" text-anchor="middle" fill="white">🎨</text>
            </svg>"""
        elif "hoodie" in product_id:
            svg = """<svg width="120" height="140" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
                <path d="M30,40 L20,50 L20,140 L100,140 L100,50 L90,40" fill="#34495e" stroke="#2c3e50" stroke-width="2"/>
                <rect x="30" y="40" width="60" height="100" fill="#34495e"/>
                <path d="M35,35 Q60,10 85,35" fill="#34495e" stroke="#2c3e50" stroke-width="2"/>
                <rect x="40" y="90" width="40" height="25" fill="#2c3e50" rx="3"/>
                <rect x="45" y="55" width="30" height="36" fill="#e74c3c" opacity="0.8" rx="2"/>
                <text x="60" y="77" font-size="20" text-anchor="middle" fill="white">🎨</text>
            </svg>"""
        elif "poster" in product_id or "canvas" in product_id:
            svg = """<svg width="100" height="140" viewBox="0 0 100 140" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#f39c12;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#e67e22;stop-opacity:1" />
                </linearGradient></defs>
                <rect x="5" y="5" width="90" height="130" fill="#2c3e50" stroke="#1a252f" stroke-width="3"/>
                <rect x="10" y="10" width="80" height="120" fill="url(#grad1)"/>
                <text x="50" y="75" font-size="24" text-anchor="middle" fill="white">🖼️</text>
            </svg>"""
        elif "framed" in product_id:
            svg = """<svg width="100" height="130" viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3498db;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#2980b9;stop-opacity:1" />
                </linearGradient></defs>
                <rect x="0" y="0" width="100" height="130" fill="#8B4513" stroke="#654321" stroke-width="2"/>
                <rect x="10" y="10" width="80" height="110" fill="#DAA520"/>
                <rect x="15" y="15" width="70" height="100" fill="url(#grad2)"/>
                <text x="50" y="70" font-size="20" text-anchor="middle" fill="white">🖼️</text>
            </svg>"""
        elif "mug" in product_id:
            svg = """<svg width="100" height="120" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="50" cy="30" rx="25" ry="8" fill="#e0e0e0"/>
                <rect x="25" y="30" width="50" height="60" fill="#ffffff" stroke="#bdc3c7" stroke-width="2"/>
                <ellipse cx="50" cy="90" rx="25" ry="8" fill="#d0d0d0"/>
                <path d="M75,40 Q90,55 75,70" fill="none" stroke="#bdc3c7" stroke-width="6"/>
                <rect x="30" y="45" width="40" height="30" fill="#e67e22" opacity="0.9" rx="2"/>
                <text x="50" y="65" font-size="18" text-anchor="middle" fill="white">☕</text>
            </svg>"""
        elif "bottle" in product_id or "tumbler" in product_id:
            svg = """<svg width="80" height="140" viewBox="0 0 80 140" xmlns="http://www.w3.org/2000/svg">
                <rect x="25" y="20" width="30" height="100" fill="#95a5a6" rx="15"/>
                <ellipse cx="40" cy="20" rx="15" ry="5" fill="#7f8c8d"/>
                <ellipse cx="40" cy="120" rx="15" ry="5" fill="#7f8c8d"/>
                <rect x="32" y="10" width="16" height="15" fill="#34495e" rx="3"/>
                <rect x="28" y="50" width="24" height="40" fill="#3498db" opacity="0.8" rx="2"/>
                <text x="40" y="75" font-size="16" text-anchor="middle" fill="white">💧</text>
            </svg>"""
        elif "pillow" in product_id:
            svg = """<svg width="130" height="110" viewBox="0 0 130 110" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="grad3" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#9b59b6;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#8e44ad;stop-opacity:1" />
                </linearGradient></defs>
                <ellipse cx="65" cy="55" rx="60" ry="50" fill="url(#grad3)"/>
                <line x1="10" y1="55" x2="120" y2="55" stroke="#7d3c98" stroke-width="2" stroke-dasharray="5,5"/>
                <text x="65" y="65" font-size="28" text-anchor="middle" fill="white">🛋️</text>
            </svg>"""
        elif "blanket" in product_id:
            svg = """<svg width="120" height="140" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="grad4" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#e74c3c;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#c0392b;stop-opacity:1" />
                </linearGradient></defs>
                <rect x="10" y="30" width="100" height="80" fill="url(#grad4)" rx="5"/>
                <line x1="10" y1="60" x2="110" y2="60" stroke="#a93226" stroke-width="2"/>
                <line x1="10" y1="80" x2="110" y2="80" stroke="#a93226" stroke-width="2"/>
                <text x="60" y="75" font-size="32" text-anchor="middle" fill="white">🛏️</text>
            </svg>"""
        elif "towel" in product_id:
            svg = """<svg width="90" height="130" viewBox="0 0 90 130" xmlns="http://www.w3.org/2000/svg">
                <rect x="15" y="10" width="60" height="110" fill="#16a085" rx="3"/>
                <line x1="15" y1="30" x2="75" y2="30" stroke="#138d75" stroke-width="1"/>
                <line x1="15" y1="50" x2="75" y2="50" stroke="#138d75" stroke-width="1"/>
                <line x1="15" y1="70" x2="75" y2="70" stroke="#138d75" stroke-width="1"/>
                <line x1="15" y1="90" x2="75" y2="90" stroke="#138d75" stroke-width="1"/>
                <line x1="15" y1="110" x2="75" y2="110" stroke="#138d75" stroke-width="1"/>
                <text x="45" y="70" font-size="24" text-anchor="middle" fill="white">🧺</text>
            </svg>"""
        elif "bag" in product_id or "tote" in product_id:
            svg = """<svg width="110" height="130" viewBox="0 0 110 130" xmlns="http://www.w3.org/2000/svg">
                <path d="M20,40 L10,120 L100,120 L90,40 Z" fill="#ecf0f1" stroke="#95a5a6" stroke-width="2"/>
                <path d="M30,40 Q30,15 40,15 Q50,15 50,40" fill="none" stroke="#7f8c8d" stroke-width="4"/>
                <path d="M60,40 Q60,15 70,15 Q80,15 80,40" fill="none" stroke="#7f8c8d" stroke-width="4"/>
                <rect x="35" y="60" width="40" height="40" fill="#16a085" opacity="0.9" rx="2"/>
                <text x="55" y="85" font-size="24" text-anchor="middle" fill="white">🎒</text>
            </svg>"""
        elif "case" in product_id or "phone" in product_id:
            svg = """<svg width="70" height="130" viewBox="0 0 70 130" xmlns="http://www.w3.org/2000/svg">
                <rect x="10" y="5" width="50" height="120" fill="#2c3e50" rx="8"/>
                <rect x="15" y="15" width="40" height="100" fill="#34495e" rx="4"/>
                <rect x="18" y="30" width="34" height="68" fill="#e74c3c" opacity="0.9" rx="2"/>
                <text x="35" y="70" font-size="20" text-anchor="middle" fill="white">📱</text>
                <circle cx="35" cy="20" r="3" fill="#95a5a6"/>
            </svg>"""
        elif "sticker" in product_id:
            svg = """<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="grad5" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#f39c12;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#e67e22;stop-opacity:1" />
                </linearGradient></defs>
                <circle cx="50" cy="50" r="40" fill="url(#grad5)"/>
                <path d="M85,15 L90,10 L95,15 Z" fill="#ecf0f1" opacity="0.8"/>
                <text x="50" y="60" font-size="28" text-anchor="middle" fill="white">✨</text>
            </svg>"""
        elif "notebook" in product_id:
            svg = """<svg width="90" height="120" viewBox="0 0 90 120" xmlns="http://www.w3.org/2000/svg">
                <rect x="10" y="10" width="70" height="100" fill="#e74c3c" rx="3"/>
                <rect x="15" y="15" width="60" height="90" fill="#c0392b" rx="2"/>
                <line x1="10" y1="20" x2="10" y2="100" stroke="#95a5a6" stroke-width="3"/>
                <circle cx="10" cy="30" r="2" fill="#7f8c8d"/>
                <circle cx="10" cy="45" r="2" fill="#7f8c8d"/>
                <circle cx="10" cy="60" r="2" fill="#7f8c8d"/>
                <circle cx="10" cy="75" r="2" fill="#7f8c8d"/>
                <circle cx="10" cy="90" r="2" fill="#7f8c8d"/>
                <text x="45" y="65" font-size="24" text-anchor="middle" fill="white">📓</text>
            </svg>"""
        elif "mousepad" in product_id:
            svg = """<svg width="130" height="100" viewBox="0 0 130 100" xmlns="http://www.w3.org/2000/svg">
                <defs><linearGradient id="grad6" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3498db;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#2980b9;stop-opacity:1" />
                </linearGradient></defs>
                <rect x="10" y="20" width="110" height="70" fill="url(#grad6)" rx="8"/>
                <text x="65" y="60" font-size="28" text-anchor="middle" fill="white">🖱️</text>
            </svg>"""
        else:
            svg = """<svg width="100" height="120" viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
                <rect x="10" y="10" width="80" height="100" fill="#95a5a6" rx="5"/>
                <text x="50" y="70" font-size="32" text-anchor="middle" fill="white">📦</text>
            </svg>"""
        
        # Convert SVG to base64 data URI
        svg_bytes = svg.encode('utf-8')
        svg_base64 = base64.b64encode(svg_bytes).decode('utf-8')
        
        # Label
        label = "Průhledný design" if coverage == "transparent" else "Celoplošný tisk"
        
        # Render as img with data URI
        preview_html = f"""
        <div style="display: flex; flex-direction: column; align-items: center; margin: 0.5rem 0;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 0.5rem; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                <img src="data:image/svg+xml;base64,{svg_base64}" style="display: block;"/>
            </div>
            <div style="margin-top: 0.3rem; font-size: 0.7rem; color: #7f8c8d;">{label}</div>
        </div>
        """
        
        return preview_html

    # Categories with emojis
    categories = {
        "apparel": {"name": "👕 Oblečení", "icon": "👕", "desc": "Trička, mikiny, topy"},
        "home_living": {"name": "🏠 Domov", "icon": "🏠", "desc": "Polštáře, deky, ručníky"},
        "wall_art": {"name": "🖼️ Nástěnné umění", "icon": "🖼️", "desc": "Plakáty, plátna, rámy"},
        "drinkware": {"name": "☕ Nádobí", "icon": "☕", "desc": "Hrnky, termosky, láhve"},
        "accessories": {"name": "🎒 Doplňky", "icon": "🎒", "desc": "Tašky, samolepky, notebooky"}
    }
    
    # Show info about current design being displayed
    if st.session_state.custom_design_path:
        st.success(f"👁️ Náhledy zobrazují váš vlastní design: **{Path(st.session_state.custom_design_path).name}**")
    elif st.session_state.assets:
        st.info("👁️ Náhledy zobrazují první vygenerovaný obrázek. Nahrajte vlastní design výše pro náhled s vaším logem.")
    else:
        st.info("👁️ Náhledy zobrazují placeholder ikony. Nahrajte design pro realistické náhledy.")

    # Quick select buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("✅ Vybrat vše", use_container_width=True):
            st.session_state.selected_products = set(PRINTIFY_PRODUCTS.keys())
            st.rerun()
    with col2:
        if st.button("❌ Zrušit vše", use_container_width=True):
            st.session_state.selected_products = set()
            st.rerun()
    with col3:
        if st.button("⭐ Bestsellery", use_container_width=True):
            bestsellers = ["tshirt_unisex", "poster_18x24", "mug_11oz", "throw_pillow_16x16", "tote_bag", "hoodie_unisex"]
            st.session_state.selected_products = set(bestsellers)
            st.rerun()
    with col4:
        st.metric("Vybrané produkty", len(st.session_state.selected_products))

    st.markdown("---")

    # Display products by category
    for cat_id, cat_info in categories.items():
        if cat_id not in PRODUCT_CATEGORIES:
            continue
            
        products = PRODUCT_CATEGORIES[cat_id]
        
        with st.expander(f"{cat_info['icon']} **{cat_info['name']}** - {cat_info['desc']} ({len(products)} produktů)", expanded=True):
            # Select all in category
            col_select, col_info = st.columns([1, 5])
            with col_select:
                category_selected = all(p in st.session_state.selected_products for p in products)
                if st.checkbox(f"Vybrat celou kategorii", key=f"cat_{cat_id}", value=category_selected):
                    st.session_state.selected_products.update(products)
                else:
                    st.session_state.selected_products.difference_update(products)
            
            # Product grid
            cols = st.columns(3)
            for idx, product_id in enumerate(products):
                if product_id not in PRINTIFY_PRODUCTS:
                    continue
                    
                product_spec = PRINTIFY_PRODUCTS[product_id]
                
                with cols[idx % 3]:
                    # Product card
                    is_selected = product_id in st.session_state.selected_products
                    
                    # Card styling
                    card_style = "background-color: #1e3a5f; padding: 1rem; border-radius: 0.5rem; border: 2px solid #4CAF50;" if is_selected else "background-color: #262730; padding: 1rem; border-radius: 0.5rem; border: 2px solid transparent;"
                    
                    st.markdown(f'<div style="{card_style}">', unsafe_allow_html=True)
                    
                    # Product preview - show with custom design if uploaded, otherwise first generated design
                    design_path = st.session_state.custom_design_path
                    
                    # If no custom design, use first generated asset
                    if not design_path and st.session_state.assets:
                        # Get first asset storage path
                        from artomate.core.job_manager import JobManager
                        manager = JobManager()
                        try:
                            with manager.db.session_scope() as session:
                                from artomate.db.models import Asset
                                first_asset = session.query(Asset).filter(
                                    Asset.id == st.session_state.assets[0]
                                ).first()
                                if first_asset:
                                    design_path = first_asset.storage_path
                        except:
                            pass
                    
                    preview_html = render_product_preview(product_id, product_spec, design_path)
                    st.markdown(preview_html, unsafe_allow_html=True)
                    
                    # Product name with checkbox
                    if st.checkbox(
                        f"**{product_spec['name']}**",
                        key=f"prod_{product_id}",
                        value=is_selected
                    ):
                        st.session_state.selected_products.add(product_id)
                    else:
                        st.session_state.selected_products.discard(product_id)
                    
                    # Product details
                    st.caption(f"📐 {product_spec['print_area']['width']}×{product_spec['print_area']['height']} px")
                    
                    # Coverage badge
                    coverage = product_spec['coverage_type']
                    if coverage == "transparent":
                        st.markdown("🔍 **Průhledné pozadí**")
                    elif coverage == "full":
                        st.markdown("🎨 **Celoplošný tisk**")
                    else:
                        st.markdown("📍 **Centrovaný design**")
                    
                    # Notes
                    if product_spec.get('notes'):
                        st.caption(f"💡 {product_spec['notes']}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")  # Spacing

    st.markdown("---")

    # Summary and create button
    if st.session_state.selected_products:
        st.markdown("### 📊 Souhrn")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vybrané produkty", len(st.session_state.selected_products))
        with col2:
            st.metric("Celkem assetů", len(st.session_state.assets))
        with col3:
            total_products = len(st.session_state.selected_products) * len(st.session_state.assets)
            st.metric("Celkem produktů k vytvoření", total_products)

        create_products_btn = st.button("🏭 Vytvořit všechny vybrané produkty", type="primary", use_container_width=True)
    else:
        st.warning("⚠️ Vyberte alespoň jeden produkt!")
        create_products_btn = False

    if create_products_btn and st.session_state.selected_products:
        # Progress tracking
        with st.status("📦 Vytváření produktů...", expanded=True) as status:
            from artomate.core.job_manager import JobManager
            from artomate.workers.printify_worker import PrintifyWorker

            manager = JobManager()
            job = manager.get_job(st.session_state.job_id)

            st.write(f"📋 Připraveno {len(st.session_state.assets)} assets")
            st.write(f"🎯 Vybrané produkty: {len(st.session_state.selected_products)}")
            st.session_state.logger.log(f"Creating products for {len(st.session_state.assets)} assets", "INFO")

            printify = PrintifyWorker()
            all_products = []

            # Convert selected products set to list
            product_types = list(st.session_state.selected_products)
            total = len(st.session_state.assets) * len(product_types)
            st.write(f"📊 Celkem produktů k vytvoření: {total}")
            
            # Progress bar
            progress_bar = st.progress(0)
            current = 0

            try:
                for asset_idx, asset in enumerate(st.session_state.assets, 1):
                    st.write(f"\n🖼️ Asset {asset_idx}/{len(st.session_state.assets)}")
                    for product_type in product_types:
                        current += 1
                        progress = current / total
                        progress_bar.progress(progress)
                        st.write(f"  ⏳ Vytvářím {product_type}... ({current}/{total})")

                        st.session_state.logger.log(f"Creating {product_type} for asset {asset.id}", "INFO")

                        product = printify.create_product(job, asset, product_type)
                        all_products.append(product)
                        st.write(f"  ✓ {product_type} vytvořen (#{product.id})")

                        st.session_state.logger.log(f"✓ Created {product_type} #{product.id}", "SUCCESS")

                st.write(f"\n💾 Ukládání {len(all_products)} produktů...")
                st.session_state.products = all_products
                st.session_state.logger.log(f"✓ Created {len(all_products)} total products", "SUCCESS")
                
                # Save session after creating products
                save_session()
                st.write("✓ Session uložena")

                progress_bar.progress(1.0)
                status.update(label=f"✅ Vytvořeno {len(all_products)} produktů!", state="complete")
                st.success(f"✓ Vytvořeno {len(all_products)} produktů!")

            except Exception as e:
                status.update(label="❌ Chyba při vytváření produktů", state="error")
                st.session_state.logger.log(f"✗ Product creation failed: {e}", "ERROR")
                st.error(f"✗ Error: {e}")


def publish_social_ui():
    """Publish to social media UI."""
    st.markdown("## 📱 Social Media Publishing")

    if not st.session_state.assets:
        st.warning("⚠️ Generate assets first!")
        return

    # All available platforms
    all_platforms = ["Instagram Carousel", "Instagram Reels", "TikTok", "YouTube Shorts"]
    
    st.markdown("### 📋 Vyberte platformy pro publikování")
    st.info("💡 Zaškrtněte platformy, na které chcete publikovat.")
    
    # Display platform info
    platform_info = {
        "Instagram Carousel": "📸 Až 10 obrázků v jednom příspěvku",
        "Instagram Reels": "🎬 Krátká videa (5-15s)",
        "TikTok": "🎵 Virální krátká videa",
        "YouTube Shorts": "▶️ Krátké vertikální videá"
    }
    
    # Initialize selected platforms in session state
    if 'selected_social_platforms' not in st.session_state:
        st.session_state.selected_social_platforms = all_platforms.copy()
    
    # Display checkboxes for each platform in 2 columns
    platforms = []
    cols = st.columns(2)
    for idx, platform in enumerate(all_platforms):
        with cols[idx % 2]:
            is_selected = st.checkbox(
                f"**{platform}**",
                value=platform in st.session_state.selected_social_platforms,
                key=f"social_{platform}"
            )
            if is_selected:
                platforms.append(platform)
            st.caption(platform_info[platform])
    
    # Update session state
    st.session_state.selected_social_platforms = platforms
    
    st.markdown("---")
    
    if not platforms:
        st.warning("⚠️ Vyberte alespoň jednu platformu!")
        return

    publish_btn = st.button("📱 Publish to Social", type="primary")

    if publish_btn and platforms:
        # Progress tracking for social media
        with st.status("📱 Publikování na sociální sítě...", expanded=True) as status:
            try:
                from artomate.core.job_manager import JobManager
                from artomate.workers.social_media_publisher import SocialMediaPublisher
                from artomate.workers.video_generator import VideoGenerator
                from artomate.db.models import SocialPlatform

                st.write("🔌 Inicializace...")
                manager = JobManager()
                job = manager.get_job(st.session_state.job_id)

                social = SocialMediaPublisher()
                video_gen = VideoGenerator()
                st.write("✓ Připojeno k publikačním službám")

                posts = []
                total_steps = len(platforms)
                progress_bar = st.progress(0)
                current_step = 0

                # Instagram Carousel with all 12 images
                if "Instagram Carousel" in platforms:
                    st.write("\n📸 Instagram Carousel")
                    st.write("  ⏳ Připravuji carousel s obrázky...")
                    st.session_state.logger.log("Creating Instagram carousel post", "INFO")

                    post = social.create_post(
                        job=job,
                        platform=SocialPlatform.INSTAGRAM,
                        image_assets=st.session_state.assets[:10]  # IG limit 10
                    )
                    posts.append(post)
                    st.write(f"  ✓ Carousel vytvořen ({len(st.session_state.assets[:10])} obrázků)")

                    st.session_state.logger.log("✓ Instagram carousel created", "SUCCESS")
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)

                # Create Reels/Shorts for each variant
                if any(p in platforms for p in ["Instagram Reels", "TikTok", "YouTube Shorts"]):
                    st.write("\n🎬 Vytváření videí")
                    st.session_state.logger.log("Creating videos for social media", "INFO")

                    for idx, asset in enumerate(st.session_state.assets[:3], 1):  # First 3 for demo
                        st.write(f"  ⏳ Video {idx}/3...")
                        video = video_gen.create_reel(
                            job=job,
                            assets=[asset],
                            duration=5,
                            style="ken_burns"
                        )

                        if "Instagram Reels" in platforms:
                            post = social.create_post(job, SocialPlatform.INSTAGRAM, video_asset=video)
                            posts.append(post)
                            st.write(f"  ✓ Video {idx} vytvořeno a připraveno")

                        st.session_state.logger.log(f"✓ Created video {idx}", "SUCCESS")
                    
                    current_step += 1
                    progress_bar.progress(current_step / total_steps)

                progress_bar.progress(1.0)
                st.write(f"\n✨ Celkem vytvořeno: {len(posts)} příspěvků")
                st.session_state.logger.log(f"✓ Created {len(posts)} social posts", "SUCCESS")
                status.update(label=f"✅ Vytvořeno {len(posts)} příspěvků!", state="complete")
                st.success(f"✓ Vytvořeno {len(posts)} příspěvků pro sociální sítě!")

            except Exception as e:
                status.update(label="❌ Chyba při publikování", state="error")
                st.session_state.logger.log(f"✗ Social publishing failed: {e}", "ERROR")
                st.error(f"✗ Error: {e}")


def submit_stock_ui():
    """Submit to stock platforms UI."""
    st.markdown("## 📸 Stock Platform Submission")

    if not st.session_state.assets:
        st.warning("⚠️ Generate assets first!")
        return

    # All available platforms
    all_platforms = [
        "Shutterstock", "Adobe Stock", "Getty Images", "iStock", "Depositphotos",
        "Unsplash", "Pexels", "Pixabay",
        "500px", "Dreamstime", "Alamy", "Pond5",
        "Etsy Digital", "Creative Market", "Creative Fabrica",
        "Redbubble", "Society6", "EyeEm"
    ]
    
    st.markdown("### 📋 Vyberte platformy pro prodej")
    st.info("💡 Zaškrtněte platformy, kam chcete nahrát a prodávat vaše obrázky.")
    
    # Display platform info
    platform_info = {
        # Premium Stock
        "Shutterstock": "🖼️ Největší stock platforma - až $120 per download",
        "Adobe Stock": "🎨 Integrace s Adobe CC - royalty 33%",
        "Getty Images": "🏆 Premium stock - nejvyšší ceny",
        "iStock": "💰 Getty Images budget verze - dostupné ceny",
        "Depositphotos": "🌍 Mezinárodní stock - dobrá provize",
        
        # Free Stock (pro viditelnost)
        "Unsplash": "🆓 Free stock - obrovská viditelnost, donations",
        "Pexels": "🆓 Free stock - sponzorství a exposure",
        "Pixabay": "🆓 Free stock - donations od uživatelů",
        
        # Specialized Stock
        "500px": "📷 Pro fotografy - licensing až 60%",
        "Dreamstime": "🌟 Micro-stock - až 50% royalty",
        "Alamy": "🔍 Vysoké provize - až 50%",
        "Pond5": "🎬 Video & audio marketplace - 50% royalty",
        
        # Digital Marketplaces
        "Etsy Digital": "🛍️ Digitální produkty - široké publikum",
        "Creative Market": "🎨 Grafické assety - 70% provize",
        "Creative Fabrica": "✨ Design & crafts - subscription model",
        
        # Print-on-Demand
        "Redbubble": "🖨️ Print-on-demand art - pasivní příjem",
        "Society6": "🎭 Art marketplace - vyšší provize než Redbubble",
        "EyeEm": "📱 Mobilní fotografie - AI powered sales"
    }
    
    # Initialize selected platforms in session state
    if 'selected_stock_platforms' not in st.session_state:
        # Default: only premium platforms selected
        st.session_state.selected_stock_platforms = [
            "Shutterstock", "Adobe Stock", "Getty Images", "iStock", "Depositphotos"
        ]
    
    # Display checkboxes for each platform in 3 columns
    platforms = []
    cols = st.columns(3)
    for idx, platform in enumerate(all_platforms):
        with cols[idx % 3]:
            is_selected = st.checkbox(
                f"**{platform}**",
                value=platform in st.session_state.selected_stock_platforms,
                key=f"stock_{platform}"
            )
            if is_selected:
                platforms.append(platform)
            st.caption(platform_info[platform])
    
    # Update session state
    st.session_state.selected_stock_platforms = platforms
    
    st.markdown("---")
    
    if not platforms:
        st.warning("⚠️ Vyberte alespoň jednu platformu!")
        return

    submit_btn = st.button("📸 Submit to Stock", type="primary")

    if submit_btn and platforms:
        # Progress tracking for stock submissions
        with st.status("📸 Příprava submission pro stock platformy...", expanded=True) as status:
            try:
                from artomate.core.job_manager import JobManager
                from artomate.workers.stock_platforms import StockPlatformWorker

                st.write("🔧 Inicializace...")
                manager = JobManager()
                job = manager.get_job(st.session_state.job_id)

                stock = StockPlatformWorker()
                submissions = []
                st.write(f"✓ Připraveno pro {len(platforms)} platforem")

                total = len(st.session_state.assets) * len(platforms)
                st.write(f"📊 Celkem submission: {total}")
                
                progress_bar = st.progress(0)
                current = 0

                for asset_idx, asset in enumerate(st.session_state.assets, 1):
                    st.write(f"\n🖼️ Asset {asset_idx}/{len(st.session_state.assets)}")
                    
                    for platform in platforms:
                        current += 1
                        progress = current / total
                        progress_bar.progress(progress)
                        st.write(f"  ⏳ {platform}... ({current}/{total})")

                        platform_key = platform.lower().replace(" ", "_")

                        st.session_state.logger.log(
                            f"Preparing {platform} submission for asset {asset.id}", "INFO"
                        )

                        submission = stock.prepare_submission(asset, job, platform_key)
                        outbox_path = stock.create_outbox_file(submission)
                        submissions.append(outbox_path)
                        st.write(f"  ✓ {platform} připraven")

                        st.session_state.logger.log(f"✓ Created {platform} submission", "SUCCESS")

                progress_bar.progress(1.0)
                st.write(f"\n✨ Celkem vytvořeno: {len(submissions)} submission")
                st.session_state.logger.log(
                    f"✓ Created {len(submissions)} stock submissions", "SUCCESS"
                )
                status.update(label=f"✅ Vytvořeno {len(submissions)} submission!", state="complete")
                st.success(f"✓ Vytvořeno {len(submissions)} stock submission!")

            except Exception as e:
                status.update(label="❌ Chyba při přípravě submission", state="error")
                st.session_state.logger.log(f"✗ Stock submission failed: {e}", "ERROR")
                st.error(f"✗ Error: {e}")


def crop_tester_ui():
    """Crop tester UI for testing different crop ratios."""
    st.markdown("## ✂️ Crop Tester")
    
    st.info("Upload an image to test different crop ratios and see how it will look on various products.")
    
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg', 'webp'])
    
    if uploaded_file:
        try:
            img = Image.open(uploaded_file)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Original Image")
                display_image_safe(img)
                st.caption(f"Size: {img.width}x{img.height}")
            
            with col2:
                st.markdown("### Crop Preview")
                
                crop_type = st.selectbox(
                    "Select crop ratio",
                    ["Square 1:1", "Portrait 2:3", "Landscape 3:2", "Wide 16:9", "Tall 9:16"]
                )
                
                # Simple center crop preview
                if crop_type == "Square 1:1":
                    size = min(img.width, img.height)
                    left = (img.width - size) // 2
                    top = (img.height - size) // 2
                    cropped = img.crop((left, top, left + size, top + size))
                elif crop_type == "Portrait 2:3":
                    if img.width / img.height > 2/3:
                        new_width = int(img.height * 2/3)
                        left = (img.width - new_width) // 2
                        cropped = img.crop((left, 0, left + new_width, img.height))
                    else:
                        new_height = int(img.width * 3/2)
                        top = (img.height - new_height) // 2
                        cropped = img.crop((0, top, img.width, top + new_height))
                elif crop_type == "Landscape 3:2":
                    if img.width / img.height < 3/2:
                        new_width = int(img.height * 3/2)
                        left = (img.width - new_width) // 2
                        cropped = img.crop((left, 0, left + new_width, img.height))
                    else:
                        new_height = int(img.width * 2/3)
                        top = (img.height - new_height) // 2
                        cropped = img.crop((0, top, img.width, top + new_height))
                else:
                    cropped = img  # Placeholder for other ratios
                
                display_image_safe(cropped)
                st.caption(f"Cropped size: {cropped.width}x{cropped.height}")
                
        except Exception as e:
            st.error(f"Error processing image: {e}")
    else:
        st.info("👆 Upload an image to start testing crops")


def analytics_dashboard_ui():
    """Analytics and performance tracking dashboard."""
    st.header("📊 Analytics Dashboard")
    
    from artomate.core.job_manager import JobManager
    from artomate.db.extended_models import StockSubmission, AnalyticsSnapshot
    from artomate.db.database import get_db
    import pandas as pd
    
    manager = JobManager()
    db = next(get_db())
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_jobs = len(manager.list_jobs())
        st.metric("Total Jobs", total_jobs, delta=None)
    
    with col2:
        submissions = db.query(StockSubmission).all()
        st.metric("Total Submissions", len(submissions))
    
    with col3:
        total_downloads = sum(s.downloads_count for s in submissions)
        st.metric("Total Downloads", total_downloads)
    
    with col4:
        total_earnings = sum(s.earnings for s in submissions)
        st.metric("Total Earnings", f"${total_earnings:.2f}")
    
    st.markdown("---")
    
    # Performance by platform
    st.subheader("📈 Performance by Platform")
    
    if submissions:
        platform_data = {}
        for sub in submissions:
            platform = sub.platform.value
            if platform not in platform_data:
                platform_data[platform] = {
                    'submissions': 0,
                    'downloads': 0,
                    'earnings': 0,
                    'views': 0
                }
            platform_data[platform]['submissions'] += 1
            platform_data[platform]['downloads'] += sub.downloads_count
            platform_data[platform]['earnings'] += sub.earnings
            platform_data[platform]['views'] += sub.views_count
        
        df = pd.DataFrame.from_dict(platform_data, orient='index')
        st.dataframe(df, use_container_width=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(df['downloads'])
        
        with col2:
            st.bar_chart(df['earnings'])
    else:
        st.info("No submissions yet. Upload some content to see analytics!")
    
    st.markdown("---")
    
    # Recent submissions
    st.subheader("📝 Recent Submissions")
    
    if submissions:
        recent = submissions[-10:]  # Last 10
        
        data = []
        for sub in recent:
            data.append({
                'Platform': sub.platform.value,
                'Title': sub.title[:50] + '...' if len(sub.title) > 50 else sub.title,
                'Status': sub.status.value,
                'Downloads': sub.downloads_count,
                'Earnings': f"${sub.earnings:.2f}",
                'Date': sub.created_at.strftime('%Y-%m-%d')
            })
        
        df_recent = pd.DataFrame(data)
        st.dataframe(df_recent, use_container_width=True)
    else:
        st.info("No submissions to display")


def collections_ui():
    """Collections and campaigns management."""
    st.header("📁 Collections & Campaigns")
    
    from artomate.db.extended_models import Collection
    from artomate.db.database import get_db
    from artomate.core.job_manager import JobManager
    
    db = next(get_db())
    manager = JobManager()
    
    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📁 All Collections", "➕ Create New", "🔄 Bulk Operations"])
    
    with tab1:
        st.subheader("Your Collections")
        
        collections = db.query(Collection).all()
        
        if collections:
            for collection in collections:
                with st.expander(f"{'📅' if collection.is_campaign else '📁'} {collection.name}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Description:** {collection.description or 'No description'}")
                        st.write(f"**Theme:** {collection.theme or 'N/A'}")
                        st.write(f"**Category:** {collection.category or 'General'}")
                        st.write(f"**Jobs:** {len(collection.job_ids or [])}")
                        st.write(f"**Created:** {collection.created_at.strftime('%Y-%m-%d')}")
                        
                        if collection.tags:
                            st.write(f"**Tags:** {', '.join(collection.tags)}")
                    
                    with col2:
                        if st.button(f"🗑️ Delete", key=f"del_{collection.id}"):
                            db.delete(collection)
                            db.commit()
                            st.success("Collection deleted!")
                            st.rerun()
        else:
            st.info("No collections yet. Create your first collection below!")
    
    with tab2:
        st.subheader("Create New Collection")
        
        with st.form("new_collection"):
            name = st.text_input("Collection Name", placeholder="My Awesome Collection")
            description = st.text_area("Description", placeholder="Describe this collection...")
            theme = st.text_input("Theme", placeholder="e.g., Animals, Nature, Abstract")
            category = st.selectbox("Category", [
                "General", "Animals", "Nature", "Abstract", "Patterns", 
                "Holidays", "Seasonal", "Business", "Art", "Other"
            ])
            is_campaign = st.checkbox("This is a campaign (time-limited)")
            
            if is_campaign:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Campaign Start")
                with col2:
                    end_date = st.date_input("Campaign End")
            
            tags_input = st.text_input("Tags (comma-separated)", placeholder="tag1, tag2, tag3")
            
            # Select jobs to add
            all_jobs = manager.list_jobs()
            if all_jobs:
                selected_jobs = st.multiselect(
                    "Add Jobs to Collection",
                    options=[f"Job {j['id']}: {j['theme']}" for j in all_jobs],
                    default=[]
                )
            
            submitted = st.form_submit_button("Create Collection", use_container_width=True)
            
            if submitted and name:
                tags = [t.strip() for t in tags_input.split(',') if t.strip()]
                job_ids = [int(j.split(':')[0].replace('Job ', '')) for j in selected_jobs] if all_jobs else []
                
                campaign_dates = None
                if is_campaign:
                    campaign_dates = {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                
                collection = Collection(
                    name=name,
                    description=description,
                    theme=theme,
                    category=category,
                    is_campaign=is_campaign,
                    campaign_dates=campaign_dates,
                    tags=tags,
                    job_ids=job_ids
                )
                
                db.add(collection)
                db.commit()
                
                st.success(f"✅ Collection '{name}' created!")
                st.rerun()
    
    with tab3:
        st.subheader("🔄 Bulk Operations")
        
        collections = db.query(Collection).all()
        
        if collections:
            selected_collection = st.selectbox(
                "Select Collection",
                options=[c.name for c in collections]
            )
            
            collection = next((c for c in collections if c.name == selected_collection), None)
            
            if collection and collection.job_ids:
                st.write(f"**Jobs in collection:** {len(collection.job_ids)}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📤 Publish All to Stock Platforms", use_container_width=True):
                        st.info("Bulk publishing feature - coming soon!")
                        # Implement bulk publishing logic
                
                with col2:
                    if st.button("📱 Post All to Social Media", use_container_width=True):
                        st.info("Bulk social posting feature - coming soon!")
                        # Implement bulk social posting
            else:
                st.warning("Selected collection has no jobs")
        else:
            st.info("Create collections first to use bulk operations")


def scheduler_ui():
    """Publication scheduling interface."""
    st.header("⏰ Publication Scheduler")
    
    from artomate.db.extended_models import ScheduledPublication, PublicationStatus
    from artomate.db.database import get_db
    from artomate.workers.publication_scheduler import PublicationScheduler
    from datetime import datetime, timedelta
    
    db = next(get_db())
    scheduler = PublicationScheduler(db)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📅 Upcoming", "➕ Schedule New", "📊 History"])
    
    with tab1:
        st.subheader("Upcoming Publications")
        
        upcoming = scheduler.get_upcoming_publications(hours=168)  # Next 7 days
        
        if upcoming:
            for pub in upcoming:
                with st.expander(f"⏰ {pub.publication_type.upper()} - {pub.scheduled_for.strftime('%Y-%m-%d %H:%M')}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Type:** {pub.publication_type}")
                        st.write(f"**Platforms:** {', '.join(pub.target_platforms)}")
                        st.write(f"**Status:** {pub.status.value}")
                        st.write(f"**Job ID:** {pub.job_id}")
                        
                        if pub.retry_count > 0:
                            st.warning(f"Retries: {pub.retry_count}/{pub.max_retries}")
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{pub.id}"):
                            if scheduler.cancel_publication(pub.id):
                                st.success("Cancelled!")
                                st.rerun()
                        
                        if st.button("⏰ Reschedule", key=f"resched_{pub.id}"):
                            st.session_state[f'reschedule_{pub.id}'] = True
                    
                    # Reschedule form
                    if st.session_state.get(f'reschedule_{pub.id}'):
                        new_date = st.date_input("New Date", key=f"date_{pub.id}")
                        new_time = st.time_input("New Time", key=f"time_{pub.id}")
                        
                        if st.button("✅ Confirm", key=f"confirm_{pub.id}"):
                            new_datetime = datetime.combine(new_date, new_time)
                            if scheduler.reschedule_publication(pub.id, new_datetime):
                                st.success("Rescheduled!")
                                del st.session_state[f'reschedule_{pub.id}']
                                st.rerun()
        else:
            st.info("No upcoming publications scheduled")
    
    with tab2:
        st.subheader("Schedule New Publication")
        
        from artomate.core.job_manager import JobManager
        manager = JobManager()
        
        all_jobs = manager.list_jobs()
        
        if not all_jobs:
            st.warning("No jobs available. Create a job first!")
        else:
            with st.form("schedule_publication"):
                job_options = [f"Job {j['id']}: {j['theme']}" for j in all_jobs]
                selected_job = st.selectbox("Select Job", options=job_options)
                job_id = int(selected_job.split(':')[0].replace('Job ', ''))
                
                pub_type = st.selectbox("Publication Type", ["stock", "social", "marketplace"])
                
                # Platform selection based on type
                if pub_type == "stock":
                    all_platforms = [
                        "shutterstock", "adobe_stock", "getty_images", "istock", 
                        "depositphotos", "unsplash", "pexels", "pixabay"
                    ]
                elif pub_type == "social":
                    all_platforms = ["instagram", "tiktok", "youtube_shorts", "facebook"]
                else:
                    all_platforms = ["etsy", "shopify", "amazon"]
                
                selected_platforms = st.multiselect("Target Platforms", options=all_platforms)
                
                col1, col2 = st.columns(2)
                with col1:
                    schedule_date = st.date_input("Schedule Date", value=datetime.now().date())
                with col2:
                    schedule_time = st.time_input("Schedule Time", value=datetime.now().time())
                
                schedule_mode = st.radio(
                    "Scheduling Mode",
                    ["Single Time", "Staggered (24h intervals)"]
                )
                
                submit = st.form_submit_button("📅 Schedule Publication", use_container_width=True)
                
                if submit and selected_platforms:
                    scheduled_datetime = datetime.combine(schedule_date, schedule_time)
                    
                    if schedule_mode == "Single Time":
                        pub = scheduler.schedule_publication(
                            job_id=job_id,
                            publication_type=pub_type,
                            target_platforms=selected_platforms,
                            scheduled_for=scheduled_datetime
                        )
                        st.success(f"✅ Publication scheduled for {scheduled_datetime}")
                    else:
                        pubs = scheduler.schedule_bulk_publication(
                            job_id=job_id,
                            platforms=selected_platforms,
                            interval_hours=24
                        )
                        st.success(f"✅ Scheduled {len(pubs)} publications with 24h intervals")
                    
                    st.rerun()
    
    with tab3:
        st.subheader("Publication History")
        
        all_pubs = db.query(ScheduledPublication).order_by(
            ScheduledPublication.created_at.desc()
        ).limit(50).all()
        
        if all_pubs:
            for pub in all_pubs:
                status_emoji = {
                    "published": "✅",
                    "failed": "❌",
                    "cancelled": "🚫",
                    "scheduled": "⏰"
                }.get(pub.status.value, "❓")
                
                st.write(f"{status_emoji} **{pub.publication_type}** - {pub.scheduled_for.strftime('%Y-%m-%d %H:%M')} - {pub.status.value}")
                
                if pub.results:
                    with st.expander("View Results"):
                        st.json(pub.results)
        else:
            st.info("No publication history yet")


def image_editor_ui():
    """Image editor interface."""
    st.header("✏️ Image Editor")
    
    from artomate.utils.image_editor import ImageEditor, FilterType, WatermarkPosition
    from PIL import Image
    import io
    import base64
    
    # File upload
    uploaded_file = st.file_uploader("Upload Image to Edit", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        # Save to temp location
        temp_path = Path(f"data/assets/temp_{uploaded_file.name}")
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.read())
        
        # Create editor
        editor = ImageEditor(temp_path)
        
        # Show original
        st.subheader("Original Image")
        display_image_safe(str(temp_path), width=400)
        
        st.markdown("---")
        
        # Editing tools
        st.subheader("🛠️ Editing Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Resize
            st.markdown("### 📐 Resize")
            new_width = st.number_input("Width", value=editor.image.width, min_value=100)
            new_height = st.number_input("Height", value=editor.image.height, min_value=100)
            maintain_aspect = st.checkbox("Maintain Aspect Ratio", value=True)
            
            if st.button("Apply Resize"):
                editor.resize(new_width, new_height, maintain_aspect=maintain_aspect)
                st.success("Resized!")
            
            st.markdown("---")
            
            # Filters
            st.markdown("### 🎨 Filters")
            filter_type = st.selectbox("Filter", [f.value for f in FilterType])
            
            if st.button("Apply Filter"):
                editor.apply_filter(FilterType(filter_type))
                st.success(f"Applied {filter_type} filter!")
            
            st.markdown("---")
            
            # Adjustments
            st.markdown("### ⚙️ Adjustments")
            brightness = st.slider("Brightness", 0.0, 2.0, 1.0, 0.1)
            contrast = st.slider("Contrast", 0.0, 2.0, 1.0, 0.1)
            saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
            
            if st.button("Apply Adjustments"):
                editor.adjust_brightness(brightness)
                editor.adjust_contrast(contrast)
                editor.adjust_saturation(saturation)
                st.success("Adjustments applied!")
        
        with col2:
            # Watermark
            st.markdown("### 💧 Watermark")
            watermark_text = st.text_input("Watermark Text", value="© Your Name")
            watermark_position = st.selectbox("Position", [p.value for p in WatermarkPosition])
            watermark_opacity = st.slider("Opacity", 0.0, 1.0, 0.5, 0.1)
            
            if st.button("Add Watermark"):
                editor.add_watermark(
                    watermark_text,
                    WatermarkPosition(watermark_position),
                    watermark_opacity
                )
                st.success("Watermark added!")
            
            st.markdown("---")
            
            # Text overlay
            st.markdown("### 📝 Text Overlay")
            overlay_text = st.text_input("Text", value="Hello World")
            text_x = st.number_input("X Position", value=50, min_value=0)
            text_y = st.number_input("Y Position", value=50, min_value=0)
            text_size = st.slider("Font Size", 10, 100, 40)
            
            if st.button("Add Text"):
                editor.add_text(overlay_text, (text_x, text_y), font_size=text_size)
                st.success("Text added!")
            
            st.markdown("---")
            
            # Transforms
            st.markdown("### 🔄 Transforms")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("⬅️ Flip Horizontal"):
                    editor.flip_horizontal()
                    st.success("Flipped!")
            
            with col_b:
                if st.button("⬆️ Flip Vertical"):
                    editor.flip_vertical()
                    st.success("Flipped!")
            
            rotation = st.slider("Rotate (degrees)", -180, 180, 0)
            if st.button("Apply Rotation"):
                editor.rotate(rotation)
                st.success(f"Rotated {rotation}°!")
        
        st.markdown("---")
        
        # Preview
        st.subheader("👁️ Preview")
        
        # Convert current image to bytes for display
        img_byte_arr = io.BytesIO()
        editor.image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        display_image_safe(img_byte_arr, width=600)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reset to Original", use_container_width=True):
                editor.reset()
                st.success("Reset!")
                st.rerun()
        
        with col2:
            # Download button
            b64 = base64.b64encode(img_byte_arr).decode()
            href = f'<a href="data:image/png;base64,{b64}" download="edited_{uploaded_file.name}">⬇️ Download</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        with col3:
            # Save to assets
            if st.button("💾 Save to Assets", use_container_width=True):
                output_path = Path(f"data/assets/edited_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.name}")
                editor.save(output_path)
                st.success(f"Saved to {output_path}!")
    
    else:
        st.info("📤 Upload an image to start editing")


# ============================================================================
# PIPELINE MODE - NEW WORKFLOW SYSTEM
# ============================================================================

def render_pipeline_progress():
    """Render progress bar at the top showing pipeline completion."""
    stages = [
        "Brief", "Prompt Matrix", "Text Generation", "Image Generation",
        "Video Generation", "Asset Review", "Product Creation", "Publishing", "Analytics"
    ]
    
    current_stage = st.session_state.get('pipeline_stage', 0)
    total_stages = len(stages)
    
    # Calculate completion
    progress_pct = (current_stage / total_stages) * 100
    
    # Top bar with job info
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        job_name = st.session_state.get('job_name', 'New Job')
        st.markdown(f"**Job:** {job_name}")
    
    with col2:
        st.markdown(f"**Stage:** {stages[current_stage]} ({current_stage + 1} / {total_stages})")
    
    with col3:
        st.markdown(f"**Progress:** {int(progress_pct)}%")
    
    # Progress bar
    st.progress(progress_pct / 100)
    
    # Output counters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Texts", st.session_state.get('pipeline_texts_count', 0))
    with col2:
        st.metric("🖼️ Images", st.session_state.get('pipeline_images_count', 0))
    with col3:
        st.metric("🎬 Videos", st.session_state.get('pipeline_videos_count', 0))
    with col4:
        st.metric("📦 Products", st.session_state.get('pipeline_products_count', 0))
    
    st.markdown("---")


def render_pipeline_sidebar():
    """Render pipeline stages in sidebar with status indicators."""
    stages = [
        ("① Brief", 0),
        ("② Prompt Matrix", 1),
        ("③ Text Generation", 2),
        ("④ Image Generation", 3),
        ("⑤ Video Generation", 4),
        ("⑥ Asset Review", 5),
        ("⑦ Product Creation", 6),
        ("⑧ Publishing", 7),
        ("⑨ Analytics", 8)
    ]
    
    current_stage = st.session_state.get('pipeline_stage', 0)
    completed_stages = st.session_state.get('pipeline_completed', set())
    
    st.markdown("## 🔄 Pipeline Stages")
    
    for stage_name, stage_num in stages:
        # Determine status
        if stage_num in completed_stages:
            status = "🟢"  # Completed
        elif stage_num == current_stage:
            status = "🔵"  # In progress
        elif stage_num < current_stage:
            status = "⚠️"  # Skipped/Error
        else:
            status = "⭕"  # Not started
        
        # Make clickable if completed or current
        if stage_num <= current_stage:
            if st.button(f"{status} {stage_name}", key=f"stage_{stage_num}", use_container_width=True):
                st.session_state.pipeline_stage = stage_num
                st.rerun()
        else:
            st.button(f"{status} {stage_name}", key=f"stage_{stage_num}", use_container_width=True, disabled=True)


def pipeline_stage_brief():
    """Stage 1: Brief - Define what we're creating."""
    st.markdown("## ① Brief")
    st.markdown("Define what you want to create.")
    
    # Constants are defined at the top of the file
    ANIMALS = [
        "Ant", "Antelope", "Arctic Fox", "Bat", "Bear", "Beaver", "Bee",
        "Beetle", "Betta Fish", "Boar", "Buffalo", "Butterfly", "Camel",
        "Canary", "Cat", "Chameleon", "Cheetah", "Chicken", "Coral Fish",
        "Cow", "Crab", "Crocodile", "Crow", "Deer", "Dog", "Dolphin",
        "Donkey", "Dove", "Dragon", "Dragonfly", "Duck", "Eagle", "Elephant",
        "Fairy", "Flamingo", "Fox", "Frog", "Gazelle", "Giraffe", "Goat",
        "Goldfish", "Gorilla", "Griffin", "Guinea Pig", "Hamster", "Hawk",
        "Hedgehog", "Hippo", "Horse", "Hummingbird", "Hyena", "Iguana",
        "Jellyfish", "Kangaroo", "Koala", "Ladybug", "Lemur", "Leopard",
        "Lion", "Lizard", "Lynx", "Meerkat", "Mermaid", "Monkey", "Moose",
        "Moth", "Octopus", "Orca", "Otter", "Owl", "Panda", "Parrot",
        "Peacock", "Pegasus", "Pelican", "Penguin", "Phoenix", "Pig",
        "Polar Bear", "Puma", "Rabbit", "Raccoon", "Reindeer", "Rhino",
        "Rooster", "Sea Turtle", "Seahorse", "Seal", "Shark", "Sheep",
        "Skunk", "Snake", "Spider", "Spirit Animal", "Squirrel", "Starfish",
        "Stingray", "Swan", "Tiger", "Turtle", "Unicorn", "Walrus", "Whale",
        "Wolf", "Zebra"
    ]
    
    STYLES = [
        "Realistic", "Watercolor", "Line Art", "Pop Art", "Abstract", "Boho",
        "Cute", "Anime", "Fantasy", "Minimalist", "Geometric", "Japandi",
        "Vintage", "Cyberpunk", "Neon", "Vaporwave", "Art Deco", "Cartoon",
        "Low Poly", "3D Render", "Ink Painting", "Pencil Sketch",
        "Pastel Illustrative", "Botanical", "Retro", "Modern Poster"
    ]
    
    ALL_THEMES = [
        "Christmas", "Valentine", "Halloween", "Easter", "Spring Blossom",
        "Summer Beach", "Fall Harvest", "Winter Snow", "Independence Day",
        "Memorial Day", "Pride Month", "St. Patrick's Day", "Lunar New Year",
        "Thanksgiving", "Horror Spooky", "Forest", "Ocean", "Space", "Desert",
        "Mountain", "Rainy Mood", "Snowy Night", "Aurora", "Japanese Spring",
        "Autumn Leaves", "Baby Nursery", "Wedding", "Cottagecore",
        "Coastal Aesthetic"
    ]
    
    job_name = st.text_input(
        "Job Name",
        value=st.session_state.get('job_name', 'Winter Calendar 2026'),
        help="Give your project a name"
    )
    st.session_state.job_name = job_name
    
    description = st.text_area(
        "Description",
        value=st.session_state.get('brief_description', 'Create monthly calendar images with cute animals'),
        help="Describe what you want to create",
        height=100
    )
    st.session_state.brief_description = description
    
    st.markdown("### Target Platforms")
    st.info("💡 Defaultně budou produkty vytvořeny pro všechny platformy (Printify, Stock, Social Media)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        printify = st.checkbox("Printify", value=True, help="Print-on-demand produkty")
    with col2:
        stock = st.checkbox("Stock Platforms", value=True, help="Shutterstock, Adobe Stock, atd.")
    with col3:
        social = st.checkbox("Social Media", value=True, help="Instagram, TikTok, YouTube Shorts")
    
    st.session_state.target_printify = printify
    st.session_state.target_stock = stock
    st.session_state.target_social = social
    
    st.markdown("### Creative Direction")
    
    # Animals selection
    st.markdown("#### 🐾 Animals")
    animals = st.multiselect(
        "Select animals to feature",
        ANIMALS,
        default=st.session_state.get('brief_animals', ["Cat", "Dog"]),
        help="Choose which animals will appear in your content"
    )
    st.session_state.brief_animals = animals
    
    # Themes and Styles
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🎨 Themes")
        themes = st.multiselect(
            "Select themes",
            ALL_THEMES,
            default=st.session_state.get('brief_themes', ["Christmas", "Winter Snow"]),
            help="Select themes for your content",
            key="brief_themes_select"
        )
        st.session_state.brief_themes = themes
    
    with col2:
        st.markdown("#### ✨ Design Styles")
        styles = st.multiselect(
            "Select styles",
            STYLES,
            default=st.session_state.get('brief_styles', ["Minimalist", "Japandi"]),
            help="Select design styles",
            key="brief_styles_select"
        )
        st.session_state.brief_styles = styles
    
    st.markdown("---")
    
    # Validation
    can_continue = bool(job_name and description and (printify or stock or social) and animals and themes and styles)
    
    if st.button("➡️ Continue to Prompt Matrix", type="primary", use_container_width=True, disabled=not can_continue):
        st.session_state.pipeline_stage = 1
        if 'pipeline_completed' not in st.session_state:
            st.session_state.pipeline_completed = set()
        st.session_state.pipeline_completed.add(0)
        st.rerun()


def pipeline_stage_prompt_matrix():
    """Stage 2: Prompt Matrix - Configure combinations."""
    st.markdown("## ② Prompt Matrix")
    st.markdown("Configure your content generation matrix.")
    
    # Use data from Brief stage if available
    brief_animals = st.session_state.get('brief_animals', ["Cat", "Dog"])
    brief_styles = st.session_state.get('brief_styles', ["Minimalist", "Japandi"])
    brief_themes = st.session_state.get('brief_themes', ["Christmas", "Winter Snow"])
    
    st.markdown("### 📋 Selected Elements")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🐾 Animals**")
        for animal in brief_animals:
            st.write(f"• {animal}")
    
    with col2:
        st.markdown("**✨ Design Styles**")
        for style in brief_styles:
            st.write(f"• {style}")
    
    with col3:
        st.markdown("**🎨 Themes**")
        for theme in brief_themes:
            st.write(f"• {theme}")
    
    st.markdown("---")
    
    # Number of images to generate
    st.markdown("### 📅 Monthly Calendar")
    months = st.slider(
        "Number of calendar months", 
        1, 12, 12,
        help="Generate one unique image for each calendar month (January, February, etc.)"
    )
    
    # Total images = one per month
    total_images = months
    
    st.markdown("### 📊 Generation Plan")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Calendar Months", months)
        st.caption("January through December" if months == 12 else f"First {months} months")
    with col2:
        st.metric("🖼️ Images to Generate", total_images)
        st.caption("One image per month")
    with col3:
        st.metric("🎨 Combined Elements", f"{len(brief_animals)}+{len(brief_styles)}+{len(brief_themes)}")
        st.caption("In each image")
    
    st.success(f"✅ Will generate **{total_images} calendar images** - each animal with natural seasonal behavior for their habitat")
    
    # Show example for specific months with animal-specific behavior
    with st.expander("📝 Example: Animal behaviors by calendar month & habitat location"):
        # Define animal-specific behaviors by month (based on natural habitat location and seasonal ecology)
        animal_behaviors = {
            "Cat": {
                "January": "🏠 Domestic indoor: cozy napping by warm fireplace in human homes",
                "February": "🏠 Urban dwellings: playful hunting of winter shadows through windows",
                "March": "🏡 Suburban homes: spring awakening, curious window watching as weather warms",
                "April": "🌸 Gardens/yards: first outdoor exploration after winter hibernation",
                "May": "🦋 Blooming gardens: hunting butterflies and insects in urban green spaces",
                "June": "☀️ Household sunny spots: lounging in long summer daylight",
                "July": "❄️ Cool indoor spaces: seeking shade and tile floors during heat waves",
                "August": "🏠 Indoor/outdoor mix: lazy summer sunbathing transitions",
                "September": "🍂 Yards/gardens: playful with falling autumn leaves",
                "October": "🎃 Decorated homes: Halloween curiosity, exploring seasonal decorations",
                "November": "🏠 Indoor comfort: cozy Thanksgiving naps as temperatures drop",
                "December": "🎄 Festive homes: playing with Christmas ornaments and decorations"
            },
            "Dog": {
                "January": "❄️ Temperate zones: snow zoomies and playing in fresh powder",
                "February": "🏠 Indoor spaces: loving cuddles and Valentine treats with family",
                "March": "🌧️ Parks/trails: muddy paw spring walks in rain and thaw",
                "April": "🐰 Suburban yards: Easter egg hunt enthusiastic participant",
                "May": "🏞️ Open fields: outdoor adventures, chasing balls in perfect weather",
                "June": "🏖️ Beaches/lakes: beach swimming and water fetch games",
                "July": "💦 Backyards: cooling off in kiddie pools during summer heat",
                "August": "🌅 Neighborhoods: late evening walks to avoid intense heat",
                "September": "🍁 Forest trails: autumn hikes through colorful mountain forests",
                "October": "🎃 Urban areas: dressed in Halloween costumes for festivities",
                "November": "🦃 Family homes: begging for Thanksgiving turkey scraps",
                "December": "🎁 Living rooms: excited unwrapping Christmas presents with family"
            },
            "Polar Bear": {
                "January": "🧊 Arctic sea ice: hunting ringed seals on thick frozen ocean at peak",
                "February": "❄️ Ice dens: mother with newborn cubs in snow caves",
                "March": "🌨️ Arctic coast: emerging from winter maternity dens with cubs",
                "April": "🦭 Spring ice: teaching young cubs to hunt seals on ice edges",
                "May": "🌊 Ice floes: fishing at melting ice edge as temperatures rise",
                "June": "💧 Arctic waters: swimming in frigid ocean as ice retreats dramatically",
                "July": "🏔️ Arctic tundra: rare summer rest on land during ice-free period",
                "August": "🌅 Coastal shores: hunting opportunities before autumn freeze returns",
                "September": "🧊 New ice: fattening up as sea ice begins forming again",
                "October": "❄️ Expanding ice: first snow arrival in Arctic, returning to ice",
                "November": "🏔️ Snow banks: pregnant females building winter maternity dens",
                "December": "🌑 Arctic darkness: deep winter hunting in 24-hour polar night"
            },
            "Panda": {
                "January": "🎋 Mountain forests (China): munching bamboo shoots in winter snow",
                "February": "💚 Bamboo groves: mating season courtship in high-altitude habitat",
                "March": "🌱 Spring forest: spring bamboo shoots feast in Sichuan mountains",
                "April": "⛰️ Misty slopes: playful rolling down forest hills",
                "May": "👶 Forest dens: cub birth season in secluded mountain caves",
                "June": "🌳 Forest canopy: teaching tiny cubs to climb bamboo trees",
                "July": "💦 Mountain streams: cooling in cold streams during summer heat",
                "August": "🎋 Diverse groves: eating various summer bamboo species",
                "September": "🍂 Autumn forest: preparing for autumn in mountain habitat",
                "October": "🎋 Dense groves: enjoying autumn bamboo varieties",
                "November": "❄️ High altitude: thick winter coat growing as snow arrives",
                "December": "🌨️ Winter forest: winter bamboo forest wandering in deep snow"
            },
            "Penguin": {
                "January": "🌞 Antarctic coast: summer peak, feeding chicks in 24-hour daylight",
                "February": "🏊 Southern Ocean: teaching chicks to swim in cold waters",
                "March": "🧊 Ice shelves: autumn migration to winter breeding sites begins",
                "April": "🐧 Colony shores: forming massive winter colonies on ice",
                "May": "❄️ Packed colony: huddling for warmth as darkness approaches",
                "June": "🌑 Antarctic winter: complete darkness, male egg incubation begins",
                "July": "🥚 Ice platform: father protecting eggs during coldest month -60°C",
                "August": "🐣 Colony center: egg hatching in extreme Antarctic conditions",
                "September": "🌅 Returning light: early spring chick care as sun returns",
                "October": "🐟 Open water: spring fishing expeditions in Southern Ocean",
                "November": "👶 Growing colony: chicks growing rapidly in crèches",
                "December": "🏊 Peak summer: intensive hunting in ice-free Antarctic waters"
            },
            "Lion": {
                "January": "🌾 African savanna: dry season hunting at peak, prey at waterholes",
                "February": "🦁 Grasslands: mating season roars echo across dry plains",
                "March": "🌵 Arid plains: preparing for wet season, late dry period",
                "April": "🌧️ Rainy savanna: rainy season rest, prey disperses widely",
                "May": "🌱 Green grasslands: cubs playing in lush vegetation after rains",
                "June": "👨‍👩‍👧 Pride territory: teaching cubs hunting skills in tall grass",
                "July": "🌾 Dense cover: mid-wet season, using grass cover for hunting",
                "August": "🦁 Open plains: territorial disputes as resources concentrate",
                "September": "🏃 Migration routes: hunting migrating wildebeest herds",
                "October": "💧 Water sources: cooling down by shrinking waterholes",
                "November": "🌵 Dry grassland: early dry season coordinated stalking",
                "December": "🌳 Acacia shade: pride bonding under trees during intense heat"
            },
            "Fox": {
                "January": "❄️ Northern forest: hunting mice under deep snow using sound",
                "February": "💕 Woodland: mating season courtship dances in snow",
                "March": "🏠 Forest den: preparing underground den for upcoming cubs",
                "April": "👶 Den nursery: cubs born in safe underground chamber",
                "May": "🦊 Den entrance: teaching cubs to pounce on prey outside den",
                "June": "🌲 Forest clearing: family playing outside den in long daylight",
                "July": "🌅 Woodland edge: hunting rodents in long summer evenings",
                "August": "🎓 Territory: cubs learning independence, practicing hunting",
                "September": "🍂 Cache sites: storing food for winter throughout territory",
                "October": "🍁 Autumn forest: hunting in colorful deciduous forest",
                "November": "❄️ First snow: thick winter coat fully grown for harsh season",
                "December": "🌨️ Deep winter: solitary hunting in snowy northern woodland"
            }
        }
        
        month_names = ["January", "February", "March", "April", "May", "June", 
                       "July", "August", "September", "October", "November", "December"]
        
        # Show examples for first few months
        for i in range(min(2, months)):
            month_name = month_names[i]
            st.markdown(f"**🗓️ {month_name} Calendar Image:**")
            
            for animal in brief_animals[:3]:  # Show first 3 animals as examples
                if animal in animal_behaviors:
                    behavior = animal_behaviors[animal][month_name]
                else:
                    # Generic behavior if animal not in dictionary
                    behavior = "seasonal activity appropriate for their natural habitat"
                
                st.text(f"  • {animal}: {behavior}")
            
            if len(brief_animals) > 3:
                st.text(f"  • ... and {len(brief_animals) - 3} more animals")
            
            # Show how it will be combined in the prompt
            styles_str = ', '.join(brief_styles)
            themes_str = ', '.join(brief_themes)
            st.caption(f"   → Combined with: {styles_str} style, {themes_str} theme")
            st.text("")
        
        if months > 2:
            st.text(f"... and {months - 2} more calendar months with unique behaviors")
    
    st.info(f"💡 Each of the **{months} calendar months** will show the month name with animals displaying natural behaviors for that time of year!")
    
    # Save to session
    st.session_state.matrix_animals = brief_animals
    st.session_state.matrix_styles = brief_styles
    st.session_state.matrix_themes = brief_themes
    st.session_state.matrix_months = months
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Brief", use_container_width=True):
            st.session_state.pipeline_stage = 0
            st.rerun()
    with col2:
        if st.button("➡️ Generate Text Prompts", type="primary", use_container_width=True, disabled=total_images == 0):
            st.session_state.pipeline_stage = 2
            st.session_state.pipeline_completed.add(1)
            st.rerun()


def pipeline_stage_text_generation():
    """Stage 3: Text Generation - Generate prompts."""
    st.markdown("## ③ Text Generation")
    st.markdown("Generate AI prompts for your images.")
    
    # Check if we have matrix data
    if not st.session_state.get('matrix_animals'):
        st.warning("⚠️ Please complete Prompt Matrix first")
        return
    
    # Generate button
    if 'generated_prompts' not in st.session_state or not st.session_state.generated_prompts:
        if st.button("🚀 Start Generation", type="primary", use_container_width=True):
            with st.spinner("Generating prompts..."):
                # Use existing prompt generator
                from artomate.workers.prompt_generator import PromptGenerator
                generator = PromptGenerator()
                
                animals = st.session_state.matrix_animals
                styles = st.session_state.matrix_styles
                themes = st.session_state.matrix_themes
                months = st.session_state.matrix_months
                
                prompts = []
                for animal in animals:
                    for style in styles:
                        for theme in themes:
                            if months > 1:
                                for month in range(1, months + 1):
                                    prompt = f"{style} style, {animal} with {theme} theme, month {month}"
                                    prompts.append(prompt)
                            else:
                                prompt = f"{style} style, {animal} with {theme} theme"
                                prompts.append(prompt)
                
                st.session_state.generated_prompts = prompts
                st.session_state.pipeline_texts_count = len(prompts)
                st.rerun()
    else:
        # Show generated prompts
        st.success(f"✅ Generated {len(st.session_state.generated_prompts)} prompts")
        
        with st.expander("📝 View Prompts", expanded=False):
            for idx, prompt in enumerate(st.session_state.generated_prompts[:20], 1):
                st.text(f"{idx}. {prompt}")
            if len(st.session_state.generated_prompts) > 20:
                st.info(f"... and {len(st.session_state.generated_prompts) - 20} more")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Back to Matrix", use_container_width=True):
                st.session_state.pipeline_stage = 1
                st.rerun()
        with col2:
            if st.button("➡️ Generate Images", type="primary", use_container_width=True):
                st.session_state.pipeline_stage = 3
                st.session_state.pipeline_completed.add(2)
                st.rerun()


def pipeline_stage_image_generation():
    """Stage 4: Image Generation - Create images."""
    st.markdown("## ④ Image Generation")
    st.markdown("Generate images from your prompts.")
    
    if not st.session_state.get('generated_prompts'):
        st.warning("⚠️ Please generate prompts first")
        return
    
    # Initialize generation state
    if 'pipeline_images_generated' not in st.session_state:
        st.session_state.pipeline_images_generated = 0
    if 'pipeline_images_total' not in st.session_state:
        st.session_state.pipeline_images_total = len(st.session_state.generated_prompts)
    
    total_images = st.session_state.pipeline_images_total
    generated_count = st.session_state.pipeline_images_generated
    
    # Show progress
    progress_percent = (generated_count / total_images * 100) if total_images > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🖼️ Total Images", total_images)
    with col2:
        st.metric("✅ Generated", generated_count)
    with col3:
        st.metric("📊 Progress", f"{progress_percent:.0f}%")
    
    # Progress bar for image generation
    st.markdown("### 🎨 Generation Progress")
    progress_bar = st.progress(progress_percent / 100)
    
    if generated_count < total_images:
        st.info(f"🔄 Ready to generate {total_images - generated_count} remaining images")
        
        # Generation controls
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("🎨 Start Generation", type="primary", use_container_width=True):
                # Simulate image generation
                with st.spinner("Generating images..."):
                    import time
                    # In real implementation, this would call actual image generation
                    for i in range(total_images):
                        st.session_state.pipeline_images_generated = i + 1
                        progress_bar.progress((i + 1) / total_images)
                        time.sleep(0.1)  # Simulate work
                    
                    st.session_state.pipeline_completed.add(3)
                    st.rerun()
        
        with col2:
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.pipeline_images_generated = total_images
                st.session_state.pipeline_completed.add(3)
                st.rerun()
    else:
        st.success(f"✅ All {total_images} images generated successfully!")
        
        # Show generated images preview
        with st.expander("🖼️ Preview Generated Images", expanded=False):
            st.markdown("**Image generation would display results here...**")
            st.markdown("(Using existing Generate Variants functionality)")
            
            # Mock image grid
            cols = st.columns(4)
            for idx in range(min(8, total_images)):
                with cols[idx % 4]:
                    st.markdown(f"**Image {idx + 1}**")
                    st.caption(f"Prompt {idx + 1}")
            
            if total_images > 8:
                st.info(f"... and {total_images - 8} more images")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Back to Prompts", use_container_width=True):
            st.session_state.pipeline_stage = 2
            st.rerun()
    with col2:
        if generated_count >= total_images:
            if st.button("➡️ Continue to Video", type="primary", use_container_width=True):
                st.session_state.pipeline_stage = 4
                st.rerun()
        else:
            st.button("➡️ Continue to Video", use_container_width=True, disabled=True, help="Complete image generation first")


def render_pipeline_mode():
    """Main pipeline mode renderer."""
    # Initialize pipeline state
    if 'pipeline_stage' not in st.session_state:
        st.session_state.pipeline_stage = 0
    if 'pipeline_completed' not in st.session_state:
        st.session_state.pipeline_completed = set()
    
    # Render progress bar at top
    render_pipeline_progress()
    
    # Render current stage
    current_stage = st.session_state.pipeline_stage
    
    if current_stage == 0:
        pipeline_stage_brief()
    elif current_stage == 1:
        pipeline_stage_prompt_matrix()
    elif current_stage == 2:
        pipeline_stage_text_generation()
    elif current_stage == 3:
        pipeline_stage_image_generation()
    else:
        st.info(f"Stage {current_stage + 1} - Coming soon...")
        if st.button("⬅️ Back"):
            st.session_state.pipeline_stage = max(0, current_stage - 1)
            st.rerun()


def main():
    """Main UI."""

    # Header
    st.markdown('<div class="main-header">🎨 Artomate - Content to Commerce</div>',
                unsafe_allow_html=True)

    # Initialize current page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🎨 Create Job"

    # Check UI mode
    if 'ui_mode' not in st.session_state:
        st.session_state.ui_mode = 'classic'

    # Sidebar Navigation
    with st.sidebar:
        # A/B Test: UI Mode (at the top)
        st.markdown("## 🧪 A/B Test")
        
        if 'ui_mode' not in st.session_state:
            st.session_state.ui_mode = 'classic'
        
        ui_mode = st.radio(
            "Typ rozhraní:",
            options=['classic', 'pipeline'],
            format_func=lambda x: {
                'classic': '📋 Klasické (Menu)',
                'pipeline': '🔄 Pipeline (Workflow)'
            }[x],
            index=0 if st.session_state.ui_mode == 'classic' else 1,
            help="Vyberte typ uživatelského rozhraní:\n- Klasické: současné menu s jednotlivými stránkami\n- Pipeline: progresivní workflow s kroky 1-9"
        )
        
        if ui_mode != st.session_state.ui_mode:
            st.session_state.ui_mode = ui_mode
            # Initialize pipeline state if switching to pipeline
            if ui_mode == 'pipeline' and 'pipeline_stage' not in st.session_state:
                st.session_state.pipeline_stage = 0  # Start at Brief
            st.rerun()
        
        st.markdown("---")
        
        # Show different navigation based on mode
        if st.session_state.ui_mode == 'classic':
            # CLASSIC MODE: Menu navigation
            st.markdown("## 📑 Menu")
            
            pages = ["🎨 Create Job", "🖼️ Generate Variants", "👀 View Assets", 
                     "📦 Create Products", "📱 Social Media", "📸 Stock Platforms", 
                     "📊 Analytics", "📁 Collections", "⏰ Scheduler", "✏️ Editor", 
                     "✂️ Crop Tester"]
            
            current_index = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0
            
            page = st.radio(
                "Vyberte stránku:",
                pages,
                index=current_index
            )
            
            if page != st.session_state.current_page:
                st.session_state.current_page = page
                save_session()
                st.rerun()
            
            st.markdown("---")
            
            # Image display mode (only in classic)
            st.markdown("## 🖼️ Zobrazení")
            
            if 'image_display_mode' not in st.session_state:
                st.session_state.image_display_mode = 'safe'
            
            mode = st.radio(
                "Obrázky:",
                options=['safe', 'native'],
                format_func=lambda x: {
                    'safe': '🔒 Bezpečný',
                    'native': '🖼️ Původní'
                }[x],
                index=0 if st.session_state.image_display_mode == 'safe' else 1
            )
            
            if mode != st.session_state.image_display_mode:
                st.session_state.image_display_mode = mode
                st.rerun()
        
        else:
            # PIPELINE MODE: Stage navigation
            render_pipeline_sidebar()
        
        st.markdown("---")
        st.markdown("## 🎯 Quick Actions")

        if st.button("🔄 Reset Session", use_container_width=True):
            # Clear saved session file
            clear_saved_session()
            
            # Reset session state
            st.session_state.job_id = None
            st.session_state.assets = []
            st.session_state.products = []
            st.session_state.logger = StreamlitLogger()
            st.session_state.current_page = "🎨 Create Job"
            st.rerun()

        if st.button("📊 View Stats", use_container_width=True):
            from artomate.core.job_manager import JobManager
            manager = JobManager()
            stats = manager.get_job_stats()
            st.json(stats)

        st.markdown("---")
        st.markdown("### 📝 Current Session")
        st.write(f"**Job ID:** {st.session_state.job_id or 'None'}")
        st.write(f"**Assets:** {len(st.session_state.assets)}")
        st.write(f"**Products:** {len(st.session_state.products)}")

    # Main content based on selection
    # Main content area - render based on UI mode
    if st.session_state.ui_mode == 'pipeline':
        # PIPELINE MODE: Render current stage
        render_pipeline_mode()
    else:
        # CLASSIC MODE: Render selected page
        page = st.session_state.current_page
        
        if page == "🎨 Create Job":
            create_job_ui()
        elif page == "🖼️ Generate Variants":
            generate_variants_ui()
        elif page == "👀 View Assets":
            display_assets_ui()
        elif page == "📦 Create Products":
            create_products_ui()
        elif page == "📱 Social Media":
            publish_social_ui()
        elif page == "📸 Stock Platforms":
            submit_stock_ui()
        elif page == "📊 Analytics":
            analytics_dashboard_ui()
        elif page == "📁 Collections":
            collections_ui()
        elif page == "⏰ Scheduler":
            scheduler_ui()
        elif page == "✏️ Editor":
            image_editor_ui()
        elif page == "✂️ Crop Tester":
            crop_tester_ui()

    # Console log (always visible at bottom)
    st.markdown("---")
    display_console()


if __name__ == "__main__":
    main()
