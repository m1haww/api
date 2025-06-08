from database import db

class Call(db.Model):
    __tablename__ = 'call'
    id = db.Column(db.String(100), primary_key=True)
    from_phone = db.Column(db.String(100))
    call_date = db.Column(db.DateTime, nullable=False)
    to_number = db.Column(db.String(100), nullable=True)
    to_contact_name = db.Column(db.String(200), nullable=True)
    
    recording_url = db.Column(db.String(500), nullable=True)
    recording_duration = db.Column(db.Integer, nullable=True)
    recording_status = db.Column(db.String(20), nullable=True)
    
    transcription_text = db.Column(db.Text, nullable=True)
    transcription_status = db.Column(db.String(20), nullable=True)
    
    def __init__(self, id, from_phone, call_date, to_number=None, to_contact_name=None,
                 recording_url=None, recording_duration=None, recording_status=None, 
                 transcription_text=None, transcription_status=None):
        self.id = id
        self.from_phone = from_phone
        self.call_date = call_date
        self.to_number = to_number
        self.to_contact_name = to_contact_name
        self.recording_url = recording_url
        self.recording_duration = recording_duration
        self.recording_status = recording_status
        self.transcription_text = transcription_text
        self.transcription_status = transcription_status
