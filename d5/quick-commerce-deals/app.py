import sqlite3
import random
import os
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase

# ---------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS platform (
        id INTEGER PRIMARY KEY, name TEXT UNIQUE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS product (
        id INTEGER PRIMARY KEY, name TEXT UNIQUE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS product_price (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        platform_id INTEGER,
        price REAL,
        discount_percent REAL,
        availability TEXT,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(product_id) REFERENCES product(id),
        FOREIGN KEY(platform_id) REFERENCES platform(id)
    )''')

    platforms = ['Blinkit', 'Zepto', 'Instamart', 'BigBasket Now']
    products = ['Onion', 'Tomato', 'Apple', 'Milk']

    for p in platforms:
        cursor.execute("INSERT OR IGNORE INTO platform (name) VALUES (?)", (p,))
    for prod in products:
        cursor.execute("INSERT OR IGNORE INTO product (name) VALUES (?)", (prod,))

    cursor.execute("DELETE FROM product_price")
    conn.commit()

    for prod_id in range(1, len(products)+1):
        for plat_id in range(1, len(platforms)+1):
            price = round(random.uniform(10, 100), 2)
            discount = random.choice([0, 10, 20, 30])
            availability = random.choice(['In Stock', 'Out of Stock'])
            cursor.execute('''INSERT INTO product_price
                (product_id, platform_id, price, discount_percent, availability)
                VALUES (?, ?, ?, ?, ?)''',
                (prod_id, plat_id, price, discount, availability))

    conn.commit()
    conn.close()

# ---------- LangChain SQL Agent Setup ----------
def get_sql_agent():
    db = SQLDatabase.from_uri("sqlite:///database.db")
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=os.getenv("OPENAI_API_KEY"))
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    return create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

# ---------- Streamlit UI ----------
def main():
    st.set_page_config(page_title="Quick Commerce Deals", layout="wide")
    st.title("🛒 Quick Commerce Deals (v1)")

    st.markdown("Ask questions like:")
    st.markdown("- Cheapest onions right now?")
    st.markdown("- Products with 30%+ discount on Blinkit")
    st.markdown("- Compare fruit prices between Zepto and Instamart")

    query = st.text_input("💬 Ask a natural language query")

    if query:
        agent = get_sql_agent()
        with st.spinner("Thinking..."):
            try:
                result = agent.run(query)
                st.success(result)
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    init_db()
    main()
