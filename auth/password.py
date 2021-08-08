import os
from typing import Callable, Tuple

import streamlit as st

from auth.session import SessionState

ENV_DASHBOARD_PASSWORD = "DASHBOARD_PASSWORD"


def is_authenticated(pwd: str) -> bool:
    return pwd == os.environ.get(ENV_DASHBOARD_PASSWORD, None)


def login(blocks: Tuple) -> str:
    style, element = blocks
    style.markdown("""
    <style>
        input { -webkit-text-security: disc; }
    </style>
    """, unsafe_allow_html=True)
    return element.text_input("Password")


def clean_blocks(*blocks):
    for block in blocks:
        block.empty()


def with_password(session_state: SessionState):
    if session_state["password"]:
        login_blocks = None
        password = session_state["password"]
    else:
        login_blocks = st.empty(), st.empty()
        password = login(login_blocks)
        session_state["password"] = password

    def wrapper(entry_point: Callable):

        def wrapped():
            if is_authenticated(password):
                if login_blocks is not None:
                    clean_blocks(*login_blocks)
                entry_point()
            elif password:
                st.error("Please configure or enter a valid password to access the dashboard.")

        return wrapped

    return wrapper
