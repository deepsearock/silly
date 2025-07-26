import streamlit as st
import httpx

st.set_page_config(page_title="PromptCode", layout="wide")
st.title("🎩 PromptCode: Vibe Coding Playground")

# Available challenges
CHALLENGES = {1: 'Palindrome Check'}

ch_id = st.selectbox("Choose Challenge", list(CHALLENGES.keys()), format_func=lambda x: f"{x}: {CHALLENGES[x]}")
prompt = st.text_area("Enter your prompt (no code!)", height=150)

if st.button("Submit Prompt"):
    if not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        with st.spinner("Vibing with the AI..."):
            try:
                resp = httpx.post(
                    "http://localhost:8000/prompt",
                    json={"challenge_id": ch_id, "prompt_text": prompt}
                )
                resp.raise_for_status()
                data = resp.json()
                st.subheader("🧑‍💻 Generated Code")
                st.code(data['code'], language='python')
                st.subheader("🧪 Test Results")
                if data['results']['returncode'] == 0:
                    st.success("All tests passed! 🎉")
                else:
                    st.error("Some tests failed")
                st.text(data['results']['output'])
                st.subheader("📊 Your Vibe Score")
                st.metric("Score", data['score'])
            except Exception as e:
                st.error(f"Error: {e}")