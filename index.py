from flask import Flask, request, redirect, render_template, send_file, send_from_directory, after_this_request
from werkzeug.utils import secure_filename
import os
from os.path import basename
import subprocess
import shutil
import zipfile
from zipfile import ZipFile

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        curdir = os.getcwd()
        os.chdir('demucs')

        # strip out the name without the .mp3 so you can make a folder with it
        filename_without_extension = filename.split('.')[0]
        # path for downloaded tracks
        downloaded_directory = os.getcwd() + '/separated/demucs_extra/' + filename_without_extension + '/'

        # execute library commands
        command = 'python3 -m demucs.separate --dl -n demucs_extra -d cpu ../demucs_app/uploads/{filename}'.format(filename=filename)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        process.wait()
        
        

        # zip tracks

        zipped = ZipFile(filename_without_extension + '.zip', 'w', zipfile.ZIP_DEFLATED)
        # with ZipFile(downloaded_directory + filename_without_extension + '.zip', 'w') as zipped:
        for folderName, subfolders, filenames in os.walk(downloaded_directory):
            for filename in filenames:
                filePath = os.path.join(folderName, filename)
                # Add file to zip
                zipped.write(filePath, basename(filePath))
        zipped.close()



        # path of zip file
        zip_file_path = os.getcwd() + '/' + filename_without_extension + '.zip'
        
        #cleanup and remove after download
        file_handle = open(zip_file_path, 'r')
        @after_this_request
        def remove_file(response):
            try:
                # remove wav files
                shutil.rmtree(downloaded_directory)
                # remove compressed version
                os.remove(zip_file_path)
                file_handle.close()
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response
        return send_file(zip_file_path, mimetype='zip', attachment_filename='tracks.zip', as_attachment=True)
        
    return render_template("index.html")


