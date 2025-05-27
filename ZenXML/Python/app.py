from flask import Flask, render_template_string, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import os, tempfile, zipfile, io, xml.etree.ElementTree as ET, json, csv

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8MB max upload

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ZenXML – Universal XML Attribute Remover</title>
  <meta name="viewport" content="width=900, initial-scale=1">
  <link rel="icon" type="image/png+xml" href="https://cdn-icons-png.flaticon.com/512/399/399305.png">
  <style>
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      background:#eaf6fb; color:#335;
      font-size: clamp(0.99em, 2vw, 1.13em);
      min-height: 100vh;
    }
    .main {
      max-width: 550px;
      margin: 40px auto 0 auto;
      padding: 40px 30px 28px 30px;
      position: relative;
      background: #fff;
      border-radius: 18px;
      box-shadow: 0 4px 24px #b4dbfb;
      min-height: 560px;
    }
    .logo-header {
      text-align: center;
      margin-bottom: 0;
    }
    .logo-header img {
      max-width: 220px;
      width: 90%;
      min-width: 110px;
      margin-bottom: 6px;
      margin-top: 5px;
    }
    .quote {
      color:#3a8edb; font-style:italic; margin:16px 0 18px 0; font-size:1.1em; text-align:center; min-height:28px;
    }
    .explainer {
      max-width: 600px; width: 95%; min-width: 300px;
      margin: 18px auto 30px auto; font-size: 0.6em; line-height: 1.4;
      padding: 11px 14px;
      border-left: 4px solid #3a8edb;
      background: #f2f8fd;
      border-radius: 9px;
      color: #497ca5;
      text-align: left;
      max-height: 180px;
      overflow-y: auto;
    }
    .quote-text {
      display: block;
      margin-top: 8px;
      font-style: italic !important;
      font-family: Georgia, serif !important;
      color: #2a5d8f;
      border-left: 3px solid #3a8edb;
      padding-left: 12px;
      font-size: 0.9em;
      opacity: 0.85;
      user-select: none;
    }
    .dropzone {
      border:2px dashed #3a8edb;
      border-radius:10px;
      padding:22px;
      text-align:center;
      margin-bottom:14px;
      color:#497ca5;
      background:#f5fafd;
      font-size: 1em;
      user-select: none;
      margin-top: 0;
    }
    .option-section { margin-top: 32px; margin-bottom: 14px; }
    .output-label {
      font-size:1em; font-weight:600; color:#3a8edb; margin-bottom:6px; display:block; margin-left:2px;
    }
    .format-select {
      font-size: 14px; padding: 4px 8px; border-radius: 5px;
      border: 1px solid #b5d8ef; background: #fafdff; color: #335;
      margin-right: 8px; min-width: 100px; text-align: center; box-sizing: border-box;
      transition: border-color 0.2s ease;
    }
    .btn {
      background: #3a8edb; color: #fff; border: none; border-radius: 5px;
      font-size: 14px; padding: 8px 24px; margin-top: 20px; cursor: pointer;
      box-shadow: 0 1px 4px #b7d8f2af; display: block; font-weight: 600;
      letter-spacing: 0.03em; min-width: 120px; transition: background 0.3s ease;
      text-align:center;
    }
    .btn:hover { background: #22598f;}
    .footer {
      margin-top: 40px;
      color: #b3c7d9;
      font-size: 0.55em;
      text-align: center;
      line-height: 1.5;
      letter-spacing: 0.01em;
    }
    .footer a { color: #3a8edb; text-decoration: underline;}
    .footer .socials { margin-top:10px; }
    .footer a.social {
      display:inline-block; margin:0 9px;
      text-decoration:none; color:#3a8edb; font-size:1.28em; vertical-align:middle;
      transition:color 0.2s;
    }
    .footer a.social:hover { color:#206ab4; }
    #download-area { text-align:center; margin-top:22px;}
    #download-area .btn { display: inline-block;}
    #file-list { text-align:center; font-size:0.92em; color:#3a8edb; margin-top:8px;}
    @media (max-width: 700px) {
      .main { padding: 8px 0 8px 0; border-radius: 10px; box-shadow: 0 1px 6px #b4dbfb;}
      .logo-header img { max-width: 160px; min-width: 70px; width: 60vw;}
      .explainer { font-size: 0.60em; padding: 10px 6px; margin: 10px 0 16px 0;}
      .option-section { margin-top: 18px; }
    }
  </style>
</head>
<body>
  <div class="main">
    <div class="logo-header">
      <img src="https://www.blackwell-tech.online/storage/app/media/zenxml-logo.png" alt="ZenXML Logo">
    </div>
    <div class="quote">ZenXML: Find peace in your data.</div>
    <div class="explainer">
      This tool removes all attributes from every XML tag, no matter what the tag is called. Example: <code>&lt;data attachment="letgo"&gt;</code> becomes <code>&lt;data&gt;</code> – 
      <span class="quote-text">=-"because even data needs to let go of attachments".</span>
    </div>
    <form method="POST" enctype="multipart/form-data" autocomplete="off">
      <div class="dropzone">
        <label for="xmlfile" style="cursor:pointer;">
          Drag &amp; drop XML files here, or click to choose files<br>
          <input type="file" name="xmlfile" id="xmlfile" accept=".xml" multiple style="display:none;" required>
          <span id="file-label">
            {% if filenames %}
              <div id="file-list">
                {{ filenames|join(", ") }}
              </div>
            {% else %}
              <span style="color:#497ca5;">No file(s) selected.</span>
            {% endif %}
          </span>
        </label>
      </div>
      <div class="option-section">
        <div style="text-align:center; margin-top:18px;">
          <label class="output-label" for="output_format" style="display:inline-block; margin-bottom:6px;">
            Output selector
          </label><br>
          <select name="output_format" class="format-select" id="output_format" style="display:inline-block;">
            <option value="xml" {% if output_format=='xml' %}selected{% endif %}>XML</option>
            <option value="json" {% if output_format=='json' %}selected{% endif %}>JSON</option>
            <option value="csv" {% if output_format=='csv' %}selected{% endif %}>CSV</option>
          </select>
        </div>
        <div style="display:flex; justify-content:center; align-items:center; margin-top:18px;">
          <button type="submit" class="btn" style="min-width:120px;" name="action" value="zen">
            Zen out!
          </button>
          <button type="submit" class="btn" id="clear-btn" style="min-width:120px; margin-left:12px;" name="action" value="clear">
            Clear
          </button>
        </div>
      </div>
    </form>
    <div id="download-area">
      {% if ready and download_link %}
        <div style="margin-bottom:8px;">Ready! Download your cleaned file{{ 's' if is_zip else '' }}.</div>
        <a class="btn" href="{{ download_link }}" download>{{ download_text }}</a>
      {% endif %}
    </div>
    <div class="footer">
      <div>
        <a href="mailto:support@blackwell-tech.online" class="social" title="Email">&#9993;</a>
        <a href="https://buymeacoffee.com/blackwelltech" class="social" target="_blank" title="Buy Me a Coffee">&#9749;</a>
        <a href="https://twitter.com/socializedmedia" class="social" target="_blank" title="Twitter / X">&#120143;</a>
      </div>
      <div style="margin-top:6px;">
        A
        <a href="https://www.blackwell-tech.online" target="_blank" rel="noopener noreferrer">
          Blackwell Technological Solutions
        </a> Project &bull; 
        Powered by 
        <a href="https://www.zns.support" target="_blank" rel="noopener noreferrer">
          Zachary Network Solutions
        </a><br>
        Designed by 
        <a href="https://www.thesocializedmediagrp.com" target="_blank" rel="noopener noreferrer">
          The Socialized Media Group
        </a>
      </div>
    </div>
  </div>
  <script>
  // Show file names when selected (just UI)
  document.addEventListener('DOMContentLoaded', function() {
    var input = document.getElementById('xmlfile');
    var label = document.getElementById('file-label');
    input.addEventListener('change', function(e){
      if (input.files.length > 0) {
        var names = [];
        for (var i=0;i<input.files.length;i++) names.push(input.files[i].name);
        label.innerHTML = "<div id='file-list'>" + names.join(", ") + "</div>";
      } else {
        label.innerHTML = '<span style="color:#497ca5;">No file(s) selected.</span>';
      }
    });
  });
  </script>
</body>
</html>
"""

def clean_xml(xmlstr):
    try:
        root = ET.fromstring(xmlstr)
        for elem in root.iter():
            elem.attrib.clear()
        return ET.tostring(root, encoding='unicode')
    except Exception:
        return xmlstr

def xml_to_json(xmlstr):
    def elem_to_dict(elem):
        d = {elem.tag: {} if elem.attrib else None}
        children = list(elem)
        if children:
            dd = {}
            for dc in map(elem_to_dict, children):
                for k, v in dc.items():
                    if k in dd:
                        if not isinstance(dd[k], list):
                            dd[k] = [dd[k]]
                        dd[k].append(v)
                    else:
                        dd[k] = v
            d = {elem.tag: dd}
        if elem.text and elem.text.strip():
            text = elem.text.strip()
            if children or elem.attrib:
                if text:
                    d[elem.tag]['text'] = text
            else:
                d[elem.tag] = text
        return d
    try:
        root = ET.fromstring(xmlstr)
        return json.dumps(elem_to_dict(root), indent=2)
    except Exception:
        return '{}'

def xml_to_csv(xmlstr):
    try:
        root = ET.fromstring(xmlstr)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Path', 'Value'])
        def walk(elem, path):
            children = list(elem)
            full_path = path + "/" + elem.tag
            if children:
                for child in children:
                    walk(child, full_path)
            else:
                writer.writerow([full_path, elem.text.strip() if elem.text else ""])
        walk(root, "")
        return output.getvalue()
    except Exception:
        return "Error converting XML to CSV"

@app.route('/', methods=['GET', 'POST'])
def index():
    ready = False
    download_link = ''
    download_text = ''
    is_zip = False
    filenames = []
    output_format = request.form.get("output_format", "xml")

    if request.method == "POST":
        if request.form.get("action") == "clear":
            return redirect(url_for('index'))

        files = request.files.getlist("xmlfile")
        files = [f for f in files if f.filename]
        filenames = [secure_filename(f.filename) for f in files]

        if not files:
            return render_template_string(HTML_TEMPLATE, ready=ready, download_link=download_link,
                download_text=download_text, is_zip=is_zip, filenames=filenames, output_format=output_format)

        cleaned_files = []
        for file in files:
            xmlstr = file.read().decode('utf-8', errors='replace')
            cleaned = clean_xml(xmlstr)
            if output_format == "xml":
                content = cleaned
                ext = ".xml"
            elif output_format == "json":
                content = xml_to_json(cleaned)
                ext = ".json"
            elif output_format == "csv":
                content = xml_to_csv(cleaned)
                ext = ".csv"
            else:
                content = cleaned
                ext = ".xml"
            fname = secure_filename(file.filename)
            base, _ = os.path.splitext(fname)
            cleaned_files.append((base + "_cleaned" + ext, content))

        if len(cleaned_files) == 1:
            filename, content = cleaned_files[0]
            file_stream = io.BytesIO(content.encode('utf-8'))
            file_stream.seek(0)
            download_link = url_for('download_single', filename=filename)
            # Save the file temporarily
            tempdir = tempfile.gettempdir()
            temp_path = os.path.join(tempdir, filename)
            with open(temp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            download_text = f"Download {output_format.upper()} File"
        else:
            is_zip = True
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for filename, content in cleaned_files:
                    zipf.writestr(filename, content)
            zip_buf.seek(0)
            zip_name = "zenxml_cleaned_files.zip"
            # Save the zip temporarily
            tempdir = tempfile.gettempdir()
            zip_path = os.path.join(tempdir, zip_name)
            with open(zip_path, 'wb') as zf:
                zf.write(zip_buf.read())
            download_link = url_for('download_zip')
            download_text = "Download ZIP File"
        ready = True

    return render_template_string(HTML_TEMPLATE, ready=ready, download_link=download_link,
        download_text=download_text, is_zip=is_zip, filenames=filenames, output_format=output_format)

@app.route('/download/<filename>')
def download_single(filename):
    tempdir = tempfile.gettempdir()
    file_path = os.path.join(tempdir, filename)
    return send_file(file_path, as_attachment=True)

@app.route('/download_zip')
def download_zip():
    tempdir = tempfile.gettempdir()
    zip_path = os.path.join(tempdir, "zenxml_cleaned_files.zip")
    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
