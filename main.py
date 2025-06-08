from flask import Flask, jsonify, request, Response
from flask_restful import Api
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse
import uuid
import os
from datetime import datetime
from database import db
from models.call import Call
from summary_service import SummaryService

HOST = "https://api-57018476417.europe-west1.run.app"
CONNECTION_STRING = "postgresql://postgres:grIfnjXjgauPzVcBJzKadyYZdwIdmoDT@shinkansen.proxy.rlwy.net:12034/railway"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STRING

CORS(app, origins=[HOST])

db.init_app(app)
api = Api(app)

def get_formated_body():
    if request.is_json:
        body = request.get_json()
        print(f"JSON body: {body}")
    elif request.form:
        body = request.form.to_dict()
        print(f"Form body: {body}")
    else:
        raw_data = request.get_data(as_text=True)
        print(f"Raw data: {raw_data}")
        from urllib.parse import parse_qs
        body = parse_qs(raw_data)
        body = {k: v[0] if len(v) == 1 else v for k, v in body.items()}
        print(f"Parsed body: {body}")
    return body

@app.route('/get_calls_for_user', methods=['POST'])
def get_calls_for_user():
    body = get_formated_body()
    user_phone = body.get('user_phone')
    
    if not user_phone:
        return jsonify({'error': 'user_phone parameter is required'}), 400

    calls = db.session.query(Call).filter_by(from_phone=user_phone).all()
    calls_list = []
    for call in calls:
        calls_list.append({
            'id': call.id,
            'from_phone': call.from_phone,
            'call_date': call.call_date.isoformat() if call.call_date else None,
            'title': call.title,
            'summary': call.summary,
            'recording_url': call.recording_url,
            'recording_duration': call.recording_duration,
            'recording_status': call.recording_status,
            'transcription_text': call.transcription_text,
            'transcription_status': call.transcription_status
        })

    return jsonify(calls_list), 200

@app.route('/transcribe-complete', methods=['POST'])
def transcribe_complete():
    call_uuid = request.args.get('call-uuid')
    
    if not call_uuid:
        return jsonify({'error': 'call-uuid parameter is required'}), 400

    body = get_formated_body()

    transcribe_text = body.get("TranscriptionText")
    transcribe_status = body.get("TranscriptionStatus")
    
    call = db.session.query(Call).filter_by(id=call_uuid).first()
    
    if not call:
        return jsonify({'error': 'Call not found'}), 404
    
    call.transcription_text = transcribe_text
    call.transcription_status = transcribe_status

    if transcribe_status == "completed" and transcribe_text:
        try:
            summary_service = SummaryService()
            
            call.summary = summary_service.get_summary(transcribe_text)
            print(f"Summary generated for call UUID: {call_uuid}")
            
            call.title = summary_service.get_title(transcribe_text)
            print(f"Title generated for call UUID: {call_uuid}")
            
        except Exception as e:
            print(f"Error generating summary/title for call UUID {call_uuid}: {str(e)}")
            call.summary = "Summary generation failed. Please review the transcription."
            call.title = "Call Recording"
    
    db.session.commit()

    return jsonify("Transcribe was successfully saved."), 200

@app.route('/record-complete', methods=['POST'])
def record_complete():
    call_uuid = request.args.get('call-uuid')
    
    if not call_uuid:
        return jsonify({'error': 'call-uuid parameter is required'}), 400

    body = get_formated_body()
    
    recording_url = body.get('RecordingUrl')
    recording_length = body.get('RecordingDuration')
    
    call = db.session.query(Call).filter_by(id=call_uuid).first()
    
    if not call:
        return jsonify({'error': 'Call not found'}), 404
    
    call.recording_url = recording_url
    call.recording_duration = int(recording_length) if recording_length else None
    call.recording_status = 'completed'

    db.session.commit()

    return jsonify("Recording successfully completed."), 200

@app.route("/test-summary", methods=["GET", "POST"])
def test_summary():
    """Test endpoint to verify the summary service is working."""
    sample_transcription = """
    Hello, this is John from ABC Corporation. I'm calling regarding our quarterly meeting scheduled for next week.
    
    We need to discuss three main points:
    First, the Q4 financial results which showed a 15% increase in revenue.
    Second, the new marketing campaign launching in January.
    Third, the upcoming merger with XYZ Company.
    
    I'll need you to prepare the financial reports by Thursday and send them to the board members.
    Also, please schedule a follow-up meeting with the marketing team for Friday at 2 PM.
    
    Let me know if you have any questions. My direct line is 555-1234.
    Thanks, and I'll see you at the meeting next Tuesday at 10 AM.
    """
    
    try:
        summary_service = SummaryService()
        
        summary = summary_service.get_summary(sample_transcription)
        
        title = summary_service.get_title(sample_transcription)
        
        return jsonify({
            'status': 'success',
            'test_transcription': sample_transcription,
            'generated_title': title,
            'generated_summary': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': 'Failed to generate summary. Check if g4f service is running.'
        }), 500

@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Handle incoming calls with gather and recording options."""
    call_uuid = str(uuid.uuid4())

    body = get_formated_body()
    user_phone = body.get('From')

    call = Call(call_uuid, user_phone, datetime.now())
    db.session.add(call)
    db.session.commit()

    response = VoiceResponse()

    response.say("The recording has started.")

    response.record(
        max_length=5400,
        action=f"/record-complete?call-uuid={call_uuid}",
        # transcribe=True,
        # transcribe_callback=f"/transcribe-complete?call-uuid={call_uuid}",
    )

    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
