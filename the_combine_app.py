import streamlit as st
from supabase import create_client, Client

# Custom CSS 
st.markdown("""
<style>
.st-key-inactive_proposals div[data-testid="stExpander"] summary {
    background-color: #340a95;
    color: #fdfdfd;
}

.st-key-inactive_proposals div[data-testid="stExpander"] details > div {
    background-color: white;
    color: black
}

.st-key-active_proposals div[data-testid="stExpander"] summary {
    background-color: #0da64d;
    color: #fdfdfd;
}

.st-key-active_proposals div[data-testid="stExpander"] details > div {
    background-color: white;
    color: black
}

.st-key-inactive_proposals {
    background-color: #350053;
    border: 1px solid #f5f9fc;
    border-radius: 10px;
    padding: 10px;
}

.st-key-active_proposals {
    background-color: #004501;
    border: 1px solid #f5f9fc;
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

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
col_left, col_mid, col_right = st.columns([0.25,0.25,0.5])

# Grab contents of main the_combine table from Supabase DB
rows_main = run_query_main_table()

# Inactive proposals section
with col_left:
    with st.container(height=600, key="inactive_proposals"):
        for i in range(len(rows_main.data)-1,-1,-1):
            if rows_main.data[i]['status'] == "inactive":
                headline = (
                    f"**[{rows_main.data[i]['proposal_id']}]  " +
                    f"{rows_main.data[i]['proposal_title']}**" +
                    "\n\n" +
                    "Proposed by : "
                    f"*{rows_main.data[i]['proposer_name']} (" +
                    f"{rows_main.data[i]['proposer_role']}, " +
                    f"{rows_main.data[i]['proposer_org']})*" +
                    "\n\n" +
                    f"Tag: {rows_main.data[i]['area_tag']} " +
                    f"(Submitted: {rows_main.data[i]['submission_month']} " +
                    f"{rows_main.data[i]['submission_year']})"
                )

                with st.expander(headline):
                    st.write(
                        rows_main.data[i]['proposal_desc'] +
                        "\n\n" +
                        "**Collaborators:**" +
                        "\n\n" +
                        rows_main.data[i]['collaborators']
                    )

# Active proposals section
with col_mid:
    with st.container(height=600, key="active_proposals"):
        for i in range(len(rows_main.data)-1,-1,-1):
            if rows_main.data[i]['status'] == "active":
                headline = (
                    f"**[{rows_main.data[i]['proposal_id']}]  " +
                    f"{rows_main.data[i]['proposal_title']}**" +
                    "\n\n" +
                    "Proposed by : "
                    f"*{rows_main.data[i]['proposer_name']} (" +
                    f"{rows_main.data[i]['proposer_role']}, " +
                    f"{rows_main.data[i]['proposer_org']})*" +
                    "\n\n" +
                    f"Tag: {rows_main.data[i]['area_tag']} " +
                    f"(Submitted: {rows_main.data[i]['submission_month']} " +
                    f"{rows_main.data[i]['submission_year']})"
                )

                with st.expander(headline):
                    st.write(
                        rows_main.data[i]['proposal_desc'] +
                        "\n\n" +
                        "**Collaborators:**" +
                        "\n\n" +
                        rows_main.data[i]['collaborators']
                    )

