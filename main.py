from flask import Flask, jsonify, request
from flask_restful import Api
from flask_cors import CORS

HOST = "https://api-57018476417.europe-west1.run.app"

app = Flask(__name__)
CORS(app, origins=[HOST])
api = Api(app)

output = {}

@app.route('/test')
def test():
    return jsonify({"message": "hello world"}), 200


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
