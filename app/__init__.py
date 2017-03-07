from flask import Flask

app = Flask(__name__)

from app import db
from app import index
from app import login_register
from app import fileupload
from app import imagetransform
from app import admin
