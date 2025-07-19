from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_jwt_extended import JWTManager
from flask_bootstrap5 import Bootstrap
import logging

logger = logging.getLogger(__name__)
db = SQLAlchemy()
jwt_blacklist = set()
csrf_token = CSRFProtect()
jwt = JWTManager()
bootstrap = Bootstrap()

