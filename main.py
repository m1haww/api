#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#|r|e|d|a|n|d|g|r|e|e|n|.|c|o|.|u|k|
#+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

app = Flask(__name__)
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

if __name__ == "__main__":
    app.run(debug=True)
