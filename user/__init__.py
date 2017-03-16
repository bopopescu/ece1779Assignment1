from flask import Flask

app = Flask(__name__)

from user import db
from user import index
from user import login_register
from user import fileupload
from user import imagetransform
from user import thumbs
