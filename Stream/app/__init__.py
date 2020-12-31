from flask import Flask
from .views import Users
from .views import Admin
from .views import Search

stream = Flask(__name__)
#stream.config["SECRET_KEY"] = "STREAM"
stream.secret_key = "STREAM"
stream.register_blueprint(Users.User)
stream.register_blueprint(Admin.Admin)
stream.register_blueprint(Search.Search)