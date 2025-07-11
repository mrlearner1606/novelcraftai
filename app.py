from flask import Flask, request, jsonify
import os

app = Flask(__name__)
SECRET_TOKEN = 'mysecrettoken'

BASE_UPLOAD_DIR = 'uploads'
MAX_SIZE_MB = 10
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE_MB * 1024 * 1024  # 10MB

# Ensure folders exist
for folder in ['sherlockmode', 'gitasahasram']:
    os.makedirs(os.path.join(BASE_UPLOAD_DIR, folder), exist_ok=True)

@app.route('/upload/<project>', methods=['POST'])
def upload_file(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify({'error': 'Invalid project name'}), 400

    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file provided'}), 400

    filepath = os.path.join(BASE_UPLOAD_DIR, project, file.filename)
    file.save(filepath)
    return jsonify({'status': 'uploaded', 'filename': file.filename, 'project': project}), 200

@app.route('/delete/<project>', methods=['POST'])
def delete_file(project):
    token = request.headers.get('Authorization', '')
    if token != f'Bearer {SECRET_TOKEN}':
        return jsonify({"error": "Unauthorized"}), 403

    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify({'error': 'Invalid project name'}), 400

    data = request.get_json()
    filename = data.get('filename')
    filepath = os.path.join(BASE_UPLOAD_DIR, project, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'status': 'deleted', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/')
def home():
    return 'SherlockMode & GitaSahasram Upload Server Active'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
