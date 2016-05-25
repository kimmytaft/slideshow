import os
from werkzeug import secure_filename
from flask import Flask, render_template, session, g, abort, flash, request, redirect, url_for, send_from_directory

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = '/home/taftk2/CS_Support/jinja/static/pictures'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'tiff', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route("/upload")
def upload_file():
    return render_template('upload.html')

@app.route("/upload", methods=['POST'])
def upload_picture():
    pic=request.files['file']
    if pic and allowed_file(pic.filename):
        filename = secure_filename(pic.filename)
        pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))
    else:
        return render_template('extension_error.html', extensions=app.config['ALLOWED_EXTENSIONS'])

@app.route('/static/pictures/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/")
def template_test():
    pic_list = [f for f in os.listdir("static/pictures/") if os.path.isfile(f)]
    return render_template('displaypic.html')

if __name__ == '__main__':
    app.run(debug=True)
