import streamlit as st

def keeper(key):
    #Save data from the widget key to a persistent key
    st.session_state[key] = st.session_state['_'+key]

def retriever(key):
    #Check for persistent key and populate widge key for multipage statefulness
    if key in st.session_state:
        st.session_state['_'+key] = st.session_state[key]