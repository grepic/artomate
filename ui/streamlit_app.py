"""Streamlit UI for Artomate with real-time console logging."""

import streamlit as st
import sys
from io import StringIO
from pathlib import Path
from datetime import datetime
from PIL import Image
import time

# Configure page
st.set_page_config(
    page_title="Artomate - Content to Commerce",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .log-container {
        background-color: #0e1117;
        color: #00ff00;
        padding: 1rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', monospace;
        max-height: 500px;
        overflow-y: auto;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitLogger:
    """Capture logs for Streamlit display."""

    def __init__(self):
        self.logs = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        return log_entry


# Initialize session state
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

    col1, col2 = st.columns(2)

    with col1:
        theme = st.text_input("Theme", placeholder="e.g., minimalist cat")
        style = st.selectbox("Style", [
            "minimalist", "japandi", "boho", "vintage", "modern",
            "watercolor", "geometric", "abstract", "rustic", "scandinavian"
        ])
        niche = st.selectbox("Niche", [
            "wall-art", "apparel", "home-decor", "stationery", "accessories"
        ])

    with col2:
        keywords = st.text_area("Keywords (one per line)", placeholder="cat\nminimal\nzen")
        priority = st.slider("Priority", 1, 10, 5)
        variant_count = st.number_input("Number of variants", 1, 12, 12)

    create_btn = st.button("🚀 Create Job", type="primary", use_container_width=True)

    if create_btn and theme:
        with st.spinner("Creating job..."):
            try:
                from artomate.core.job_manager import JobManager

                st.session_state.logger.log(f"Creating job: {theme}", "INFO")

                manager = JobManager()
                keywords_list = [k.strip() for k in keywords.split('\n') if k.strip()]

                job = manager.create_job(
                    theme=theme,
                    style=style,
                    niche=niche,
                    keywords=keywords_list,
                    priority=priority
                )

                st.session_state.job_id = job.id
                st.session_state.logger.log(f"✓ Job {job.id} created successfully", "SUCCESS")

                st.markdown(f'<div class="success-box">✓ Job {job.id} created!</div>',
                           unsafe_allow_html=True)

            except Exception as e:
                st.session_state.logger.log(f"✗ Job creation failed: {e}", "ERROR")
                st.markdown(f'<div class="error-box">✗ Error: {e}</div>',
                           unsafe_allow_html=True)


def generate_variants_ui():
    """Generate image variants UI."""
    st.markdown("## 🎨 Generate Image Variants")

    if not st.session_state.job_id:
        st.warning("⚠️ Create a job first!")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"Job ID: {st.session_state.job_id}")
        variant_count = st.number_input("Variants to generate", 1, 12, 12, key="gen_variants")

    with col2:
        generate_btn = st.button("🎨 Generate", type="primary", use_container_width=True)

    if generate_btn:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            from artomate.core.job_manager import JobManager
            from artomate.workers.enhanced_image_generator import EnhancedImageGenerator

            manager = JobManager()
            job = manager.get_job(st.session_state.job_id)

            st.session_state.logger.log(f"Starting generation for job {job.id}", "INFO")
            status_text.text("🎨 Initializing AI generator...")

            generator = EnhancedImageGenerator()

            # Generate variants
            assets = []
            for i in range(variant_count):
                progress = (i + 1) / variant_count
                progress_bar.progress(progress)
                status_text.text(f"🎨 Generating variant {i+1}/{variant_count}...")

                st.session_state.logger.log(f"Generating variant {i+1}/{variant_count}", "INFO")

                variant_assets = generator.generate_monthly_variant(job, month_index=i)
                assets.extend(variant_assets)

                st.session_state.logger.log(f"✓ Variant {i+1} generated", "SUCCESS")

            st.session_state.assets = assets
            st.session_state.logger.log(f"✓ Generated {len(assets)} total assets", "SUCCESS")

            progress_bar.progress(1.0)
            status_text.text(f"✓ Generated {len(assets)} variants!")

            st.success(f"✓ Generated {len(assets)} image variants!")

        except Exception as e:
            st.session_state.logger.log(f"✗ Generation failed: {e}", "ERROR")
            st.error(f"✗ Error: {e}")


def display_assets_ui():
    """Display generated assets."""
    st.markdown("## 🖼️ Generated Assets")

    if not st.session_state.assets:
        st.info("No assets generated yet. Generate variants first!")
        return

    cols = st.columns(4)

    for idx, asset in enumerate(st.session_state.assets[:12]):  # Show first 12
        with cols[idx % 4]:
            try:
                img = Image.open(asset.storage_path)
                st.image(img, caption=f"Variant {idx+1}", use_container_width=True)
                st.caption(f"{asset.width}x{asset.height}")
            except:
                st.error(f"Failed to load asset {asset.id}")


def create_products_ui():
    """Create Printify products UI."""
    st.markdown("## 🏭 Create Products")

    if not st.session_state.assets:
        st.warning("⚠️ Generate assets first!")
        return

    product_types = st.multiselect(
        "Select product types",
        ["tshirt", "poster_12x18", "poster_18x24", "mug", "hoodie", "canvas_16x20"],
        default=["tshirt", "poster_18x24"]
    )

    create_products_btn = st.button("🏭 Create All Products", type="primary")

    if create_products_btn and product_types:
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            from artomate.core.job_manager import JobManager
            from artomate.workers.printify_worker import PrintifyWorker

            manager = JobManager()
            job = manager.get_job(st.session_state.job_id)

            st.session_state.logger.log(f"Creating products for {len(st.session_state.assets)} assets", "INFO")

            printify = PrintifyWorker()
            all_products = []

            total = len(st.session_state.assets) * len(product_types)
            current = 0

            for asset in st.session_state.assets:
                for product_type in product_types:
                    current += 1
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Creating {product_type} for variant {asset.id}...")

                    st.session_state.logger.log(f"Creating {product_type} for asset {asset.id}", "INFO")

                    product = printify.create_product(job, asset, product_type)
                    all_products.append(product)

                    st.session_state.logger.log(f"✓ Created {product_type} #{product.id}", "SUCCESS")

            st.session_state.products = all_products
            st.session_state.logger.log(f"✓ Created {len(all_products)} total products", "SUCCESS")

            progress_bar.progress(1.0)
            st.success(f"✓ Created {len(all_products)} products!")

        except Exception as e:
            st.session_state.logger.log(f"✗ Product creation failed: {e}", "ERROR")
            st.error(f"✗ Error: {e}")


def publish_social_ui():
    """Publish to social media UI."""
    st.markdown("## 📱 Social Media Publishing")

    if not st.session_state.assets:
        st.warning("⚠️ Generate assets first!")
        return

    platforms = st.multiselect(
        "Select platforms",
        ["Instagram Carousel", "Instagram Reels", "TikTok", "YouTube Shorts"],
        default=["Instagram Carousel"]
    )

    publish_btn = st.button("📱 Publish to Social", type="primary")

    if publish_btn and platforms:
        progress_bar = st.progress(0)

        try:
            from artomate.core.job_manager import JobManager
            from artomate.workers.social_media_publisher import SocialMediaPublisher
            from artomate.workers.video_generator import VideoGenerator
            from artomate.db.models import SocialPlatform

            manager = JobManager()
            job = manager.get_job(st.session_state.job_id)

            social = SocialMediaPublisher()
            video_gen = VideoGenerator()

            posts = []

            # Instagram Carousel with all 12 images
            if "Instagram Carousel" in platforms:
                st.session_state.logger.log("Creating Instagram carousel post", "INFO")

                post = social.create_post(
                    job=job,
                    platform=SocialPlatform.INSTAGRAM,
                    image_assets=st.session_state.assets[:10]  # IG limit 10
                )
                posts.append(post)

                st.session_state.logger.log("✓ Instagram carousel created", "SUCCESS")
                progress_bar.progress(0.25)

            # Create Reels/Shorts for each variant
            if any(p in platforms for p in ["Instagram Reels", "TikTok", "YouTube Shorts"]):
                st.session_state.logger.log("Creating videos for social media", "INFO")

                for idx, asset in enumerate(st.session_state.assets[:3]):  # First 3 for demo
                    video = video_gen.create_reel(
                        job=job,
                        assets=[asset],
                        duration=5,
                        style="ken_burns"
                    )

                    if "Instagram Reels" in platforms:
                        post = social.create_post(job, SocialPlatform.INSTAGRAM, video_asset=video)
                        posts.append(post)

                    st.session_state.logger.log(f"✓ Created video {idx+1}", "SUCCESS")
                    progress_bar.progress(0.5 + (idx+1) * 0.16)

            st.session_state.logger.log(f"✓ Created {len(posts)} social posts", "SUCCESS")
            st.success(f"✓ Created {len(posts)} social media posts!")

        except Exception as e:
            st.session_state.logger.log(f"✗ Social publishing failed: {e}", "ERROR")
            st.error(f"✗ Error: {e}")


def submit_stock_ui():
    """Submit to stock platforms UI."""
    st.markdown("## 📸 Stock Platform Submission")

    if not st.session_state.assets:
        st.warning("⚠️ Generate assets first!")
        return

    platforms = st.multiselect(
        "Select stock platforms",
        ["Shutterstock", "Adobe Stock"],
        default=["Shutterstock", "Adobe Stock"]
    )

    submit_btn = st.button("📸 Submit to Stock", type="primary")

    if submit_btn and platforms:
        progress_bar = st.progress(0)

        try:
            from artomate.core.job_manager import JobManager
            from artomate.workers.stock_platforms import StockPlatformWorker

            manager = JobManager()
            job = manager.get_job(st.session_state.job_id)

            stock = StockPlatformWorker()
            submissions = []

            total = len(st.session_state.assets) * len(platforms)
            current = 0

            for asset in st.session_state.assets:
                for platform in platforms:
                    current += 1
                    progress = current / total
                    progress_bar.progress(progress)

                    platform_key = platform.lower().replace(" ", "_")

                    st.session_state.logger.log(
                        f"Preparing {platform} submission for asset {asset.id}", "INFO"
                    )

                    submission = stock.prepare_submission(asset, job, platform_key)
                    outbox_path = stock.create_outbox_file(submission)
                    submissions.append(outbox_path)

                    st.session_state.logger.log(f"✓ Created {platform} submission", "SUCCESS")

            st.session_state.logger.log(
                f"✓ Created {len(submissions)} stock submissions", "SUCCESS"
            )
            st.success(f"✓ Created {len(submissions)} stock submissions!")

        except Exception as e:
            st.session_state.logger.log(f"✗ Stock submission failed: {e}", "ERROR")
            st.error(f"✗ Error: {e}")


def main():
    """Main UI."""

    # Header
    st.markdown('<div class="main-header">🎨 Artomate - Content to Commerce</div>',
                unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Quick Actions")

        if st.button("🔄 Reset Session", use_container_width=True):
            st.session_state.job_id = None
            st.session_state.assets = []
            st.session_state.products = []
            st.session_state.logger = StreamlitLogger()
            st.rerun()

        if st.button("📊 View Stats", use_container_width=True):
            from artomate.core.job_manager import JobManager
            manager = JobManager()
            stats = manager.get_job_stats()
            st.json(stats)

        st.markdown("---")
        st.markdown("### 📝 Current Session")
        st.write(f"Job ID: {st.session_state.job_id or 'None'}")
        st.write(f"Assets: {len(st.session_state.assets)}")
        st.write(f"Products: {len(st.session_state.products)}")

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1️⃣ Create Job",
        "2️⃣ Generate Variants",
        "3️⃣ View Assets",
        "4️⃣ Create Products",
        "5️⃣ Social Media",
        "6️⃣ Stock Platforms"
    ])

    with tab1:
        create_job_ui()

    with tab2:
        generate_variants_ui()

    with tab3:
        display_assets_ui()

    with tab4:
        create_products_ui()

    with tab5:
        publish_social_ui()

    with tab6:
        submit_stock_ui()

    # Console log (always visible)
    st.markdown("---")
    display_console()

    # Auto-refresh console
    if st.session_state.logger.logs:
        time.sleep(0.1)
        st.rerun()


if __name__ == "__main__":
    main()
