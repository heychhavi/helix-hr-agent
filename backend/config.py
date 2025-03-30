import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    # Database
    SQLALCHEMY_DATABASE_URI = 'postgresql://neondb_owner:npg_pvayKxe05qno@ep-silent-bonus-a68yb6ue-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # SocketIO
    CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

# Export configs
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 