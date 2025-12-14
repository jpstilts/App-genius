import streamlit as st
import openai
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="AppGenius AI", page_icon="⚡", layout="wide")

# --- 2. SECRETS ---
# This is the "Backdoor" you asked for.
MASTER_KEY = "MY_SECRET_FREE_PASS_2025" 

# --- 3. THE BRAIN ---
def get_api_key():
    # Tries to get key from Cloud Secrets, then Local Env, then Admin Input
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        return os.environ.get("OPENAI_API_KEY")

class AgentBrain:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)
    
    def think(self, prompt, code_context=""):
        system_prompt = """
        You are a Senior Python Developer. 
        OUTPUT RULES:
        1. Return ONLY valid Python code. No markdown (```).
        2. Use st.session_state for memory.
        3. Import all necessary libraries (streamlit, pandas, numpy, random, datetime).
        4. If updating code, keep existing features intact.
        """
        user_msg = f"Current Code:\n{code_context}\n\nRequest: {prompt}" if code_context else prompt
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}]
            )
            return True, response.choices[0].message.content.replace("```python", "").replace("```", "").strip()
        except Exception as e:
            return False, str(e)

# --- 4. THE UI ---
def main():
    with st.sidebar:
        st.title("💎 AppGenius Pro")
        license_key = st.text_input("License Key", type="password")
        
        # AUTH CHECK
        is_admin = (license_key == MASTER_KEY)
        is_paid = (license_key == "SUBSCRIPTION_CODE_123")
        
        if is_admin:
            st.success("👑 Master Unlocked")
        elif is_paid:
            st.success("✅ Pro Active")
        else:
            st.warning("🔒 Locked")
            st.info("Subscribe ($4.99/mo) to unlock AI creation.")
            
    # APP LOGIC
    if is_admin or is_paid:
        api_key = get_api_key()
        if not api_key and is_admin:
            api_key = st.text_input("Enter OpenAI API Key (Debug)", type="password")
            
        if not api_key:
            st.error("System Error: API Key missing in Secrets.")
            st.stop()
            
        brain = AgentBrain(api_key)
        if 'code' not in st.session_state: st.session_state['code'] = ""
        
        prompt = st.chat_input("Describe the app you want to build...")
        
        if prompt:
            with st.spinner("🤖 AI is building your app..."):
                success, result = brain.think(prompt, st.session_state['code'])
                if success:
                    st.session_state['code'] = result
                    st.rerun()
                else:
                    st.error(f"Error: {result}")

        if st.session_state['code']:
            st.subheader("📱 Live Preview")
            st.code(st.session_state['code'], language='python')
            st.download_button("Download .py", st.session_state['code'], "app.py")
            
    else:
        st.header("AppGenius AI")
        st.write("Please enter your license key to start building.")

if __name__ == "__main__":
    main()

