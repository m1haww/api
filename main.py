from flask import Flask, jsonify, request, Response
from flask_restful import Api
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Dial

HOST = "https://api-57018476417.europe-west1.run.app"

app = Flask(__name__)
CORS(app, origins=[HOST])
api = Api(app)

output = {}

@app.route('/test')
def test():
    return jsonify({"message": "hello world"}), 200

@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Handle incoming calls with gather and recording options."""
    response = VoiceResponse()
    
    response.say("Mihai tu o sa ai padrugi tare multe si bani multi.")

    response.record()

    return Response(str(response), mimetype='text/xml')

@app.route("/handle-recording", methods=["POST"])
def handle_recording():
    """Handle the recording action callback."""
    response = VoiceResponse()
    
    # Get recording details from the request
    recording_url = request.values.get('RecordingUrl')
    recording_duration = request.values.get('RecordingDuration')
    
    response.say("Thank you for your recording.")
    response.hangup()
    
    return Response(str(response), mimetype='text/xml')

@app.route("/process-gather", methods=["POST"])
def process_gather():
    """Process gathered input from caller."""
    response = VoiceResponse()
    
    # Get the user's input
    digits = request.values.get('Digits')
    speech_result = request.values.get('SpeechResult')
    confidence = request.values.get('Confidence')
    
    if digits:
        if digits == '1':
            response.say("Connecting you to sales. This call will be recorded.")
            # Dial with recording enabled
            dial = Dial(
                record="record-from-answer-dual",  # Records both sides
                recording_status_callback="/recording-status",
                recording_status_callback_method="POST"
            )
            dial.number("+1234567890")  # Replace with actual sales number
            response.append(dial)
        elif digits == '2':
            response.say("Connecting you to support. This call will be recorded.")
            # Dial with recording enabled
            dial = Dial(
                record="record-from-answer-dual",  # Records both sides
                recording_status_callback="/recording-status",
                recording_status_callback_method="POST"
            )
            dial.number("+1234567890")  # Replace with actual support number
            response.append(dial)
        else:
            response.say("Invalid option.")
            response.redirect("/answer")  # Go back to main menu
    elif speech_result:
        response.say(f"You said: {speech_result}. Let me record your message.")
        # Record the caller's message
        response.record(
            action="/handle-recording",
            method="POST",
            max_length=300,  # 5 minutes max
            recording_status_callback="/recording-status",
            recording_status_callback_method="POST",
            trim="trim-silence"
        )
    else:
        response.say("No input received.")
        response.hangup()
    
    return Response(str(response), mimetype='text/xml')


def save_recording_to_db(call_sid, recording_sid, recording_url):
    print("----------------------------------------")
    print(recording_url)
    print("----------------------------------------")

def save_call_status(call_sid, call_status):
    print("-----------------------------------------")
    print(call_status)
    print("-----------------------------------------")

@app.route("/handle-dial-status", methods=["POST"])
def handle_dial_status():
    data = request.form.to_dict()

    call_sid = data.get("CallSid")
    call_status = data.get("DialCallStatus")  # 'completed', 'no-answer', etc.

    save_call_status(call_sid, call_status)

    return "OK", 200

@app.route("/recording-status", methods=["POST"])
def recording_status():
    data = request.form.to_dict()

    recording_url = data.get("RecordingUrl")
    call_sid = data.get("CallSid")
    recording_sid = data.get("RecordingSid")
    status = data.get("RecordingStatus")

    if status == "completed":
        save_recording_to_db(call_sid, recording_sid, recording_url)

    return "OK", 200

if __name__ == "__main__":
    port = 8080
    app.run(host='0.0.0.0', port=port, debug=False)
