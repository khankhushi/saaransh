from flask import Flask, request
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline


app = Flask(__name__)

@app.get('/summary')

def sum_api():
    url = request.args.get('url', '') #passing url of the youtube video as an arguement
    video_id = url.split('=')[1]
    summary = fetch_summary(fetch_transcript(video_id))
    return summary, 200

def fetch_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ' '.join([d['text'] for d in transcript_list])
    return transcript

def fetch_summary(transcript)
    summarise = pipeline('summarization')
    summary = ''
    summary = ''
    for i in range(0, (len(transcript)//1000)+1):
        summary_text = summarise(transcript[i*1000:(i+1)*1000])[0]['summary_text']
        summary = summary + summary_text + ' '
    return summary
    

if __name__ == '__main__':
    app.run()