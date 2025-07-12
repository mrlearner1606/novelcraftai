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
      margin: 5px 0;
    }
    textarea {
      width: 48%;
      display: inline-block;
      vertical-align: top;
    }
    .right-half {
      width: 48%;
      display: inline-block;
      vertical-align: top;
      padding-left: 10px;
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
    .line-item {
      display: flex;
      justify-content: space-between;
      margin-bottom: 4px;
      align-items: center;
    }
    .line-item input[type="radio"] {
      margin-right: 10px;
    }
    .line-text {
      flex-grow: 1;
      margin-right: 10px;
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
        form.querySelector('input[name="files"]').value = '';
      } catch (err) {
        document.getElementById(messageId).innerText = 'Upload failed';
      }
    }

    function copyText(text) {
      navigator.clipboard.writeText(text).then(() => {
        alert("Copied: " + text);
      });
    }

    async function uploadTxtFile(event, project, containerId, messageId) {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`/upload_txt/${project}`, {
        method: 'POST',
        body: formData
      });

      const msg = await response.text();
      document.getElementById(messageId).innerText = msg;

      loadLines(project, containerId);
    }

    async function loadLines(project, containerId) {
      const response = await fetch(`/get_lines/${project}`);
      const lines = await response.json();
      const container = document.getElementById(containerId);
      container.innerHTML = '';

      lines.forEach((line) => {
        const div = document.createElement('div');
        div.className = 'line-item';
        div.innerHTML = `
          <input type="radio" name="line-${containerId}" onclick="removeLine('${project}', \`${line}\`, this)">
          <span class="line-text">${line}</span>
          <button onclick="copyText(\`${line}\`)">Copy</button>
        `;
        container.appendChild(div);
      });
    }

    async function removeLine(project, line, radioEl) {
      const res = await fetch(`/remove_line/${project}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ line: line })
      });

      if (res.ok) {
        radioEl.closest('.line-item').remove();
      } else {
        alert("Failed to remove line.");
      }
    }

    window.onload = () => {
      loadLines('sherlockmode', 'lines-sm');
      loadLines('gitasahasram', 'lines-gs');
    };
  </script>
</head>
<body>
<h1>Upload Panel</h1>

<h2>SherlockMode</h2>
<form id="form-sm" data-project="sherlockmode" enctype="multipart/form-data">
  <input type="file" name="files" multiple><br>
  <div style="display: flex; justify-content: space-between;">
    <textarea name="description" placeholder="Gets saved as content.json" rows="8"></textarea>
    <div class="right-half">
      <input type="file" accept=".txt" onchange="uploadTxtFile(event, 'sherlockmode', 'lines-sm', 'msg-sm')"><br>
      <div id="lines-sm"></div>
    </div>
  </div>
  <button type="button" onclick="uploadForm('form-sm', 'msg-sm')">Upload</button>
</form>
<p id="msg-sm"></p>

<h2>GitaSahasram</h2>
<form id="form-gs" data-project="gitasahasram" enctype="multipart/form-data">
  <input type="file" name="files" multiple><br>
  <div style="display: flex; justify-content: space-between;">
    <textarea name="description" placeholder="Gets saved as content.json" rows="8"></textarea>
    <div class="right-half">
      <input type="file" accept=".txt" onchange="uploadTxtFile(event, 'gitasahasram', 'lines-gs', 'msg-gs')"><br>
      <div id="lines-gs"></div>
    </div>
  </div>
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
                temp_path = os.path.join(save_dir, 'temp_upload.png')
                file.save(temp_path)
                with Image.open(temp_path) as img:
                    rgb_img = img.convert('RGB')
                    jpg_path = os.path.join(save_dir, 'thumbnail.jpg')
                    rgb_img.save(jpg_path, 'JPEG')
                os.remove(temp_path)
                saved_files.append('thumbnail.jpg')
            elif ext == '.jpg':
                filename = 'thumbnail.jpg'
                filepath = os.path.join(save_dir, filename)
                file.save(filepath)
                saved_files.append(filename)
            else:
                filepath = os.path.join(save_dir, filename)
                file.save(filepath)
                saved_files.append(filename)

    if description:
        content_path = os.path.join(BASE_UPLOAD_DIR, project, 'content.json')
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(description)

    return f"{project.capitalize()} data uploaded."

@app.route('/upload_txt/<project>', methods=['POST'])
def upload_txt(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return 'Invalid project', 400

    file = request.files.get('file')
    if not file or not file.filename.endswith('.txt'):
        return 'Invalid file', 400

    save_path = os.path.join(BASE_UPLOAD_DIR, project, 'lines.txt')
    file.save(save_path)
    return 'TXT uploaded', 200

@app.route('/get_lines/<project>', methods=['GET'])
def get_lines(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify([])

    file_path = os.path.join(BASE_UPLOAD_DIR, project, 'lines.txt')
    if not os.path.exists(file_path):
        return jsonify([])

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    return jsonify(lines)

@app.route('/remove_line/<project>', methods=['POST'])
def remove_line(project):
    if project not in ['sherlockmode', 'gitasahasram']:
        return jsonify({'error': 'Invalid project'}), 400

    data = request.get_json()
    line_to_remove = data.get('line', '').strip()
    if not line_to_remove:
        return jsonify({'error': 'No line provided'}), 400

    file_path = os.path.join(BASE_UPLOAD_DIR, project, 'lines.txt')
    if not os.path.exists(file_path):
        return jsonify({'error': 'lines.txt not found'}), 404

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]

    with open(file_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.strip() != line_to_remove:
                f.write(line + '\n')

    return jsonify({'status': 'removed', 'line': line_to_remove})

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
