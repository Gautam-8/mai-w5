from langchain_community.agent_toolkits.sql.base import create_sql_agent
import streamlit as st
from dotenv import load_dotenv
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.chat_models import init_chat_model

# Load environment
load_dotenv()

# Streamlit UI setup
st.set_page_config(page_title="🛒 Quick Commerce Deals")
st.title("🛍️ SQL Agent for Quick Commerce")

# 1. Initialize the LLM
llm = init_chat_model("gemini-1.5-flash", model_provider="google_genai")

# 2. Load multiple DBs (you can add more)
zeptodb = SQLDatabase.from_uri("sqlite:///zepto.db")
blinkitdb = SQLDatabase.from_uri("sqlite:///blinkit.db")
instamartdb = SQLDatabase.from_uri("sqlite:///instasmart.db")

# 3. Create toolkits for each DB
zepto_toolkit = SQLDatabaseToolkit(db=zeptodb, llm=llm)
blinkit_toolkit = SQLDatabaseToolkit(db=blinkitdb, llm=llm)
instamart_toolkit = SQLDatabaseToolkit(db=instamartdb, llm=llm)

# 4. Combine all tools
all_tools = zepto_toolkit.get_tools() + blinkit_toolkit.get_tools() + instamart_toolkit.get_tools()

# 5. Create SQL agent with all tools
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=zepto_toolkit,  # just needs one as primary
    verbose=True,
)

# 6. User query input
query = st.text_input("🔍 Ask a question (e.g., Cheapest onions across platforms):")
if query:
    with st.spinner("Thinking..."):
        try:
            result = agent_executor.run(query)
            st.success("✅ Result:")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
