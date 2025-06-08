from flask import Flask, jsonify, request, Response
from flask_restful import Api
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse
import uuid
from datetime import datetime
from database import db
from models.call import Call

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
    
    db.session.commit()

    if transcribe_status == "completed":
        print(f"Transcription completed for call UUID: {call_uuid}")
        print(f"Transcription text: {transcribe_text}")
    else:
        print(f"Transcription status not completed for call UUID: {call_uuid}")

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

@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Handle incoming calls with gather and recording options."""
    call_uuid = str(uuid.uuid4())

    body = get_formated_body()
    user_phone = body.get('From')

    call = Call(call_uuid, user_phone, datetime.now())
    db.session.add(call)
    db.session.commit()

    return jsonify("Call was successfully saved."), 200

    # response = VoiceResponse()
    #
    # response.say("The recording has started.")
    #
    # response.record(
    #     action=f"/record-complete?call-uuid={call_uuid}",
    #     transcribe=True,
    #     transcribe_callback=f"/transcribe-complete?call-uuid={call_uuid}",
    # )
    #
    # return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = 8080
    app.run(host='0.0.0.0', port=port, debug=False)
