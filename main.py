import streamlit as st

from auth import session
from auth.password import with_password

session_state = session.get(password=False)


@with_password(session_state)
def main():
    st.text("Authenticated!")


if __name__ == '__main__':
    main()
