import streamlit as st
from supabase import create_client, Client

# Use wide layout
st.set_page_config(
    layout="wide",
    page_title="The Combine"
)

# Function to initialise a Supabase DB connection from details stored in secrets
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Create Supabase DB connection
supabase = init_connection()

# Function to grab everything in the Supabase table the_combine
def run_query_main_table():
    return supabase.table("the_combine").select("*").execute()

# Title for app
st.title("Welcome to The Combine - the hub for HSMA Lambda Project Proposals")

# Set up main sections of the app
col_left, col_right = st.columns([0.5,0.5])

