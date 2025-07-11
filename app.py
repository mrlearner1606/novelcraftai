from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import json

app = Flask(__name__)
SECRET_TOKEN = 'mysecrettoken'

BASE_UPLOAD_DIR = 'uploads'
MAX_SIZE_MB = 10
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE_MB * 1024 * 1024  # 10 MB limit

# Ensure project folders exist
for folder in ['sherlockmode', 'gitasahasram']:
    os.makedirs(os.path.join(BASE_UPLOAD_DIR, folder), exist_ok=True)

UPLOAD_PAGE_HTML = '''
<!doctype html>
<title>Upload Files</title>
<h1>Upload Files</h1>

<h2>SherlockMode Upload</h2>
<form method="POST" action="/upload/sherlockmode" enctype="multipart/form-data">
  <input type="file" name="files" multiple required><br><br>
  <textarea name="description" placeholder="Enter text for content_sm.json" rows="4" cols="50"></textarea><br><br>
  <input type="submit" value="Upload to SherlockMode">
</form>

<h2>GitaSahasram Upload</h2>
<form method="POST" action="/upload/gitasahasram" enctype="multipart/form-data">
  <input type="file" name="files" multiple required><br><br>
  <textarea name="description" placeholder="Enter text for content_gs.json" rows="4" cols="50"></textarea><br><br>
  <input type="submit" value="Upload to GitaSahasram">
</form>
'''

@app.route('/', methods=['GET'])
def home():
    return render_template_string(UPLOAD_PAGE_HTML)

@app.route('/upload/<project>', methods=['POST'])
def upload_files(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify({'error': 'Invalid project name'}), 400

    files = request.files.getlist('files')
    description = request.form.get('description', '').strip()

    if not files or len(files) == 0:
        return jsonify({'error': 'No files provided'}), 400

    saved_files = []
    for file in files:
        filepath = os.path.join(BASE_UPLOAD_DIR, project, file.filename)
        file.save(filepath)
        saved_files.append(file.filename)

    if description:
        content_filename = 'content_sm.json' if project == 'sherlockmode' else 'content_gs.json'
        content_path = os.path.join(BASE_UPLOAD_DIR, project, content_filename)
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump({'text': description}, f, ensure_ascii=False, indent=2)

    return f"Uploaded files to {project}: {', '.join(saved_files)}. Text saved."

@app.route('/delete/<project>', methods=['POST'])
def delete_file(project):
    token = request.headers.get('Authorization', '')
    if token != f'Bearer {SECRET_TOKEN}':
        return jsonify({"error": "Unauthorized"}), 403

    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify({'error': 'Invalid project name'}), 400

    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    filepath = os.path.join(BASE_UPLOAD_DIR, project, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'status': 'deleted', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/files/<project>/<filename>', methods=['GET'])
def get_file(project, filename):
    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify({'error': 'Invalid project name'}), 400

    folder_path = os.path.join(BASE_UPLOAD_DIR, project)
    try:
        return send_from_directory(folder_path, filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
