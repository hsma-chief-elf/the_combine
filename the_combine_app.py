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

# Function to grab everything in the Supabase table lambda_proposals
def run_query_main_table():
    return supabase.table("lambda_proposals").select("*").execute()

# Title for app
st.title("Welcome to The Combine - the hub for HSMA Lambda Project Proposals")

# Set up main sections of the app
col_left, col_right = st.columns([0.5,0.5])

# Grab contents of main the_combine table from Supabase DB
rows_main = run_query_main_table()

# Left section
with col_left:
    with st.container(height=600):
        for i in range(len(rows_main.data)-1,-1,-1):
            st.write(
                f"Proposal ID: **{rows_main.data[i]['proposal_id']}**",
                f"**{rows_main.data[i]['proposal_title']}**",
                f"*{rows_main.data[i]['proposer_name']}*",
                f"*{rows_main.data[i]['proposer_role']}*",
                f"*{rows_main.data[i]['proposer_org']}*",
                f"Area: {rows_main.data[i]['area_tag']}",
                f"Submitted: {rows_main.data[i]['submission_month']}",
                f"{rows_main.data[i]['submission_year']}"
            )
            if rows_main.data[i]['status'] == "inactive":
                st.info(
                    (
                        rows_main.data[i]['proposal_desc'] +
                        "\n\n" +
                        "**Collaborators:**" +
                        "\n\n" +
                        rows_main.data[i]['collaborators']
                    )
                )
            else:
                st.success(
                    (
                        rows_main.data[i]['proposal_desc'] +
                        "\n\n" +
                        "**Collaborators:**" +
                        "\n\n" +
                        rows_main.data[i]['collaborators']
                    )
                )

