import streamlit as st
from supabase import create_client, Client
from google import genai

client = genai.Client(
    api_key = st.secrets["GEMINI_API_KEY"]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

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
    background-color: #0000ff;
    color: #fdfdfd;
}

.st-key-active_proposals div[data-testid="stExpander"] details > div {
    background-color: white;
    color: black
}

.st-key-completed_proposals div[data-testid="stExpander"] summary {
    background-color: #0da64d;
    color: #fdfdfd;
}

.st-key-completed_proposals div[data-testid="stExpander"] details > div {
    background-color: white;
    color: black
}

.st-key-inactive_proposals {
    background-color: #2b0043;
    border: 1px solid #f5f9fc;
    border-radius: 10px;
    padding: 10px;
}

.st-key-active_proposals {
    background-color: #080072;
    border: 1px solid #f5f9fc;
    border-radius: 10px;
    padding: 10px;
}

.st-key-completed_proposals {
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

# Function to load all of the proposal information across the database into a
# single text block, for use as context for LLM
def create_proposal_context(rows):
    context = ""

    for row in rows.data:
        context += f"""
        Proposal ID: {row['proposal_id']}
        Title: {row['proposal_title']}
        Organisation: {row['proposer_org']}
        Proposer: {row['proposer_name']}
        Description:
        {row['proposal_desc']}
        ---
        """

    return context

# Title for app
st.title("The Combine")
st.write(
    "Welcome to The Combine - the hub for HSMA Lambda Project Proposals."
)

# Set up main sections of the app
col_left, col_mid, col_right = st.columns([0.25,0.25,0.5])

# Grab contents of main the_combine table from Supabase DB
rows_main = run_query_main_table()

proposal_context = create_proposal_context(rows_main)

# Proposals information section
with col_left:
    # Tabs for proposal categories
    tab_inactive, tab_active, tab_completed = st.tabs(
        ["Submitted Proposals",
        "Proposals currently Active as Projects",
        "Completed Projects"]
    )

    # Inactive proposals
    with tab_inactive:
        with st.container(height=600, key="inactive_proposals"):
            st.header(
                "Submitted Proposals"
            )
            st.write(
                "This section lists HSMA Lambda proposals that have been " +
                "submitted, but are not yet active HSMA projects"
            )
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

    # Active projects
    with tab_active:
        with st.container(height=600, key="active_proposals"):
            st.header(
                "Active Projects"
            )
            st.write(
                "This section lists HSMA Lambda proposals that are currently " +
                "being worked on as active HSMA projects"
            )

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

    # Completed projects
    with tab_completed:
        with st.container(height=600, key="completed_proposals"):
            st.header(
                "Completed Projects"
            )
            st.write(
                "This section lists HSMA Lambda proposals that were " +
                "completed as part of the HSMA programme"
            )

            for i in range(len(rows_main.data)-1,-1,-1):
                if rows_main.data[i]['status'] == "completed":
                    headline = (
                        f"**[{rows_main.data[i]['proposal_id']}]  " +
                        f"{rows_main.data[i]['proposal_title']}**" +
                        "\n\n" +
                        "Proposed by : "
                        f"*{rows_main.data[i]['proposer_name']} (" +
                        f"{rows_main.data[i]['proposer_role']}, " +
                        f"{rows_main.data[i]['proposer_org']})*" +
                        "\n\n" +
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

# LLM Chatbot section
with col_mid:
    st.header("The Combine Harvester")

    with st.container(height=500):
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    question = st.chat_input(
        "Ask a question about the proposals in the database..."
    )

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        conversation = ""

        for message in st.session_state.messages:
            conversation += f"{message['role']}: {message['content']}\n"

        with st.spinner("Thinking..."):
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=f"""
                You are an assistant helping senior NHS leaders find
                information about HSMA Lambda project proposals that have
                been previously submitted (some of which will have turned
                into active or even completed projects).

                Only answer using the proposal information provided.  If
                there are no matching proposals, say so.

                Here are the project proposals :
                {proposal_context}

                And here's the conversation so far :
                {conversation}

                Please answer the user's latest question.
                """
            )

        answer = response.text

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content" : answer
            }
        )

        st.rerun()

