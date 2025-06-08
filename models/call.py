from database import db

class Call(db.Model):
    __tablename__ = 'call'
    id = db.Column(db.String(100), primary_key=True)
    from_phone = db.Column(db.String(100))
    
    recording_url = db.Column(db.String(500), nullable=True)
    recording_duration = db.Column(db.Integer, nullable=True)
    recording_status = db.Column(db.String(20), nullable=True)
    
    transcription_text = db.Column(db.Text, nullable=True)
    transcription_status = db.Column(db.String(20), nullable=True)
    
    def __init__(self, id, from_phone, recording_url=None, recording_duration=None, 
                 recording_status=None, transcription_text=None, transcription_status=None):
        self.id = id
        self.from_phone = from_phone
        self.recording_url = recording_url
        self.recording_duration = recording_duration
        self.recording_status = recording_status
        self.transcription_text = transcription_text
        self.transcription_status = transcription_status
