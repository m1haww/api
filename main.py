from flask import Flask, jsonify, request, Response
from flask_restful import Api
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Dial
import uuid
import os
import threading
from datetime import datetime
from database import db
from models.call import Call
from models.user import User
from summary_service import SummaryService

HOST = "https://api-57018476417.europe-west1.run.app"
CONNECTION_STRING = "postgresql://postgres:grIfnjXjgauPzVcBJzKadyYZdwIdmoDT@shinkansen.proxy.rlwy.net:12034/railway"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = CONNECTION_STRING

CORS(app, origins=[HOST])

db.init_app(app)
api = Api(app)

def process_summary_and_title_background(call_uuid, transcribe_text):
    """Background function to generate summary and title for a call."""
    with app.app_context():
        try:
            print(f"Starting background processing for call UUID: {call_uuid}")
            
            call = db.session.query(Call).filter_by(id=call_uuid).first()
            if not call:
                print(f"Call not found for UUID: {call_uuid}")
                return
            
            summary_service = SummaryService()
            
            call.summary = summary_service.get_summary(transcribe_text)
            print(f"Summary generated for call UUID: {call_uuid}")
            
            call.title = summary_service.get_title(transcribe_text)
            print(f"Title generated for call UUID: {call_uuid}")
            
            db.session.commit()
            print(f"Background processing completed for call UUID: {call_uuid}")
            
        except Exception as e:
            print(f"Error in background processing for call UUID {call_uuid}: {str(e)}")
            try:
                call = db.session.query(Call).filter_by(id=call_uuid).first()
                if call:
                    call.summary = "Summary generation failed. Please review the transcription."
                    call.title = "Call Recording"
                    db.session.commit()
            except Exception as inner_e:
                print(f"Failed to update call with error fallback: {str(inner_e)}")

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

@app.route('/api/users/register', methods=['POST'])
def register_user():
    try:
        body = get_formated_body()
        
        phone_number = body.get('phoneNumber')
        fcm_token = body.get('fcmToken')
        
        if not phone_number:
            return jsonify({'error': 'phoneNumber is required'}), 400
        
        if not fcm_token:
            return jsonify({'error': 'fcmToken is required'}), 400
        
        existing_user = db.session.query(User).filter_by(phone_number=phone_number).first()
        
        if existing_user:
            existing_user.fcm_token = fcm_token
            existing_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'userId': str(existing_user.id),
                'message': 'User updated successfully'
            }), 200
        else:
            new_user = User(
                phone_number=phone_number,
                fcm_token=fcm_token
            )
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'userId': str(new_user.id),
                'message': 'User registered successfully'
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/notifications', methods=['PUT'])
def update_notification_settings():
    try:
        body = get_formated_body()
        
        user_id = body.get('userId')
        push_notifications_enabled = body.get('pushNotificationsEnabled')
        
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        if push_notifications_enabled is None:
            return jsonify({'error': 'pushNotificationsEnabled is required'}), 400
        
        user = db.session.query(User).filter_by(id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.push_notifications_enabled = push_notifications_enabled
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'userId': str(user.id),
            'pushNotificationsEnabled': user.push_notifications_enabled,
            'message': 'Notification settings updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/transcribe-complete', methods=['POST'])
def transcribe_complete():
    call_uuid = request.args.get('call-uuid')
    try:
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

        if transcribe_status == "completed" and transcribe_text:
            background_thread = threading.Thread(
                target=process_summary_and_title_background,
                args=(call_uuid, transcribe_text)
            )
            background_thread.daemon = True
            background_thread.start()
            print(f"Started background processing for call UUID: {call_uuid}")

        return jsonify("Transcribe was successfully saved."), 200
    except Exception as e:
        print(f"Error generating summary/title for call UUID {call_uuid}: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    """Handle incoming call and connect to a conference with beep and recording."""
    call_uuid = str(uuid.uuid4())

    body = get_formated_body()
    user_phone = body.get('From')

    call = Call(call_uuid, user_phone, datetime.now())
    db.session.add(call)
    db.session.commit()

    response = VoiceResponse()

    response.say("You are being connected. This call will be recorded.")

    response.pause(length=15)

    response.say("The recording has started.")

    response.record(
        play_beep=True,
        max_length = 5400,
        action = f"/record-complete?call-uuid={call_uuid}",
        transcribe = True,
        transcribe_callback = f"/transcribe-complete?call-uuid={call_uuid}",
    )

    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
