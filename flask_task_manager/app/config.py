import os

class Config:
    SECRET_KEY = '6dbd0e3fcf073919573b73adbdb24f21'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///task.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Setări pentru sesiuni
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'