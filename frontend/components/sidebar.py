
import streamlit as st

def render_sidebar():

    st.sidebar.title("🚀 My Application")
    st.sidebar.caption("Navigation Menu")

    menu_options = [
        "🏠 Dashboard",
        "📊 Analytics",
        "📁 Projects",
        "👥 Users",
        "⚙️ Settings"
    ]

    selected = st.sidebar.radio(
        "Navigate",
        menu_options,
        label_visibility="collapsed"
    )

    # Remove emoji from selected menu
    return selected.split(" ", 1)[1]
