"""
Authentication module for Daily Habit Tracker
Handles user login and session management
"""

import os
import streamlit as st
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

# Load environment variables
load_dotenv()


def get_all_users() -> Dict[str, Dict]:
    """
    Load all users from environment variables
    Returns dict: {username: {password, display_name, is_admin}}
    """
    users = {}
    
    # Add admin user
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    users[admin_username] = {
        "password": admin_password,
        "display_name": "Admin 👑",
        "is_admin": True
    }
    
    # Add regular users (USER_1, USER_2, etc.)
    i = 1
    while True:
        username = os.getenv(f"USER_{i}_USERNAME")
        if not username:
            break
        
        password = os.getenv(f"USER_{i}_PASSWORD", "")
        display_name = os.getenv(f"USER_{i}_DISPLAYNAME", username)
        
        users[username] = {
            "password": password,
            "display_name": display_name,
            "is_admin": False
        }
        i += 1
    
    return users


def authenticate(username: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Authenticate user credentials
    Returns (success, user_info)
    """
    users = get_all_users()
    
    if username in users and users[username]["password"] == password:
        return True, {
            "username": username,
            "display_name": users[username]["display_name"],
            "is_admin": users[username]["is_admin"]
        }
    
    return False, None


def get_all_usernames() -> List[str]:
    """Get list of all usernames (excluding admin)"""
    users = get_all_users()
    return [u for u in users.keys() if not users[u]["is_admin"]]


def get_user_display_name(username: str) -> str:
    """Get display name for a username"""
    users = get_all_users()
    if username in users:
        return users[username]["display_name"]
    return username


def login_page():
    """Render login page"""
    st.set_page_config(
        page_title="Daily Habit Tracker - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    # Custom CSS for login page
    st.markdown("""
        <style>
        .login-header {
            text-align: center;
            padding: 2rem 0;
        }
        .login-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            font-size: 1.1rem;
            color: #666;
        }
        .login-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 16px;
            margin: 2rem auto;
            max-width: 400px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="login-header">
            <div class="login-title">✅ Daily Habit Tracker</div>
            <div class="login-subtitle">Track your habits, achieve your goals!</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if username and password:
                    success, user_info = authenticate(username, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_info
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.caption("🔒 Contact admin for access credentials")


def logout():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[Dict]:
    """Get current logged in user"""
    return st.session_state.get("user", None)


def is_admin() -> bool:
    """Check if current user is admin"""
    user = get_current_user()
    return user.get("is_admin", False) if user else False
