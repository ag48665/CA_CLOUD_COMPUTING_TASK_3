
class Config:
    SECRET_KEY = "cloud_bus_pass_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///bus_pass.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False