# from flask import Flask, request
# from youtube_transcript_api import YouTubeTranscriptApi
# from transformers import pipeline


# app = Flask(__name__)

# @app.get('/summary')

# def summary_api():
#     url = request.args.get('url', '') #passing url of the youtube video as an arguement
#     video_id = url.split('=')[1]
#     summary = get_summary(get_transcript(video_id))
#     return summary, 200

# def get_transcript(video_id):
#     transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
#     transcript = ' '.join([d['text'] for d in transcript_list])
#     return transcript

# def get_summary(transcript)
#     summariser = pipeline('summarization')
#     summary = ''
#     summary = ''
#     for i in range(0, (len(transcript)//1000)+1): 
#         # Transformers api only work upto 1000 characters so dividing transcripts into parts of 1000 then combining them.
#         summary_text = summariser(transcript[i*1000:(i+1)*1000])[0]['summary_text']
#         summary = summary + summary_text + ' '
#     return summary
    

# if __name__ == '__main__':
#     app.run()

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline
import json
from flask import Flask, jsonify, request, abort, Response
import flask as f
import re
from http import HTTPStatus

app = Flask(__name__)

@app.route('/')
def mainpage():
    resp = f.Response("Hello there")
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-CSRF-Token'
    return resp

def Transcript_To_Text(transcript):
    formatter = JSONFormatter()
    json_formatted = formatter.format_transcript(transcript)
    speech_text = json.loads(json_formatted)
    speech_text_string = ""
    for i in speech_text: 
        speech_text_string += i['text']
        speech_text_string += " "
    return speech_text_string

def Text_Summary(script):
    model = T5ForConditionalGeneration.from_pretrained("t5-large")
    tokenizer = T5Tokenizer.from_pretrained("t5-large")
    inputs = tokenizer.encode("summarize: " + script, return_tensors="pt", max_length=512,truncation=True)
    outputs = model.generate(
    inputs, 
    max_length=150, 
    min_length=40, 
    length_penalty=2.0, 
    num_beams=4, 
    early_stopping=True)
    return tokenizer.decode(outputs[0])

def Text_Summary_Default(script):
    summarizer = pipeline('summarization')
    num_iters = int(len(script)/1000)
    summarized_text = []
    for i in range(0, num_iters + 1):
        start = 0
        start = i * 1000
        end = (i + 1) * 1000
        out = summarizer(script[start:end],max_length=20, min_length=10)
        out = out[0]
        out = out['summary_text']
        summarized_text.append(out)
    text = ""
    return text.join(summarized_text)

@app.errorhandler(404)
def handle_exception(e):
    return f'Bad Request! Error: {HTTPStatus(e.code)}, {HTTPStatus(e.code).phrase}'

@app.route('/api/summarize', methods=['GET'])
def api():
    url_yt = request.args.get('youtube_url', None)
    if url_yt==None:
        abort(404)
    x = re.search("watch\?v\=\w+", url_yt)
    v_id = ""
    for i in range(len(x.group())):
        if i>7:
            v_id += x.group()[i]
    transcript = YouTubeTranscriptApi.get_transcript(v_id)
    script = Transcript_To_Text(transcript)
    resp = f.Response(Text_Summary(script))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization, X-CSRF-Token'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)