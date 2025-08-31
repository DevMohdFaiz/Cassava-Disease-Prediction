from flask import Flask, render_template, request, url_for, redirect
from pathlib import Path
from helper_functions import run_prediction

app = Flask(__name__)
uploads_folder = 'static/uploads'
Path(uploads_folder).mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = uploads_folder
# Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

@app.route('/', methods= ['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file:
            filepath = Path(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            short_pred, full_pred = run_prediction(filepath)
            return render_template('index.html', filepath=filepath, short_pred= short_pred, full_pred=full_pred)
    return render_template('index.html', prediction=None, uploaded_image=None)

if __name__ == '__main__':
    app.run(debug=True)


