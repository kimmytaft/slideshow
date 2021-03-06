import os
import json
from werkzeug import secure_filename
from flask import (Flask, Response, render_template, request, redirect,
        url_for, send_from_directory)

app = Flask(__name__)

app_dir = os.path.join(os.path.dirname(__file__))

app.config['UPLOAD_METADATA'] = os.path.join(app_dir, 'static/metadata.json')
app.config['UPLOAD_FOLDER'] = os.path.join(app_dir, 'static/pictures')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'tiff', 'tif', 'gif', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def duplicate_file(filename):
    metadata = json.load(open(app.config['UPLOAD_METADATA']))
    for item in metadata['pictures']:
        if os.path.basename(item['path']) == filename:
            return True
    return False

@app.route("/delete", methods=['POST', 'GET'])
def delete_picture():
    if request.method == 'GET':
        with open(app.config['UPLOAD_METADATA'], 'r+') as json_file:
            metadata = json.load(json_file)

        pic_array = [os.path.basename(metadata['pictures'][i]['path']) for i in range(len(metadata['pictures']))]
        return render_template('delete.html', pic_array=pic_array)
    else:
        pic=request.form.get('piclist')
        filename = os.path.join(app.config['UPLOAD_FOLDER'], pic)
        metadata = json.load(open(app.config['UPLOAD_METADATA']))

        for item in metadata['pictures']:
            if item['path'] == filename:
                metadata['pictures'].remove(item)
                os.remove(filename)
        with open(app.config['UPLOAD_METADATA'], 'w') as json_file:
            json.dump(metadata, json_file, indent=2)


        return render_template('success.html', message="deleted {} from ".format(pic))

@app.route("/upload", methods=['POST', 'GET'])
def upload_picture():
    if request.method == 'POST':
        duration = 5000
        order = 1
        pic=request.files['file']
        if request.form.get('duration'):
            duration=int(request.form.get('duration'))*1000
        order=int(request.form.get('order') or 1)

        if not pic:
            return render_template('extension_error.html', message="Could not read picture or picture doesn't exist", extensions=app.config['ALLOWED_EXTENSIONS'])
        elif duplicate_file(pic.filename):
            return render_template('extension_error.html', message="Filename already exists", extensions=app.config['ALLOWED_EXTENSIONS'])
        elif allowed_file(pic.filename.lower()):
            filename = secure_filename(pic.filename)
            pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            entry = {}
            entry['path'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            entry['duration'] = duration

            with open(app.config['UPLOAD_METADATA'], 'r+') as json_file:
                metadata = json.load(json_file)
                json_file.seek(0)
                metadata['pictures'].insert((int(order)-1), entry)
                json.dump(metadata, json_file, indent=2)

            return render_template('success.html', message="uploaded {} to ".format(filename))
        else:
            return render_template('extension_error.html', message="Extension not allowed", extensions=app.config['ALLOWED_EXTENSIONS'])
    else:
        return render_template('upload.html')

@app.route('/reorder', methods=['POST', 'GET'])
def reorder_picture():
    if request.method == 'POST':
        jsdata = request.form.getlist('listValues[]')
        if jsdata:
            entry = {}
            entry['path'] = '' 
            entry['duration'] = 2000
            final = {}
            final['pictures'] = []

            for num in range(0, len(jsdata)):
                entry['path'] = jsdata[num].split('"')[1]
                final['pictures'].append(entry.copy())

            with open(app.config['UPLOAD_METADATA'], 'r+') as json_file:
                json.dump(final, json_file, indent=2)

        return render_template('success.html', message="changed the order of ")
    else:
        with open(app.config['UPLOAD_METADATA'], 'r+') as json_file:
            metadata = json.load(json_file)

        pic_array = [metadata['pictures'][i]['path'] for i in range(len(metadata['pictures']))]

        return render_template('reorder.html', pic_array=pic_array)

@app.route('/static/pictures/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/pictures")
def pictures():
    with open(app.config['UPLOAD_METADATA'], 'r') as mf:
        return Response(mf.read(), mimetype='application/json')

@app.route("/")
def slideshow():
    return render_template('displaypic.html')

if __name__ == '__main__':
    debug = True if os.environ.get('SLIDESHOW_DEBUG') else False
    if (not os.path.isfile(app.config['UPLOAD_METADATA']) or os.stat(app.config['UPLOAD_METADATA']).st_size==0):
        json_string = '{"pictures": []}'
        with open(app.config['UPLOAD_METADATA'], 'w') as json_file:
            json_file.write(json_string)

    app.run(debug=debug)
