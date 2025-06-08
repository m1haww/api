from flask import Flask, jsonify, request, Response
from flask_restful import Api
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse

HOST = "https://api-57018476417.europe-west1.run.app"

app = Flask(__name__)
CORS(app, origins=[HOST])
api = Api(app)

output = {}

@app.route('/test')
def test():
    return jsonify({"message": "hello world"}), 200

@app.route('/transcribe-complete', methods=['POST'])
def transcribe_complete():
    return jsonify(output), 200

@app.route('/record-complete', methods=['POST'])
def record_complete():
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
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
    
    recording_url = body.get('RecordingUrl')
    recording_length = body.get('RecordingDuration')

    print("----------------------------------------")
    print(f"Recording url: {recording_url}")
    print(f"Recording length: {recording_length}")
    print("----------------------------------------")
    
    output['recordingUrl'] = recording_url
    output['recordingLength'] = recording_length

    return jsonify(output), 200

@app.route("/answer", methods=["GET", "POST"])
def answer():
    """Handle incoming calls with gather and recording options."""
    response = VoiceResponse()
    
    response.say("Mihai tu o sa ai padrugi tare multe si bani multi.")

    response.record(
        action="/record-complete",
        # transcribe=True,
        # transcribe_callback="/transcribe-complete",
    )

    return Response(str(response), mimetype='text/xml')

if __name__ == "__main__":
    port = 8080
    app.run(host='0.0.0.0', port=port, debug=False)
