from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class EmailSequence(db.Model):
    """Email sequence model."""
    __tablename__ = 'email_sequences'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    persona = db.Column(db.String(50), nullable=False)
    tone = db.Column(db.String(50), nullable=True)
    sequence_type = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'persona': self.persona,
            'tone': self.tone,
            'sequence_type': self.sequence_type,
            'created_at': self.created_at.isoformat()
        }

class Conversation(db.Model):
    """Conversation history model."""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    messages = db.Column(db.JSON, nullable=False)
    persona = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'messages': self.messages,
            'persona': self.persona,
            'created_at': self.created_at.isoformat()
        } 