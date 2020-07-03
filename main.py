from flask import Flask, request, render_template, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from amazon_client import upload_file_to_s3, get_faces, get_objects

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = '/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f.filename == "":
            context = {
                "upload_error": True
            }
            return render_template('index.html', **context)
        s3_response = upload_file_to_s3(f)
        if f.filename[-1] == "/":
            f.filename = f.filename[0:-2]
    context = {
        "img_url": s3_response,
        "img_name": f.filename,
    }
    return render_template('index.html', **context)


@app.route('/face-detection', methods=['POST'])
def detect_faces():
    image_name = request.form.get("image_name")
    image_url = request.form.get("image_url")
    if image_name[-1] == "/":
        image_name = image_name[0:-1]
    if image_url[-1] == "/":
        image_url = image_url[0:-1]
    faces = get_faces(image_name)
    context = {
        "img_url": image_url,
        "img_name": image_name,
        "faces": faces,
        "face_detection": True
    }
    return render_template('index.html', **context)

@app.route('/object-detection', methods=['POST'])
def detect_objects():
    image_name = request.form.get("image_name")
    image_url = request.form.get("image_url")
    if image_name[-1] == "/":
        image_name = image_name[0:-1]
    if image_url[-1] == "/":
        image_url = image_url[0:-1]
    labels = get_objects(image_name)
    context = {
        "img_url": image_url,
        "img_name": image_name,
        "labels": labels
    }
    return render_template('index.html', **context)
