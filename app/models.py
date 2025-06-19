from . import db
from datetime import datetime

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    num_rows = db.Column(db.Integer)
    num_columns = db.Column(db.Integer)
