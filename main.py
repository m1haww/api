#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|r|e|d|a|n|d|g|r|e|e|n|.|c|o|.|u|k|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

app = Flask(__name__)
CORS(app, origins=['https://api-57018476417.europe-west1.run.app'])
api = Api(app)

output = {}

# argument parsing
parser = reqparse.RequestParser()
parser.add_argument('q',help='Pass a sentence to analyse')

class SentAnalysis(Resource):

    def get(self):

        # use parser and find the user's query
        args = parser.parse_args()
        sentence = args['q']

        nltk.download("vader_lexicon")
        sid = SentimentIntensityAnalyzer()
        score = sid.polarity_scores(sentence)["compound"]
        if score > 0:
            output["sentiment"] = "Positive"    
        else:
            output["sentiment"] = "Negative"  

        return jsonify(output)

api.add_resource(SentAnalysis, '/')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "sentiment-analysis-api"}), 200

@app.route('/analyze-and-call', methods=['POST'])
def analyze_and_call():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'message' not in data or 'to_number' not in data:
            return jsonify({"error": "Missing required fields: message, to_number"}), 400
        
        message = data['message']
        to_number = data['to_number']
        from_number = data.get('from_number', os.environ.get('TWILIO_PHONE_NUMBER'))
        
        # Check for Twilio credentials
        try:
            account_sid = os.environ["TWILIO_ACCOUNT_SID"]
            auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        except KeyError:
            return jsonify({"error": "TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables must be set"}), 500
        
        if not from_number:
            return jsonify({"error": "No from_number provided and TWILIO_PHONE_NUMBER not set"}), 400
        
        # Analyze sentiment
        nltk.download("vader_lexicon", quiet=True)
        sid = SentimentIntensityAnalyzer()
        sentiment_scores = sid.polarity_scores(message)
        score = sentiment_scores["compound"]
        
        if score > 0:
            sentiment = "Positive"
            response_message = f"The message has a positive sentiment. The text was: {message}"
        else:
            sentiment = "Negative"
            response_message = f"The message has a negative sentiment. The text was: {message}"
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Create TwiML response
        twiml = f'<Response><Say voice="alice">{response_message}</Say></Response>'
        
        # Make the call
        call = client.calls.create(
            twiml=twiml,
            to=to_number,
            from_=from_number
        )
        
        return jsonify({
            "status": "success",
            "sentiment": sentiment,
            "sentiment_scores": sentiment_scores,
            "call_sid": call.sid,
            "call_status": call.status,
            "to": call.to,
            "from": call.from_
        }), 200
        
    except TwilioException as e:
        return jsonify({"error": f"Twilio error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
