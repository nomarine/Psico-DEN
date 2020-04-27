from flask import Flask
from datetime import date, time
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

UPLOAD_FOLDER = '/home/nomarine/PsicoDEN/app/static/arquivos'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav'])

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="nomarine",
    password="fijosaquino",
    hostname="nomarine.mysql.pythonanywhere-services.com",
    databasename="nomarine$PsicoDEN",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.secret_key = "something only you know"
login_manager = LoginManager()
login_manager.init_app(app)

from app.controllers import default