"""
Medical AI Chatbot - Streamlit Frontend

A conversational interface for the dental patient simulation chatbot.
Provides:
- Session creation with pathology selection
- Real-time chat interaction
- Conversation history display
- Session management (reset, delete)
"""

import streamlit as st
import requests
from typing import Optional, Dict, List


# ============================================
# Configuration
# ============================================

API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Medical AI Chatbot",
    page_icon="🦷",
    layout="centered",
    initial_sidebar_state="expanded"
)


# ============================================
# API Client
# ============================================

class APIClient:
    """Client for communicating with the backend API."""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.timeout = 60  # Longer timeout for AI generation

    def health_check(self) -> Dict:
        """Check API health status."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.json()
        except requests.RequestException:
            return {"status": "unavailable", "model_loaded": False}

    def get_pathologies(self) -> List[Dict]:
        """Get list of available pathologies."""
        try:
            response = requests.get(f"{self.base_url}/chats/pathologies/list", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("pathologies", [])
        except requests.RequestException:
            return []

    def create_chat(self, pathology: Optional[str] = None) -> Optional[Dict]:
        """Create a new chat session."""
        try:
            payload = {"pathology": pathology} if pathology else {}
            response = requests.post(
                f"{self.base_url}/chats",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to create chat: {e}")
            return None

    def send_message(
        self,
        chat_id: str,
        message: str,
        max_tokens: int = 100,
        temperature: float = 0.4
    ) -> Optional[Dict]:
        """Send a message and get the patient's response."""
        try:
            response = requests.post(
                f"{self.base_url}/chats/{chat_id}/message",
                json={
                    "message": message,
                    "max_new_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to send message: {e}")
            return None

    def get_chat(self, chat_id: str) -> Optional[Dict]:
        """Get chat details and history."""
        try:
            response = requests.get(f"{self.base_url}/chats/{chat_id}", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def reset_chat(self, chat_id: str) -> Optional[Dict]:
        """Reset a chat session."""
        try:
            response = requests.post(f"{self.base_url}/chats/{chat_id}/reset", timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to reset chat: {e}")
            return None

    def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat session."""
        try:
            response = requests.delete(f"{self.base_url}/chats/{chat_id}", timeout=10)
            return response.status_code == 204
        except requests.RequestException:
            return False

    def list_chats(self) -> List[Dict]:
        """List all chat sessions."""
        try:
            response = requests.get(f"{self.base_url}/chats", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("chats", [])
        except requests.RequestException:
            return []


# ============================================
# Session State Management
# ============================================

def init_session_state():
    """Initialize session state variables."""
    if "api_client" not in st.session_state:
        st.session_state.api_client = APIClient()

    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_pathology" not in st.session_state:
        st.session_state.current_pathology = None

    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False
    
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    
    if "diagnosis_stats" not in st.session_state:
        st.session_state.diagnosis_stats = {
            "total_sessions": 0,
            "correct_diagnoses": 0,
            "total_questions": 0,
            "session_history": []
        }


def clear_chat_state():
    """Clear current chat state."""
    st.session_state.current_chat_id = None
    st.session_state.messages = []
    st.session_state.current_pathology = None
    st.session_state.show_answer = False


# ============================================
# UI Components
# ============================================

def render_sidebar():
    """Render the sidebar with controls."""
    with st.sidebar:
        st.title("🦷 Medical AI Chatbot")
        st.caption("Dental Patient Simulation for Training")

        st.divider()

        # Health check
        health = st.session_state.api_client.health_check()
        if health.get("model_loaded"):
            st.success("✅ API Connected & Model Ready")
        elif health.get("status") == "degraded":
            st.warning("⚠️ API Connected, Model Loading...")
        else:
            st.error("❌ API Unavailable")
            st.info("Make sure the backend is running on http://localhost:8000")
            return

        st.divider()

        # New Chat Section
        st.subheader("Start New Simulation")

        pathologies = st.session_state.api_client.get_pathologies()

        pathology_options = ["Random"] + [p["label"] for p in pathologies]
        pathology_keys = [None] + [p["key"] for p in pathologies]

        selected_idx = st.selectbox(
            "Select Pathology",
            range(len(pathology_options)),
            format_func=lambda i: pathology_options[i],
            help="Choose a specific pathology or let the system pick randomly"
        )

        if st.button("🆕 Start New Chat", use_container_width=True):
            selected_pathology = pathology_keys[selected_idx]
            with st.spinner("Creating chat session..."):
                result = st.session_state.api_client.create_chat(selected_pathology)
                if result:
                    st.session_state.current_chat_id = result["chat_id"]
                    st.session_state.current_pathology = result["pathology"]
                    st.session_state.messages = []
                    st.rerun()

        st.divider()

        # Current Session Info
        if st.session_state.current_chat_id:
            st.subheader("Current Session")
            st.text(f"ID: {st.session_state.current_chat_id[:8]}...")
            
            # Show answer toggle
            if st.session_state.show_answer:
                # Get pathology label
                pathologies = st.session_state.api_client.get_pathologies()
                pathology_dict = {p["key"]: p["label"] for p in pathologies}
                pathology_label = pathology_dict.get(
                    st.session_state.current_pathology,
                    st.session_state.current_pathology
                )
                st.success(f"🎯 **Answer:** {pathology_label}")
            else:
                st.text(f"Pathology: Hidden 🔒")
            
            # Show/Hide answer button
            if st.session_state.show_answer:
                if st.button("🔒 Hide Answer", use_container_width=True):
                    st.session_state.show_answer = False
                    st.rerun()
            else:
                if st.button("👁️ Show Answer", use_container_width=True):
                    st.session_state.show_answer = True
                    st.rerun()

            st.divider()

            # Diagnosis submission
            st.subheader("Submit Diagnosis")
            
            pathologies = st.session_state.api_client.get_pathologies()
            pathology_labels = [p["label"] for p in pathologies]
            pathology_keys = [p["key"] for p in pathologies]
            
            selected_diagnosis_idx = st.selectbox(
                "Your diagnosis:",
                range(len(pathology_labels)),
                format_func=lambda i: pathology_labels[i],
                key="diagnosis_select"
            )
            
            if st.button("✅ Submit Diagnosis", use_container_width=True, type="primary"):
                selected_key = pathology_keys[selected_diagnosis_idx]
                is_correct = selected_key == st.session_state.current_pathology
                
                # Update stats
                st.session_state.diagnosis_stats["total_sessions"] += 1
                if is_correct:
                    st.session_state.diagnosis_stats["correct_diagnoses"] += 1
                
                # Count questions asked
                user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
                st.session_state.diagnosis_stats["total_questions"] += user_messages
                
                # Add to history
                pathology_dict = {p["key"]: p["label"] for p in pathologies}
                st.session_state.diagnosis_stats["session_history"].append({
                    "correct_pathology": pathology_dict.get(st.session_state.current_pathology),
                    "your_diagnosis": pathology_labels[selected_diagnosis_idx],
                    "is_correct": is_correct,
                    "questions_asked": user_messages
                })
                
                # Show result
                if is_correct:
                    st.success("🎉 Correct diagnosis!")
                    st.balloons()
                else:
                    correct_label = pathology_dict.get(st.session_state.current_pathology)
                    st.error(f"❌ Incorrect. The correct diagnosis was: **{correct_label}**")
                
                st.session_state.show_answer = True

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Reset", use_container_width=True):
                    result = st.session_state.api_client.reset_chat(
                        st.session_state.current_chat_id
                    )
                    if result:
                        st.session_state.messages = []
                        st.session_state.show_answer = False
                        st.success("Chat reset!")
                        st.rerun()

            with col2:
                if st.button("🗑️ Delete", use_container_width=True):
                    if st.session_state.api_client.delete_chat(
                        st.session_state.current_chat_id
                    ):
                        clear_chat_state()
                        st.rerun()

        st.divider()
        
        # Statistics
        stats = st.session_state.diagnosis_stats
        if stats["total_sessions"] > 0:
            st.subheader("📊 Your Statistics")
            
            accuracy = (stats["correct_diagnoses"] / stats["total_sessions"]) * 100
            avg_questions = stats["total_questions"] / stats["total_sessions"] if stats["total_sessions"] > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Accuracy", f"{accuracy:.1f}%")
                st.metric("Sessions", stats["total_sessions"])
            with col2:
                st.metric("Correct", stats["correct_diagnoses"])
                st.metric("Avg Questions", f"{avg_questions:.1f}")
            
            # Recent history
            with st.expander("📜 Recent History"):
                for i, session in enumerate(reversed(stats["session_history"][-5:])):
                    icon = "✅" if session["is_correct"] else "❌"
                    st.text(f"{icon} {session['your_diagnosis']} ({session['questions_asked']} Q)")
            
            if st.button("🔄 Reset Statistics", use_container_width=True):
                st.session_state.diagnosis_stats = {
                    "total_sessions": 0,
                    "correct_diagnoses": 0,
                    "total_questions": 0,
                    "session_history": []
                }
                st.rerun()

        st.divider()

        # Settings
        with st.expander("⚙️ Generation Settings"):
            st.session_state.max_tokens = st.slider(
                "Max Response Length",
                min_value=50,
                max_value=300,
                value=100,
                step=10
            )
            st.session_state.temperature = st.slider(
                "Creativity",
                min_value=0.1,
                max_value=1.0,
                value=0.4,
                step=0.1,
                help="Lower = more consistent, Higher = more varied"
            )

        st.divider()

        # Disclaimer
        st.caption(
            "⚠️ **Training Tool Only**\n\n"
            "This is a simulated patient for educational purposes. "
            "Do not use for actual diagnosis."
        )


def render_chat_interface():
    """Render the main chat interface."""
    if not st.session_state.current_chat_id:
        # Welcome screen
        st.title("Welcome to the Medical AI Chatbot")
        st.markdown("""
        This application simulates dental patients for diagnosis training.
        
        ### How to use:
        1. **Select a pathology** from the sidebar (or choose Random)
        2. **Click "Start New Chat"** to begin a simulation
        3. **Ask questions** as if you were a dentist examining the patient
        4. **Diagnose the condition** based on the patient's responses
        
        ### Tips:
        - Ask about pain characteristics (location, intensity, triggers)
        - Inquire about duration and progression
        - Ask about medical history
        - The patient won't reveal their diagnosis - you must figure it out!
        
        ---
        *Use the sidebar to begin a new simulation.*
        """)
        return

    # Chat header
    st.title("🦷 Patient Consultation")
    st.caption(f"Session: {st.session_state.current_chat_id[:8]}... | Pathology: Hidden")

    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            with st.chat_message("user", avatar="👨‍⚕️"):
                st.markdown(content)
        elif role == "assistant":
            with st.chat_message("assistant", avatar="🤒"):
                st.markdown(content)

    # Chat input
    if prompt := st.chat_input("Ask the patient a question...", disabled=st.session_state.is_loading):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar="👨‍⚕️"):
            st.markdown(prompt)

        # Get response
        st.session_state.is_loading = True

        with st.chat_message("assistant", avatar="🤒"):
            with st.spinner("Patient is thinking..."):
                response = st.session_state.api_client.send_message(
                    chat_id=st.session_state.current_chat_id,
                    message=prompt,
                    max_tokens=st.session_state.get("max_tokens", 100),
                    temperature=st.session_state.get("temperature", 0.4)
                )

        st.session_state.is_loading = False

        if response:
            reply = response["reply"]
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
        else:
            st.error("Failed to get response. Please try again.")


def render_footer():
    """Render the footer."""
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("Medical AI Chatbot v1.0")
    with col2:
        st.caption(f"Messages: {len(st.session_state.messages)}")
    with col3:
        if st.session_state.current_chat_id:
            st.caption("🟢 Active Session")
        else:
            st.caption("⚪ No Session")


# ============================================
# Main Application
# ============================================

def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    render_chat_interface()
    render_footer()


if __name__ == "__main__":
    main()

