"""
Demo: Correct implementation of random selection buttons with multiselect in Streamlit
This demonstrates the CORRECT way to update multiselect widgets programmatically.
"""

import streamlit as st
import random

st.title("🎲 Streamlit Multiselect with Random Selection - WORKING VERSION")

st.markdown("""
**The Key Insight**: Don't use separate session state variables with the `default` parameter.
Instead, use the widget's `key` parameter as the ONLY source of state, and modify it directly.
""")

# Sample data
ANIMALS = ["Cat", "Dog", "Fox", "Owl", "Deer", "Bear", "Rabbit", "Squirrel", "Hedgehog", "Koala"]
STYLES = ["Minimalist", "Japandi", "Watercolor", "Sketch", "Abstract", "Realistic", "Cartoon", "3D Render"]
THEMES = ["Christmas", "Winter Snow", "Spring Blossom", "Summer Beach", "Autumn Leaves", "Halloween"]

# ✅ CORRECT: Initialize the widget keys directly (not separate variables!)
if 'animals_select' not in st.session_state:
    st.session_state.animals_select = ["Cat", "Dog"]
if 'styles_select' not in st.session_state:
    st.session_state.styles_select = ["Minimalist", "Japandi"]
if 'themes_select' not in st.session_state:
    st.session_state.themes_select = ["Christmas", "Winter Snow"]

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🐾 Animals")
    col_animal1, col_animal2 = st.columns([3, 1])
    
    with col_animal2:
        if st.button("🎲 Random", key="random_animals", help="Select random animals"):
            count = random.randint(3, 7)
            # ✅ CORRECT: Modify the widget's key directly
            st.session_state.animals_select = random.sample(ANIMALS, count)
            st.rerun()
    
    with col_animal1:
        # ✅ CORRECT: No default parameter needed! The key controls everything
        animals = st.multiselect(
            "Select animals",
            ANIMALS,
            key="animals_select",  # This is the source of truth
            help="Choose one or more animals"
        )
    
    st.markdown("### 🎨 Art Styles")
    col_style1, col_style2 = st.columns([3, 1])
    
    with col_style2:
        if st.button("🎲 Random", key="random_styles", help="Select random styles"):
            count = random.randint(2, 5)
            st.session_state.styles_select = random.sample(STYLES, count)
            st.rerun()
    
    with col_style1:
        styles = st.multiselect(
            "Select styles",
            STYLES,
            key="styles_select",
            help="Choose one or more styles"
        )

with col2:
    st.markdown("### 🌄 Themes")
    col_theme1, col_theme2 = st.columns([3, 1])
    
    with col_theme2:
        if st.button("🎲 Random", key="random_themes", help="Select random themes"):
            count = random.randint(2, 5)
            st.session_state.themes_select = random.sample(THEMES, count)
            st.rerun()
    
    with col_theme1:
        themes = st.multiselect(
            "Select themes",
            THEMES,
            key="themes_select",
            help="Choose one or more themes"
        )
    
    st.markdown("### 🔄 Bulk Actions")
    
    if st.button("🎲 Randomize All", type="primary", use_container_width=True):
        st.session_state.animals_select = random.sample(ANIMALS, random.randint(3, 7))
        st.session_state.styles_select = random.sample(STYLES, random.randint(2, 5))
        st.session_state.themes_select = random.sample(THEMES, random.randint(2, 5))
        st.rerun()
    
    if st.button("❌ Clear All", use_container_width=True):
        st.session_state.animals_select = []
        st.session_state.styles_select = []
        st.session_state.themes_select = []
        st.rerun()

st.markdown("---")

# Display current selections
st.markdown("### 📊 Current Selections")
col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"**Animals ({len(st.session_state.animals_select)})**")
    for animal in st.session_state.animals_select:
        st.write(f"• {animal}")

with col2:
    st.info(f"**Styles ({len(st.session_state.styles_select)})**")
    for style in st.session_state.styles_select:
        st.write(f"• {style}")

with col3:
    st.info(f"**Themes ({len(st.session_state.themes_select)})**")
    for theme in st.session_state.themes_select:
        st.write(f"• {theme}")

# Show the pattern comparison
with st.expander("🔍 See the Code Pattern Comparison"):
    st.markdown("""
    ### ❌ WRONG Pattern (Your Current Code)
    ```python
    # Separate variable
    if 'selected_animals' not in st.session_state:
        st.session_state.selected_animals = ["Cat", "Dog"]
    
    # Button modifies separate variable
    if st.button("🎲", key="random_animals"):
        st.session_state.selected_animals = random.sample(ANIMALS, count)
        st.rerun()
    
    # Widget uses default parameter
    animals = st.multiselect(
        "Select animals",
        ANIMALS,
        default=st.session_state.selected_animals,  # ❌ Ignored after first render!
        key="animals_select"
    )
    st.session_state.selected_animals = animals  # ❌ Unnecessary sync
    ```
    
    **Why it fails**: The `default` parameter is only used on the first render when the widget 
    is created. After that, the widget maintains its own state via `st.session_state["animals_select"]` 
    (the key), and changes to `st.session_state.selected_animals` are ignored!
    
    ---
    
    ### ✅ CORRECT Pattern (This Demo)
    ```python
    # Initialize the widget's key directly
    if 'animals_select' not in st.session_state:
        st.session_state.animals_select = ["Cat", "Dog"]
    
    # Button modifies the widget's key directly
    if st.button("🎲", key="random_animals"):
        st.session_state.animals_select = random.sample(ANIMALS, count)  # ✅ Direct modification
        st.rerun()
    
    # Widget controlled by its key
    animals = st.multiselect(
        "Select animals",
        ANIMALS,
        key="animals_select"  # ✅ This is the source of truth
    )
    # No sync needed - the value is already in st.session_state.animals_select
    ```
    
    **Why it works**: The widget stores its state in `st.session_state["animals_select"]` (via the key). 
    When you modify this directly and rerun, the widget picks up the new value. Simple and clean!
    """)

st.markdown("---")
st.caption("💡 Tip: Click the random buttons and see the multiselect values update immediately!")
