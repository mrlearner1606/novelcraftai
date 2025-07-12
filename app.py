from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import json
from PIL import Image

app = Flask(__name__)
SECRET_TOKEN = 'mysecrettoken'

BASE_UPLOAD_DIR = 'uploads'
MAX_SIZE_MB = 20
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE_MB * 1024 * 1024

for folder in ['sherlockmode', 'gitasahasram']:
    os.makedirs(os.path.join(BASE_UPLOAD_DIR, folder), exist_ok=True)

UPLOAD_PAGE_HTML = '''
<!doctype html>
<html>
<head>
  <title>Upload Files</title>
  <style>
    body {
      background-color: #121212;
      color: #ffffff;
      font-family: Arial, sans-serif;
      padding: 20px;
    }
    input[type="file"],
    textarea,
    button {
      background-color: #1e1e1e;
      color: #ffffff;
      border: 1px solid #555;
      border-radius: 4px;
      padding: 8px;
    }
    textarea {
      width: 100%;
    }
    button {
      cursor: pointer;
    }
    button:hover {
      background-color: #333;
    }
    h1, h2 {
      color: #ffcc00;
    }
    p {
      color: #00ff99;
    }
  </style>
  <script>
    async function uploadForm(formId, messageId) {
      const form = document.getElementById(formId);
      const formData = new FormData(form);
      const project = form.getAttribute('data-project');
      const url = `/upload/${project}`;

      try {
        const response = await fetch(url, {
          method: 'POST',
          body: formData
        });
        const resultText = await response.text();
        document.getElementById(messageId).innerText = resultText;

        form.querySelector('textarea').value = '';
        if (form.querySelector('input[type="file"]')) {
          form.querySelector('input[type="file"]').value = '';
        }
      } catch (err) {
        document.getElementById(messageId).innerText = 'Upload failed';
      }
    }
  </script>
</head>
<body>
<h1>Upload Panel</h1>

<h2>SherlockMode</h2>
<form id="form-sm" data-project="sherlockmode" enctype="multipart/form-data">
  <input type="file" name="files" multiple><br><br>
  <textarea name="description" placeholder="Gets saved as content.json" rows="4" cols="50"></textarea><br><br>
  <button type="button" onclick="uploadForm('form-sm', 'msg-sm')">Upload</button>
</form>
<p id="msg-sm"></p>

<h2>GitaSahasram</h2>
<form id="form-gs" data-project="gitasahasram" enctype="multipart/form-data">
  <input type="file" name="files" multiple><br><br>
  <textarea name="description" placeholder="Gets saved as content.json" rows="4" cols="50"></textarea><br><br>
  <button type="button" onclick="uploadForm('form-gs', 'msg-gs')">Upload</button>
</form>
<p id="msg-gs"></p>

</body>
</html>
'''


@app.route('/', methods=['GET'])
def home():
    return render_template_string(UPLOAD_PAGE_HTML)

@app.route('/upload/<project>', methods=['POST'])
def upload_files(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return 'Invalid project name', 400

    files = request.files.getlist('files')
    description = request.form.get('description', '').strip()

    saved_files = []
    for file in files:
        if file.filename:
            filename = file.filename
            ext = os.path.splitext(filename)[1].lower()
            save_dir = os.path.join(BASE_UPLOAD_DIR, project)
            if ext == '.png':
                # Save PNG temporarily
                temp_path = os.path.join(save_dir, 'temp_upload.png')
                file.save(temp_path)
                # Convert to JPG and rename to thumbnail.jpg
                with Image.open(temp_path) as img:
                    rgb_img = img.convert('RGB')
                    jpg_path = os.path.join(save_dir, 'thumbnail.jpg')
                    rgb_img.save(jpg_path, 'JPEG')
                os.remove(temp_path)
                saved_files.append('thumbnail.jpg')
            elif ext == '.jpg':
                # Save directly as thumbnail.jpg
                filename = 'thumbnail.jpg'
                filepath = os.path.join(save_dir, filename)
                file.save(filepath)
                saved_files.append(filename)
            else:
                # Save other files as-is
                filepath = os.path.join(save_dir, filename)
                file.save(filepath)
                saved_files.append(filename)

    if description:
        content_path = os.path.join(BASE_UPLOAD_DIR, project, 'content.json')
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(description)

    return f"{project.capitalize()} data uploaded. "


@app.route('/upload_text/<project>', methods=['POST'])
def upload_text_only(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return 'Invalid project name', 400

    description = request.form.get('description', '').strip()
    if not description:
        return 'No text provided', 400

    content_path = os.path.join(BASE_UPLOAD_DIR, project, 'content.json')
    with open(content_path, 'w', encoding='utf-8') as f:
        f.write(description)

    return f"{project.capitalize()} text uploaded"


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
