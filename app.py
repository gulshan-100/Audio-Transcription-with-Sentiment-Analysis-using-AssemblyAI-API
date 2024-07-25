

from flask import Flask, render_template, request, jsonify
import os
import assemblyai as aai

app = Flask(__name__)

aai.settings.api_key = "api_key"


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file and allowed_file(file.filename):
            filename = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filename)
            
            try:
                # Transcribe the video file
                transcriber = aai.Transcriber()
                transcript = transcriber.transcribe(filename, aai.TranscriptionConfig(sentiment_analysis=True))

                # Process sentiment analysis results
                sentiment_results = []
                for result in transcript.sentiment_analysis:
                    sentiment_results.append({
                        'text': result.text,
                        'sentiment': result.sentiment,
                        'start': result.start,
                        'end': result.end
                    })

                # Clean up the uploaded file
                os.remove(filename)

                return jsonify({'results': sentiment_results})
            except Exception as e:
                return jsonify({'error': str(e)})
        else:
            return jsonify({'error': 'File type not allowed'})
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)