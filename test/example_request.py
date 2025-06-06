import requests

url = "https://sentiment-analysis-flask-api-f67ilpsazq-nw.a.run.app"

params = {
	'q':'python360 videos are invariably somewhat interesting'
}

answer = requests.get(url, params = params)

print(answer.text)
