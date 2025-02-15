import os
import streamlit as st

from streamlit.web.server import websocket_headers
from streamlit_chat import message

import requests

################################################################################
# Application State
################################################################################

# Initialise session state variables.
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

################################################################################
# Application UI
################################################################################

# Configure the side bar. This will allow a user to clear the chat and to set the number of tokens to return in the responses.
st.set_page_config(initial_sidebar_state='collapsed')
clear_button = st.sidebar.button("Clear Conversation", key="clear")
# We will give the end users the option to tailor how many characters are returned by the model as some questions require more detail than others.
output_tokens = st.sidebar.number_input('Number of output characters (50-500): ', min_value=50, max_value=500, value=200)

if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Header Image - You can change this to suit your application
st.image("https://futurium.ec.europa.eu/sites/default/files/2020-06/eu-ai-alliance-3_0.png")
# container for chat history
response_container = st.container()
# container for text box
container = st.container()

################################################################################
# User Input and Model API call
################################################################################

# Container for the chat interface
with container:
    with st.form(key='my_form', clear_on_submit=True):
        # Capture the user input
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')
    
    # When the user enters a question and clicks the submit button we will call out to the Deployed Llama2 model
    # to search on our documents.
    if submit_button and user_input:
        answer = None
        with st.spinner("Searching for the answer..."):
            # You will need to update the "post" and "auth" details for the model you have deployed
            response = requests.post("https://ws.domino-eval.com:443/models/6628fb935bdbbd56e9f7c144/latest/model",
    auth=(
        "X18p4AhlvC8oju9092GvtKzzIeWJw4yrCGw8UnefNZQne6eZNYitxIVZvFYgz7Bj",
        "X18p4AhlvC8oju9092GvtKzzIeWJw4yrCGw8UnefNZQne6eZNYitxIVZvFYgz7Bj"
        ),
                json={
                    # This is the data payload for the API
                    # It contains the question and the number of output characters from the UI
                    "data": {
                        "input_text": user_input,
                        "max_new_tokens": output_tokens
                    }
                }
            )
        if response:
            # The response from the API is returned as JSON and we want to get the text response from the model
            answer = response.json()["result"]["text_from_llm"]
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(answer)
    
    # update the state of the Chatbot and display the message to the user with a logo.
    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, logo='https://freesvg.org/img/1367934593.png', key=str(i) + '_user')
                # You can change this chat image to the logo of your organisation
                message(st.session_state["generated"][i], logo='https://ec.europa.eu/regional_policy/images/information-sources/logo-download-center/eu_flag.jpg', key=str(i))
