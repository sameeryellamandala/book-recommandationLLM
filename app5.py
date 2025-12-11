import streamlit as st
import os 
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import json
load_dotenv()

st.set_page_config(page_title="Book Recommendation App", page_icon="📚")
st.title("📚 LLM Book Recommendation App")

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a book recommendation expert. "
     "Return ONLY the best and most popular books within the user's max budget. "
     "Always respond with EXACTLY 10 books in clean JSON."
    ),

    ("user",
     "Genre: {genre}\n"
     "Maximum budget: {max_cost}\n\n"
     "Give me 10 books in this genre that cost LESS THAN OR EQUAL to the given budget.\n"
     "Return the output strictly in this JSON format:\n"
     "[\n"
     "  {{\n"
     "    \"title\": \"string\",\n"
     "    \"author\": \"string\",\n"
     "    \"description\": \"string\",\n"
     "    \"reviews\": \"string\",\n"
     "    \"cost\": \"string\",\n"
     "    \"purchase_link\": \"string\"\n"
     "  }}\n"
     "]"
    )
])

api_key = st.sidebar.text_input( "enter groq api-key here" , value = "" , type= "password")

if not api_key:
    st.write(" Enter Groq API key first")
    st.stop()


try:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key
    )
    llm.invoke("ping")   # test call
except Exception as e:
    st.error("❌ Invalid API Key. Please provide a valid Groq API key.")
    st.stop()

chain = prompt | llm | StrOutputParser()


genre = st.text_input("Enter the book genre you want:")
cost = st.text_input("Enter the max price in dollars that you can afford:")

if st.button("🔍 Search"):
    if not genre or not cost:
        st.error("❗ Please enter all details first.")
    else:
        with st.spinner("📚 Fetching top book recommendations..."):
            result = chain.invoke({"genre": genre, "max_cost": cost})
        try:
            books = json.loads(result.strip())
            for book in books:
                st.markdown(f"""
<div style="padding: 15px; border-radius: 10px; border: 1px solid #444; margin-bottom: 12px;">
    <h3>{book.get('title', '')}</h3>
    <p><b>Author:</b> {book.get('author', '')}</p>
    <p><b>Description:</b> {book.get('description', '')}</p>
    <p><b>Reviews:</b> {book.get('reviews', '')}</p>
    <p><b>Cost:</b> ₹{book.get('cost', '')}</p>
    <a href="{book.get('purchase_link', '#')}" target="_blank">
        📚 Buy Now
    </a>
</div>
""", unsafe_allow_html=True)
        except Exception as e:
            st.error("❗ Model did not return valid JSON. Try again.")
