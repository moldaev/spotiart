import streamlit as st
from PIL import Image, ImageDraw
import random

st.set_page_config(page_title="Visualization Window", layout="wide")

# Session state to track current visualization
if "viz_index" not in st.session_state:
    st.session_state.viz_index = 0

# List of placeholder visualizations (replace with your own)
def render_viz_1():
    img = Image.new("RGB", (800, 600), (30, 30, 60))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Visualization 1", fill=(255, 255, 255))
    return img

def render_viz_2():
    img = Image.new("RGB", (800, 600), (60, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Visualization 2", fill=(255, 255, 255))
    return img

def render_viz_3():
    img = Image.new("RGB", (800, 600), (30, 60, 30))
    draw = ImageDraw.Draw(img)
    draw.text((50, 50), "Visualization 3", fill=(255, 255, 255))
    return img

visualizations = [render_viz_1, render_viz_2, render_viz_3]

# Main window
st.markdown(
    """
    <style>
    .main { padding-top: 0rem; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Spotiart")

# Display current visualization
viz_func = visualizations[st.session_state.viz_index % len(visualizations)]
image = viz_func()
st.image(image, use_column_width=True)

# Button to switch visualization
if st.button("🔄 Change Visualization"):
    st.session_state.viz_index += 1
    st.experimental_rerun()
