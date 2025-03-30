from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmailSequence(db.Model):
    """Email sequence model."""
    __tablename__ = 'email_sequences'
    
    id = db.Column(db.Integer, primary_key=True)
    persona = db.Column(db.String(50), nullable=False)
    tone = db.Column(db.String(50), nullable=False)
    sequence_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'persona': self.persona,
            'tone': self.tone,
            'sequence_type': self.sequence_type,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Conversation(db.Model):
    """Conversation history model."""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    messages = db.Column(db.JSON, nullable=False)
    persona = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'messages': self.messages,
            'persona': self.persona,
            'created_at': self.created_at.isoformat()
        } 