"""Hack to add per-session state to Streamlit.

References
----------
[1] https://gist.github.com/tvst/036da038ab3e999a64497f42de966a92
"""
from typing import Any

try:
    import streamlit.ReportThread as ReportThread
    from streamlit.server.Server import Server
except ImportError:
    # Streamlit >= 0.65.0
    import streamlit.report_thread as ReportThread  # noqa
    from streamlit.server.server import Server


class SessionState:

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __getitem__(self, item: str):
        if item in self.__dict__:
            return self.__dict__[item]
        raise KeyError(item)

    def __setitem__(self, key: str, value: Any):
        self.__dict__[key] = value

    def logout(self):
        if "password" in self.__dict__:
            del self.__dict__["password"]


def get(**kwargs):
    """Gets a SessionState object for the current session.
    Creates a new object if necessary.
    Parameters
    ----------
    **kwargs : any
        Default values you want to add to the session state, if we're creating a
        new one.
    Example
    -------
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state["user_name"]
    ''
    >>> session_state.user_name = 'Mary'
    >>> session_state["favorite_color"]
    'black'
    Since you set user_name above, next time your script runs this will be the
    result:
    >>> session_state = get(user_name='', favorite_color='black')
    >>> session_state["user_name"]
    'Mary'
    """
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    this_session = None
    current_server = Server.get_current()
    if hasattr(current_server, '_session_infos'):
        # Streamlit < 0.56
        session_infos = current_server._session_infos.values() # noqa
    else:
        session_infos = current_server._session_info_by_id.values() # noqa

    for session_info in session_infos:
        s = session_info.session
        if (
            # Streamlit < 0.54.0
            (hasattr(s, '_main_dg') and s._main_dg == ctx.main_dg) # noqa
            or
            # Streamlit >= 0.54.0
            (not hasattr(s, '_main_dg') and s.enqueue == ctx.enqueue)
            or
            # Streamlit >= 0.65.2
            (not hasattr(s, '_main_dg') and s._uploaded_file_mgr == ctx.uploaded_file_mgr) # noqa
        ):
            this_session = s

    if this_session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object. "
            "Are you doing something fancy with threads?")

    # Got the session object! Now let's attach some state into it.

    if not hasattr(this_session, '_custom_session_state'):
        this_session._custom_session_state = SessionState(**kwargs)

    return this_session._custom_session_state # noqa