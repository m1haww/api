"""
Example Twilio recording configurations for different use cases
"""

from flask import Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial

def basic_recording_example():
    """Basic recording with timeout and finish key."""
    response = VoiceResponse()
    
    response.say("Please leave your message after the beep. Press pound when finished.")
    response.record(
        action="/handle-recording",
        method="POST",
        max_length=5400,  # Maximum 2 minutes
        finish_on_key="#",
        recording_status_callback="/recording-status",
        recording_status_callback_method="POST"
    )
    
    return Response(str(response), mimetype='text/xml')

def recording_with_transcription():
    """Recording with automatic transcription."""
    response = VoiceResponse()
    
    response.say("Your call will be recorded and transcribed.")
    response.record(
        transcribe=True,
        transcribe_callback="/transcription-complete",
        max_length=300,  # 5 minutes
        recording_status_callback="/recording-status",
        play_beep=True
    )
    
    return Response(str(response), mimetype='text/xml')

def gather_with_background_recording():
    """Gather input while recording entire call."""
    response = VoiceResponse()
    
    # Start recording the entire call
    response.start_recording(
        recording_status_callback="/recording-status",
        recording_status_callback_method="POST"
    )
    
    # Gather user input
    gather = Gather(
        action="/process-menu",
        method="POST",
        input="speech dtmf",
        timeout=10,
        speech_timeout=3,
        language="en-US",
        speech_model="phone_call"
    )
    gather.say("Welcome. Please tell us how we can help you today, or press 1 for sales, 2 for support.")
    response.append(gather)
    
    response.say("We didn't receive any input. Transferring you to an agent.")
    response.dial("+1234567890")
    
    return Response(str(response), mimetype='text/xml')

def dial_with_recording():
    """Record a call when dialing another number."""
    response = VoiceResponse()
    
    response.say("Connecting your call. This call will be recorded.")
    
    dial = Dial(
        record="record-from-answer-dual",  # Records both legs of the call
        recording_status_callback="/recording-status",
        recording_status_callback_method="POST"
    )
    dial.number("+1234567890")
    response.append(dial)
    
    return Response(str(response), mimetype='text/xml')

def advanced_gather_example():
    """Advanced gather with speech recognition and hints."""
    response = VoiceResponse()
    
    gather = Gather(
        action="/process-speech",
        method="POST",
        input="speech",
        language="en-US",
        speech_model="experimental_conversations",
        speech_timeout="auto",
        timeout=15,
        hints="sales, support, billing, technical issue, cancel service",
        profanity_filter=True
    )
    gather.say("Please describe your issue in a few words.")
    response.append(gather)
    
    response.say("Sorry, we couldn't understand your request.")
    response.redirect("/answer")
    
    return Response(str(response), mimetype='text/xml')

def recording_with_pause_resume():
    """Example showing pause and resume recording."""
    response = VoiceResponse()
    
    response.say("Starting call recording.")
    response.start_recording()
    
    response.say("Recording is active. Press 1 to pause recording.")
    
    gather = Gather(action="/toggle-recording", num_digits=1)
    response.append(gather)
    
    return Response(str(response), mimetype='text/xml')

# Callback handlers

def handle_recording_callback(request):
    """Process recording status callback."""
    recording_url = request.values.get('RecordingUrl')
    recording_sid = request.values.get('RecordingSid')
    recording_duration = request.values.get('RecordingDuration')
    call_sid = request.values.get('CallSid')
    
    # Save to database or process recording
    print(f"Recording completed: {recording_sid}")
    print(f"Duration: {recording_duration} seconds")
    print(f"URL: {recording_url}")
    
    return "OK", 200

def handle_transcription_callback(request):
    """Process transcription callback."""
    transcription_text = request.values.get('TranscriptionText')
    transcription_status = request.values.get('TranscriptionStatus')
    recording_sid = request.values.get('RecordingSid')
    
    if transcription_status == 'completed':
        print(f"Transcription for {recording_sid}: {transcription_text}")
    
    return "OK", 200