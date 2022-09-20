import uuid

from traitlets import Bool
from tornado import gen

from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join


class VideoStationAuthenticateHandler(BaseHandler):
    """
    Handler for /tmplogin

    Creates a new user with a username passed via URL or random UUID, and auto starts their server
    """

    def initialize(self, force_new_server, process_user):
        super().initialize()
        self.force_new_server = force_new_server
        self.process_user = process_user

    @gen.coroutine
    def get(self):
        raw_user = yield self.get_current_user()
        self.clear_cookie("jupyterhub-session-id")
        self.clear_cookie("jupyterhub-hub-login")
        if raw_user:
            if self.force_new_server and user.running:
                # Stop user's current server if it is running
                # so we get a new one.
                status = yield raw_user.spawner.poll_and_notify()
                # if status is None:
                #     yield self.stop_single_user(raw_user)
        else:
            next_url = self.get_argument("next")
            if "spawn" in next_url:
                username = next_url.split("/")[-1]
            else:
                username = str(self.get_param_from_url(self.get_argument("next"), "user"))
            if username == "":
                username = str(uuid.uuid4())
            if "ts" in username:
                username = username.split("&")[0]
            raw_user = self.user_from_username(username)
            self.set_login_cookie(raw_user)
        user = yield gen.maybe_future(self.process_user(raw_user, self))
        self.redirect(self.get_next_url(user))

    @staticmethod
    def get_param_from_url(url, param_name):
        try:
            return [i.split("=")[-1] for i in url.split("?", 1)[-1].split("&") if i.startswith(param_name + "=")][0]
        except IndexError as E:
            return ""




class VideostationAuthenticator(Authenticator):
    """
    JupyterHub Authenticator for use with tmpnb.org

    When JupyterHub is configured to use this authenticator, visiting the home
    page immediately logs the user in with a username assgined in the URL if they
    are already not logged in, and spawns a server for them.
    """

    auto_login = True
    login_service = 'tmp'

    force_new_server = Bool(
        False,
        help="""
        Stop the user's server and start a new one when visiting /hub/tmplogin

        When set to True, users going to /hub/tmplogin will *always* get a
        new single-user server. When set to False, they'll be
        redirected to their current session if one exists.
        """,
        config=True
    )

    def process_user(self, user, handler):
        print("INSIDE PROCESS USER")
        print(user)
        """
        Do additional arbitrary things to the created user before spawn.

        user is a user object, and handler is a TmpAuthenticateHandler object

        Should return the new user object.

        This method can be a @tornado.gen.coroutine.

        Note: This is primarily for overriding in subclasses
        """
        return user

    def get_handlers(self, app):
        print("inside get handlers")
        # FIXME: How to do this better?
        extra_settings = {
            'force_new_server': self.force_new_server,
            'process_user': self.process_user
        }
        return [
            ('/tmplogin', VideoStationAuthenticateHandler, extra_settings)
        ]

    def login_url(self, base_url):
        print("inside login url")
        print(base_url)
        if "ts" in base_url:
                base_url = base_url.split("&")[0]
        print(base_url)
        return url_path_join(base_url, 'tmplogin')
