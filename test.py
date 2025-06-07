import os
from twilio.rest import Client

# Set environment variables for your credentials
# Read more at http://twil.io/secure

HOST = "https://api-57018476417.europe-west1.run.app"

account_sid = ""
auth_token = ""
client = Client(account_sid, auth_token)

call = client.calls.create(
  url=f"{HOST}/answer",  # Point to your answer endpoint
  to="(347) 673-1472",
  from_="+19865294217",
  record=True,  # Enable call recording
  recording_status_callback=f"{HOST}/recording-status",
  recording_status_callback_method="POST"
)

print(call.sid)