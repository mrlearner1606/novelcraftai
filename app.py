from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import json

app = Flask(__name__)
SECRET_TOKEN = 'mysecrettoken'

BASE_UPLOAD_DIR = 'uploads'
MAX_SIZE_MB = 10
app.config['MAX_CONTENT_LENGTH'] = MAX_SIZE_MB * 1024 * 1024

for folder in ['sherlockmode', 'gitasahasram']:
    os.makedirs(os.path.join(BASE_UPLOAD_DIR, folder), exist_ok=True)

UPLOAD_PAGE_HTML = '''
<!doctype html>
<html>
<head>
  <title>Upload Files</title>
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

        // Clear textarea and file input
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
  <textarea name="description" placeholder="Upload text (optional)" rows="4" cols="50"></textarea><br><br>
  <button type="button" onclick="uploadForm('form-sm', 'msg-sm')">Upload</button>
</form>
<p id="msg-sm" style="color: green;"></p>

<h2>GitaSahasram</h2>
<form id="form-gs" data-project="gitasahasram" enctype="multipart/form-data">
  <input type="file" name="files" multiple><br><br>
  <textarea name="description" placeholder="Upload text (optional)" rows="4" cols="50"></textarea><br><br>
  <button type="button" onclick="uploadForm('form-gs', 'msg-gs')">Upload</button>
</form>
<p id="msg-gs" style="color: green;"></p>

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
            if ext == '.jpg':
                filename = 'thumbnail.jpg'

            filepath = os.path.join(BASE_UPLOAD_DIR, project, filename)
            file.save(filepath)
            saved_files.append(filename)

    if description:
        content_path = os.path.join(BASE_UPLOAD_DIR, project, 'content.json')
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(description)

    return f"{project.capitalize()} data uploaded. " + (
        f"<a href='/files/{project}/thumbnail.jpg' target='_blank'>Download thumbnail.jpg</a>" if 'thumbnail.jpg' in saved_files else ""
    )



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
