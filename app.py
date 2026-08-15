import streamlit as st
from google import genai

st.set_page_config(page_title="Bistro AI Assistant", page_icon="🍽️")

st.title("🍽️ Bistro AI Customer Assistant")
st.caption("Ask about our menu, dietary options, or daily specials!")

# Simulated Menu Knowledge Base
MENU_CONTEXT = """
Menu & Information:
1. Margherita Pizza ($12) - Classic tomato sauce, fresh mozzarella, basil (Vegetarian).
2. Truffle Mushroom Pasta ($16) - Creamy wild mushroom sauce, fettuccine, parmesan (Vegetarian).
3. Grilled Salmon ($22) - Atlantic salmon, lemon-herb butter, roasted asparagus (Gluten-Free).
4. Vegan Buddha Bowl ($14) - Quinoa, roasted chickpeas, avocado, tahini dressing (Vegan, Gluten-Free).
5. Tiramisu ($8) - Espresso-soaked ladyfingers, mascarpone cream.

Opening Hours: 11:00 AM - 10:00 PM daily.
Location: 100 Main Street.
"""

# Gemini API setup (reads from Streamlit Secrets or sidebar input)
api_key = st.sidebar.text_input("Enter Gemini API Key (optional if configured in secrets):", type="password")

if not api_key:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Welcome to Bistro AI. How can I help you with our menu today?"}
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask a question about our menu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    if not api_key:
        with st.chat_message("assistant"):
            st.error("Please enter a Gemini API Key in the sidebar to generate a live response.")
    else:
        try:
            client = genai.Client(api_key=api_key)
            system_instruction = f"""
            You are a polite, helpful customer service assistant for our restaurant.
            Use ONLY the following menu context to answer user questions:
            {MENU_CONTEXT}
            If an item or question cannot be answered from the menu context, politely let the customer know.
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=dict(system_instruction=system_instruction)
            )
            with st.chat_message("assistant"):
                st.write(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error: {e}")
