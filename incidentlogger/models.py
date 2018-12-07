from datetime import datetime 
from incidentlogger import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #image_file = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    incidents = db.relationship('Incident', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_resolved = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    descrption = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(100), nullable=False)
    tags = db.Column(db.String(100), nullable=False)
    current_assignee = db.Column(db.String(100), nullable=False)
    case_history = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_created}')"