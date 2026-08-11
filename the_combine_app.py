import streamlit as st
from supabase import create_client, Client
from google import genai
import random
from datetime import datetime

client = genai.Client(
    api_key = st.secrets["GEMINI_API_KEY"]
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Custom CSS 
st.markdown("""
<style>
.st-key-inactive_proposals div[data-testid="stExpander"] summary {
    background-color: #875a00;
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
    background-color: #3e3000;
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

.st-key-chat_history_container {
    background-color: #230949;
    border: 1px solid #f5f9fc;
    border-radius: 10px;
    padding: 10px;
}

.st-key-new_prop_container {
    background-color: #636363;
    border: 1px solid #f5f9fc;
    border-radius: 10px;
    padding: 10px;
}

.st-key-form_error_container {
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
        Role of Proposer : {row['proposer_role']}
        Description:
        {row['proposal_desc']}
        Collaborators:
        {row['collaborators']}
        Date Submitted : {row['submission_month']} {row['submission_year']}
        Status of Proposal : {row['status']}
        ---
        """

    return context

# Decorated function to display error in dialog box for combine harvester errors
@st.dialog("Something went wrong")
def show_error_harvester():
    st.write(
        "Sorry - I couldn't get a response from Gemini.  Please try again"
    )
    hl_quotes = [
        "Wake up and... smell the ashes...",
        "They're waiting for you Gordon... in the test chamber",
        """The right man in the wrong place can make all the difference in the
        world""",
        "Prepare... for unforeseen consequences..."
    ]
    chosen_hl_quote = random.choice(hl_quotes)
    st.caption(chosen_hl_quote)
    if st.button("OK"):
        st.rerun()

# Decorated function to display new proposal submission confirmation in dialog
# box
@st.dialog("Proposal Submitted")
def show_new_prop_confirmation(pr_id, pr_title):
    st.write(
        f"Your proposal **{pr_title}** has been successfully submitted."
    )
    st.write(
        f"Your proposal ID is **{pr_id}**.  Please make a note of this and " +
        "ensure you pass it to any staff applying to the HSMA programme to " +
        "work on this project, as they will need it at the application stage."
    )

# Set up header columns
header_col_left, header_col_mid, header_col_right = st.columns([0.1,0.8,0.1])

# Logo section
with header_col_left:
    st.image("arc_logo.jpg", width="stretch")

    st.image("hsma_logo.png", width="stretch")

# Header intro section 
with header_col_mid:
    # Title for app
    st.header("The Combine")
    st.write(
        """
        Welcome to The Combine - the hub for HSMA Lambda Project Proposals.
        \n
        You can browse submitted project proposals using the section on the
        left, and use the tabs to switch between proposals that have been
        submitted but not yet turned into HSMA projects, those that are 
        current
        HSMA projects, and those that have been completed as HSMA projects.
        Use the Combine Harvester to ask questions about the proposals in 
        the
        database.  For example, you could ask if any proposals are looking 
        at
        something you're interested in, or if there are any proposals 
        submitted
        from your organisation.  The Combine Harvester is AI-powered.
        Use the form on the right to submit new proposals.  You should only
        submit proposals if you have attended a HSMA Lambda workshop.\n
        If you have any queries, please contact penchord@exeter.ac.uk
        HSMA : https://hsma.co.uk 
        HSMA Lambda : https://hsma.co.uk/lambda.html
        """
    )

# HL2 image section
with header_col_right:
    st.image("hl_2_image.png", width="stretch")

# Set up main sections of the app
col_left, col_mid, col_right_f, col_right_e = st.columns([0.25,0.25,0.35,0.15])

# Grab contents of main the_combine table from Supabase DB
try:
    rows_main = run_query_main_table()
except:
    col_left.error("Error connecting to database.  Please try again later")
    st.stop()

proposal_context = create_proposal_context(rows_main)

# Reset form manually if required
if st.session_state.get("clear_proposal_form", False):
    st.session_state.new_name = ""
    st.session_state.new_role = ""
    st.session_state.new_org = ""
    st.session_state.new_desc_question = ""
    st.session_state.new_desc_background = ""
    st.session_state.new_desc_pot_impact = ""
    st.session_state.new_collaborators = ""
    st.session_state.clear_proposal_form = False

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
    st.subheader("The Combine Harvester")
    st.write(":sparkles: *Powered by Gemini*")

    with st.container(height=480, key="chat_history_container"):
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    question = st.chat_input(
        "Ask me anything about the proposals in the database..."
    )

    if question:
        try:
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
                    #model="gemini-3.6-flash",
                    model="gemini-3.5-flash-lite",
                    contents=f"""
                    You are an assistant helping senior NHS leaders find
                    information about HSMA Lambda project proposals that have
                    been previously submitted (some of which will have turned
                    into active or even completed projects, which you can see by
                    their status).

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
        except:
            st.session_state.error_harvester = True
            
        st.rerun()

with col_right_e:
    st.subheader("Form Errors")
    # Form error container
    form_error_container = st.container(height=600, key="form_error_container")

# Proposals input form section
with col_right_f:
    st.subheader("Submit a New Project Proposal")

    with st.container(height=600, key="new_prop_container"):
        st.write(
            """
            Use this form to submit a new project proposal.  You should only use
            this form if you have attended a HSMA Lambda workshop.  However, 
            you may 
            submit proposals that you didn't formulate at the workshop.  Please
            provide as much information as possible.  You should also make 
            a note 
            of the proposal number you are allocated when you submit the proposal -
            if you are sending an applicant onto the HSMA programme with the
            intention to work on this project, they will need to provide this
            proposal number on their application.
            """
        )

        with st.form(
            "new_proposal_form",
            enter_to_submit=False
        ):
            new_name = st.text_input(
                "What's your name?",
                key="new_name"
            )

            new_role = st.text_input(
                "What's your job title?",
                key="new_role"
            )

            new_org = st.text_input(
                "What's your organisation?",
                key="new_org"
            )

            new_desc_question = st.text_area(
                "What are the question(s) you want the project to answer? " +
                "Capture any 'what if?' scenarios you want to test, " +
                "if relevant. Please be as specific as possible, " +
                "and ensure your question(s) are clear, focused and relevant " +
                "for modelling.",
                height="content",
                key="new_desc_question"
            )

            new_desc_background = st.text_area(
                "What's the background to the problem you're trying to solve? "+
                "What's happening now and why is this a problem?  Why is now "+ 
                "the right time to try to solve this?",
                height="content",
                key="new_desc_background"
            )

            new_desc_pot_impact = st.text_area(
                "What would be the potential impact of solving this problem? " +
                "Specify the potential impact for your organisation " +
                "(particularly in terms of any cost savings or efficiencies) " +
                "and for patients.",
                height="content",
                key="new_desc_pot_impact"
            )

            new_collaborators = st.text_area(
                "Please list any organisations with which you intend to " +
                "collaborate on this project.  If there are no collaborators, "+
                "please leave this blank.  We encourage HSMA Lambda project " +
                "proposals to consider collaboration wherever possible to " +
                "maximise impact and share learning, expertise and resources " +
                "to tackle common problems.  We consider collaboration and " +
                "scope of impact strongly when considering which HSMA " +
                "projects are selected for mentoring support.  We encourage " +
                "you to chat on the provided Discourse platform to continue " +
                "to discuss ideas with others who have been on the " +
                "HSMA-Lambda series of workshops.",
                height="content",
                key="new_collaborators"
            )

            st.write(
                """
                Please note, we cannot guarantee that submitted project
                proposals will be selected to receive mentoring support in the
                HSMA programme, or that the applicant(s) sent onto the
                programme to undertake the work will be successful in their
                application.  By submitting the form, you understand that we
                cannot guarantee our support or mentoring provision for the 
                work you are proposing.
                """
            )

            proposal_submitted = st.form_submit_button("Submit Proposal")

            # Update database with new entry
            if proposal_submitted:
                # Grab current rows in database table
                rows = run_query_main_table()

                input_errors = []

                # Identify any inputs (other than collaborators) that are empty
                # (or just whitespace) and throw an error if they are
                if not new_name.strip():
                    input_errors.append("You must provide your name")

                if not new_role.strip():
                    input_errors.append("You must provide your role")

                if not new_org.strip():
                    input_errors.append("You must provide your organisation")

                if (
                    not new_desc_question.strip() and
                    not new_desc_background.strip() and
                    not new_desc_pot_impact.strip()
                ):
                    input_errors.append(
                        "You must provide some proposal information"
                    )

                if input_errors:
                    for error in input_errors:
                        form_error_container.error(error)
                else:
                    # Check if any of the individual description inputs are 
                    # blank and replace with "Information not provided" if so
                    if not new_desc_question.strip():
                        new_desc_question = "Information not provided"

                    if not new_desc_background.strip():
                        new_desc_background = "Information not provided"

                    if not new_desc_pot_impact.strip():
                        new_desc_pot_impact = "Information not provided"

                    # Concatenate the proposal description from the provided
                    # information
                    new_desc = (
                        "Question(s):" +
                        "\n\n" +
                        new_desc_question +
                        "\n\n" +
                        "Background:" +
                        "\n\n" +
                        new_desc_background +
                        "\n\n" +
                        "Potential Impact:" +
                        "\n\n" +
                        new_desc_pot_impact
                    )

                    # If collaborators field is empty, replace it with "(None at
                    # this time)"
                    if new_collaborators == "":
                        new_collaborators = "(None at this time)"

                    # Identify month and year of submission
                    list_of_months = [
                        "Jan",
                        "Feb",
                        "Mar",
                        "Apr",
                        "May",
                        "Jun",
                        "Jul",
                        "Aug",
                        "Sep",
                        "Oct",
                        "Nov",
                        "Dec"
                    ]
                    new_month = list_of_months[
                        datetime.today().month - 1
                    ]
                    new_year = datetime.today().year

                    # Try generating proposal title using AI
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.5-flash-lite",
                            contents=f"""
                            A senior NHS leader has just submitted the following
                            information as a proposal for a modelling / data 
                            science project to be undertaken as part of the 
                            HSMA Programme.

                            Please come up with a title for the proposal that  
                            can be used as the project title if selected.  Where
                            relevant, provide the geographic area of the 
                            proposed work in the title.

                            This is a description of what they want to do:
                            {new_desc}
                            This is the organisation that is proposing the work:
                            {new_org}
                            And here are the collaborators (if any):
                            {new_collaborators}

                            Please provide your answer simply as the title you 
                            come up with - nothing else.
                            """
                        )

                        new_title = response.text
                    except:
                        new_title = "Placeholder Title (Final TBC)"

                    while True:
                        try:
                            # Randomly generate a proposal identifier
                            new_prop_id = random.randint(100000,999999)

                            response = (
                                supabase.table("lambda_proposals").insert(
                                    {
                                        "proposal_id":new_prop_id,
                                        "proposal_title":new_title,
                                        "proposer_name":new_name,
                                        "proposer_role":new_role,
                                        "proposer_org":new_org,
                                        "proposal_desc":new_desc,
                                        "collaborators":new_collaborators,
                                        "submission_month":new_month,
                                        "submission_year":new_year,
                                        "status":"inactive"
                                    }
                                ).execute()
                            )

                            break
                        except:
                            pass

                    st.session_state.pr_id = new_prop_id
                    st.session_state.pr_title = new_title
                    st.session_state.new_proposal_submitted = True

                    st.session_state.clear_proposal_form = True

                    st.rerun()

if st.session_state.pop("error_harvester", False):
    show_error_harvester()

if st.session_state.pop("new_proposal_submitted", False):
    show_new_prop_confirmation(
        st.session_state.pr_id,
        st.session_state.pr_title
    )

