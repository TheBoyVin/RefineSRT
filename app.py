import os
from flask import Flask, render_template, request, flash, redirect, url_for, send_file, send_from_directory, send_file, current_app
from werkzeug.utils import secure_filename
from main import Refine

#Specify upload folder and allowed file extensions
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'srt'}

#create flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Kenya@2030'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Ensure the uploaded extension is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#create home route
@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

file_list = []
#create a result route
@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)

        file = request.files['file']
        # If the user does not select a file, filename is empty
        if file.filename == '':
            flash('Please select a file!', category='error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'upload.srt'))
            refine = Refine()
            refine.run()
            flash(f'Refined {refine.short} subtitles of less than 1 second and {refine.long} subtitles of longer than 5 seconds, while {refine.not_adjusted} failed.', category='success')
            #return redirect(url_for('download_file'))
    

        elif file and not allowed_file(file.filename):
            flash('Only .srt files are compatible!', category='error')

    return render_template('home.html')

#Route to download refined srt file
@app.route('/download', methods=['GET', 'POST'])
def download(): 
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    path = './uploads/refined.srt' 
    return  send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001)