from flask import Flask, jsonify, request, Response
from flask_restful import Api
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather, Record

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
    """Handle incoming calls with TwiML response including recording."""
    response = VoiceResponse()
    
    # Start recording the entire call in the background
    response.start_recording(
        recording_status_callback="/recording-status",
        recording_status_callback_method="POST",
        recording_status_callback_event="completed"
    )
    
    # Add a gather to collect input while call is being recorded
    gather = Gather(
        action="/process-gather",
        method="POST",
        input="speech dtmf",
        timeout=5,
        speech_timeout="auto",
        num_digits=1
    )
    gather.say("Welcome to our service. Press 1 for sales, 2 for support, or say your request.")
    response.append(gather)
    
    # If no input received
    response.say("We didn't receive any input. Goodbye!")
    response.hangup()
    
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
            response.say("Connecting you to sales.")
            # You can add dial functionality here
        elif digits == '2':
            response.say("Connecting you to support.")
            # You can add dial functionality here
        else:
            response.say("Invalid option.")
    elif speech_result:
        response.say(f"You said: {speech_result}")
        # Process speech input here
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
