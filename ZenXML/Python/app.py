from flask import Flask, render_template_string, request, send_file, redirect, url_for
import xml.etree.ElementTree as ET
import os
import io
import csv
import json
import tempfile

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ZenXML – Universal XML Attribute Remover</title>
  <meta name="viewport" content="width=900, initial-scale=1">
  <link rel="icon" type="image/svg+xml" href="{{ url_for('static_files', filename='zenxml-favicon.svg') }}">
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; max-width:850px; margin:40px auto; background:#eaf6fb; color:#335; font-size: clamp(0.99em, 2vw, 1.13em);}
    .main { background:#fff; border-radius:18px; box-shadow:0 4px 24px #b4dbfb; padding:40px 48px 28px 48px; margin-top: 40px;}
    .logo-header { text-align: center; margin-bottom: 0; }
    .logo-header img { max-width: 220px; width: 90%; min-width: 110px; margin-bottom: 6px;}
    .quote { color:#3a8edb; font-style:italic; margin:16px 0 28px 0; font-size:1.1em; text-align:center; min-height:28px;}
    form { margin-bottom: 20px; }
    .explainer { color:#497ca5; background:#f2f8fd; border-radius:9px; padding:11px 14px; margin: 18px 0 30px 0; font-size:0.65em; border-left:4px solid #3a8edb; text-align:left; line-height:1.5;}
    .option-section { margin-top: 32px; margin-bottom: 14px;}
    .option-row { display: flex; align-items: center; gap: 18px; margin-bottom: 7px; margin-top: 5px;}
    .option-row label { font-size:1em; color:#497ca5; cursor:pointer; }
    .output-label { font-size:1em; font-weight:600; color:#3a8edb; margin-bottom:6px; display:block; margin-left:2px;}
    .format-select { font-size:1em; border-radius:5px; border:1px solid #b5d8ef; padding:3px 10px 3px 7px; background:#fafdff; color:#335; margin-right:8px;}
    .btn { background:#3a8edb; color:#fff; border:none; border-radius:6px; font-size:17px; padding:13px 40px; margin-top:20px; cursor:pointer; box-shadow: 0 2px 8px #b7d8f2af; display: block; font-weight:600; letter-spacing: 0.03em;}
    .btn:hover { background:#22598f;}
    .cbx { transform: scale(1.2);}
    a.btn { text-decoration:none; display:inline-block; margin: 18px 0 0 0;}
    .footer { margin-top: 40px; color: #b3c7d9; font-size: 0.55em; text-align: center; line-height: 1.5; letter-spacing: 0.01em;}
    .footer .socials { margin-top:10px; }
    .footer a.social { display:inline-block; margin:0 9px; text-decoration:none; color:#3a8edb; font-size:1.28em; vertical-align:middle; transition:color 0.2s;}
    .footer a.social:hover { color:#206ab4; }
    #download-link { display: none; }
  </style>
</head>
<body>
  <div class="main">
    <div class="logo-header">
      <img src="{{ url_for('static_files', filename='zenxml-logo.png') }}" alt="ZenXML Logo">
    </div>
    <div class="quote" id="quote">ZenXML: Find peace in your data.</div>
    <form method="POST" enctype="multipart/form-data">
      <div class="explainer" style="font-size:0.70em; color:#497ca5;">
        This tool removes all attributes from every XML tag, no matter what the tag is called. Example: <code>&lt;data attachment="letgo"&gt;</code> becomes <code>&lt;data&gt;</code> – because even data needs to let go of attachments.
      </div>
      <input type="file" name="xmlfile" accept=".xml" required>
      <div class="option-section">
        <div style="margin-left:32px;">
          <div class="option-row">
            <label>
              <input type="checkbox" class="cbx" name="remove_empty" value="yes" {% if remove_empty %}checked{% endif %}>
              Remove all empty attributes?
            </label>
          </div>
          <div style="font-size:0.55em; font-style:italic; color:#497ca5; text-align:left; margin-top:6px; margin-left:8px;">
            *If checked, also removes empty attributes like <code>foo=""</code> for extra cleaning and works for any XML—nested or flat.
          </div>
        </div>
        <div style="text-align:center; margin-top:24px;">
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
          <button type="submit" class="btn" style="min-width:160px;">
            Zen out!
          </button>
        </div>
      </div>
    </form>
    {% if download_link %}
    <div style="display:flex; justify-content:center;">
      <a class="btn" href="{{ download_link }}">Download cleaned {{ output_format.upper() }}</a>
    </div>
    {% endif %}
    <div class="footer">
      <div>
        <a href="mailto:support@blackwell-tech.online" class="social" title="Email">&#9993;</a>
        <a href="https://buymeacoffee.com/blackwelltech" class="social" target="_blank" title="Buy Me a Coffee">&#9749;</a>
        <a href="https://twitter.com/socializedmedia" class="social" target="_blank" title="Twitter / X">&#120143;</a>
      </div>
      <div style="margin-top:6px;">
        A Blackwell Tech Project &bull; Powered by Zachary Network Solutions<br>
        Designed by The Socialized Media Group
      </div>
    </div>
  </div>
</body>
</html>
'''

# --------- Core XML logic functions ---------

def remove_all_attributes(elem, remove_empty=False):
    # Remove all attributes, or only empty ones if specified
    attribs = list(elem.attrib.keys())
    for key in attribs:
        if remove_empty:
            if elem.attrib[key] == "":
                elem.attrib.pop(key)
        else:
            elem.attrib.pop(key)
    for child in elem:
        remove_all_attributes(child, remove_empty)

def elem_to_dict(elem):
    # Recursive XML-to-dict (JSON) converter
    d = {}
    children = list(elem)
    if children:
        dd = {}
        for child in children:
            child_dict = elem_to_dict(child)
            tag = child.tag
            if tag in dd:
                if not isinstance(dd[tag], list):
                    dd[tag] = [dd[tag]]
                dd[tag].append(child_dict[tag])
            else:
                dd[tag] = child_dict[tag]
        d[elem.tag] = dd
    else:
        d[elem.tag] = elem.text.strip() if elem.text else ""
    return d

def xml_to_csv_rows(elem, path=""):
    rows = []
    this_path = f"{path}/{elem.tag}" if path else elem.tag
    # Get value if only text, no children
    value = elem.text.strip() if elem.text and len(list(elem)) == 0 else ""
    row = {
        "Tag": elem.tag,
        "Path": this_path,
        "Value": value
    }
    rows.append(row)
    for child in elem:
        rows.extend(xml_to_csv_rows(child, this_path))
    return rows

@app.route("/", methods=["GET", "POST"])
def index():
    download_link = None
    output_format = "xml"
    remove_empty = False

    if request.method == "POST":
        f = request.files.get("xmlfile")
        if not f:
            return render_template_string(HTML, download_link=None, output_format=output_format, remove_empty=remove_empty)
        xml_data = f.read().decode("utf-8")

        output_format = request.form.get("output_format", "xml")
        remove_empty = bool(request.form.get("remove_empty"))

        # Parse XML
        try:
            tree = ET.ElementTree(ET.fromstring(xml_data))
        except Exception as e:
            return f"Invalid XML: {e}"

        root = tree.getroot()
        remove_all_attributes(root, remove_empty=remove_empty)

        # Temp file for download
        temp = tempfile.NamedTemporaryFile(delete=False, suffix="." + output_format)
        filename = os.path.basename(f.filename).rsplit('.',1)[0] + "_cleaned." + output_format
        # Handle output
        if output_format == "xml":
            tree.write(temp.name, encoding="utf-8", xml_declaration=True)
            temp.flush()
            temp.close()
        elif output_format == "json":
            obj = elem_to_dict(root)
            temp.write(json.dumps(obj, indent=2).encode("utf-8"))
            temp.flush()
            temp.close()
        elif output_format == "csv":
            temp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", encoding="utf-8", newline="")
            rows = xml_to_csv_rows(root)
            fieldnames = ["Tag", "Path", "Value"]
            writer = csv.DictWriter(temp, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            temp.flush()
            temp.close()
        download_link = url_for("download_file", filename=os.path.basename(temp.name), outfilename=filename)

        return render_template_string(HTML, download_link=download_link, output_format=output_format, remove_empty=remove_empty)

    return render_template_string(HTML, download_link=None, output_format="xml", remove_empty=False)

@app.route("/download/<filename>")
def download_file(filename):
    outfilename = request.args.get("outfilename") or filename
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    if not os.path.isfile(file_path):
        return "File not found", 404
    return send_file(file_path, as_attachment=True, download_name=outfilename)

# Serve your logo and favicon from /static_files/
@app.route('/static_files/<path:filename>')
def static_files(filename):
    return send_file(os.path.join("static", filename))

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(debug=True, port=5000)
