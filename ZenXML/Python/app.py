from flask import Flask, render_template_string, request, send_file
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ZenXML – Universal XML Attribute Remover</title>
  <meta name="viewport" content="width=900, initial-scale=1">
  <link rel="icon" type="image/svg+xml" href="{{ url_for('static', filename='zenxml-favicon.svg') }}">
  <style>
    body {
      font-family: 'Segoe UI', Arial, sans-serif;
      max-width:850px; margin:40px auto;
      background:#eaf6fb; color:#335;
      transition: background 0.3s, color 0.3s;
      font-size: clamp(0.99em, 2vw, 1.13em);
    }
    body.dark {
      background:#232942; color:#eaf6fb;
    }
    .main {
      background:#fff; border-radius:18px;
      box-shadow:0 4px 24px #b4dbfb; padding:40px 48px 28px 48px;
      transition: background 0.3s, color 0.3s;
      margin-top: 40px;
    }
    body.dark .main {
      background:#2a3251; color:#eaf6fb;
      box-shadow:0 4px 18px #111a3466;
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
    }
    .quote { color:#3a8edb; font-style:italic; margin:16px 0 28px 0; font-size:1.1em; text-align:center; min-height:28px;}
    body.dark .quote { color:#9ad3f8; }
    form { margin-bottom: 20px; }
    .explainer {
      color:#497ca5; background:#f2f8fd; border-radius:9px;
      padding:11px 14px; margin: 18px 0 30px 0; font-size:0.85em;
      border-left:4px solid #3a8edb;
      text-align:left;
      line-height:1.5;
    }
    body.dark .explainer { color:#b8dfff; background:#23345a; border-left:4px solid #54baff;}
    .option-section {
      margin-top: 32px;
      margin-bottom: 14px;
    }
    .option-row {
      display: flex; align-items: center; gap: 18px; margin-bottom: 7px; margin-top: 5px;
    }
    .option-row label { font-size:1em; color:#497ca5; cursor:pointer; }
    body.dark .option-row label { color:#a3d8fc; }
    .output-label {
      font-size:1em; font-weight:600; color:#3a8edb; margin-bottom:6px; display:block; margin-left:2px;
    }
    body.dark .output-label { color:#88c6fc; }
    .format-select {
      font-size:1em; border-radius:5px; border:1px solid #b5d8ef;
      padding:3px 10px 3px 7px; background:#fafdff; color:#335; margin-right:8px;
    }
    body.dark .format-select {
      background:#232942; color:#eaf6fb; border:1px solid #497ca5;
    }
    .btn {
      background:#3a8edb; color:#fff; border:none;
      border-radius:6px; font-size:17px; padding:13px 40px;
      margin-top:20px; cursor:pointer; box-shadow: 0 2px 8px #b7d8f2af;
      display: block;
      font-weight:600;
      letter-spacing: 0.03em;
    }
    .btn:hover { background:#22598f;}
    body.dark .btn { background:#54baff; color:#222;}
    .cbx { transform: scale(1.2);}
    a.btn { text-decoration:none; display:inline-block; margin: 18px 0 0 0;}
    .theme-toggle {
      float:right; background:#fff; color:#3a8edb; border:1px solid #a6cdf2;
      padding:3px 11px; border-radius:10px; font-size:1.1em; cursor:pointer;
      transition: background 0.2s; z-index:22; box-shadow: 0 1px 6px #e4f0fb60;
      margin-left:10px;
    }
    .theme-toggle:hover { background:#d1e8fa; color:#4691d6; }
    body.dark .theme-toggle {
      background:#273357; color:#95ccfd; border:1px solid #478fca;
    }
    .footer {
  margin-top: 40px;
  color: #b3c7d9;
  font-size: 0.7em !important;
  text-align: center;
  line-height: 1.5;
  letter-spacing: 0.01em;
}
    body.dark .footer { color: #b8dbf6; }
    .footer .socials { margin-top:10px; }
    .footer a.social {
      display:inline-block; margin:0 9px;
      text-decoration:none; color:#3a8edb; font-size:1.28em; vertical-align:middle;
      transition:color 0.2s;
    }
    .footer a.social:hover { color:#206ab4; }
    body.dark .footer a.social { color: #54baff;}
    #download-link { display: none; }
    /* --- Responsive Improvements --- */
    @media (max-width: 950px) {
      .main { padding: 12px 2vw 12px 2vw; }
      body { max-width: 98vw; }
    }
    @media (max-width: 700px) {
      .main {
        padding: 8px 0 8px 0;
        border-radius: 10px;
        box-shadow: 0 1px 6px #b4dbfb;
      }
      .logo-header img {
        max-width: 160px;
        min-width: 70px;
        width: 60vw;
      }
      .explainer {
        font-size: 0.95em;
        padding: 10px 6px;
        margin: 10px 0 16px 0;
      }
      .option-section { margin-top: 18px; }
    }
    @media (max-width: 480px) {
      .main {
        padding: 3px 0 3px 0;
        border-radius: 6px;
      }
      .logo-header img {
        max-width: 110px;
        min-width: 44px;
        width: 70vw;
      }
      .explainer {
        font-size: 1em;
        padding: 7px 2px;
      }
      .btn {
        font-size: 15px;
        padding: 9px 15px;
      }
    }
  </style>
  <script>
    function toggleTheme() {
      document.body.classList.toggle('dark');
      document.cookie = "zenxml_theme=" + (document.body.classList.contains('dark') ? 'dark' : 'light') + ";path=/";
      document.getElementById('themeToggle').textContent = document.body.classList.contains('dark') ? "☀️" : "🌙";
    }
    window.onload = function() {
      var match = document.cookie.match(/zenxml_theme=(dark|light)/);
      if (match && match[1] === "dark") {
        document.body.classList.add("dark");
        document.getElementById('themeToggle').textContent = "☀️";
      }
      fetch('https://zenquotes.io/api/random')
        .then(response => response.json())
        .then(data => {
          document.getElementById('quote').textContent = `"${data[0].q}" —${data[0].a}`;
        })
        .catch(() => {
          document.getElementById('quote').textContent = "ZenXML: Flatten the curve—of your data structure.";
        });
    }
  </script>
</head>
<body>
  <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()" aria-label="Toggle dark mode">🌙</button>
  <div class="main">
    <div class="logo-header">
      <img src="{{ url_for('static', filename='zenxml-logo.png') }}" alt="ZenXML Logo">
    </div>
    <div class="quote" id="quote">ZenXML: Find peace in your data.</div>
    <form method="post" enctype="multipart/form-data">
      <div class="explainer" style="font-size:0.85em; color:#497ca5;">
        This tool removes all attributes from every XML tag, no matter what the tag is called. Example: <code>&lt;data attachment="letgo"&gt;</code> becomes <code>&lt;data&gt;</code> – because even data needs to let go of attachments.
      </div>
      <input type="file" name="xmlfile" accept=".xml" required>
      <div class="option-section">
        <div style="margin-left:32px;">
          <div class="option-row">
            <label>
              <input type="checkbox" class="cbx" name="remove_empty" value="yes">
              Remove all empty attributes?
            </label>
          </div>
          <div style="font-size:0.85em; font-style:italic; color:#497ca5; text-align:left; margin-top:6px; margin-left:8px;">
            *If checked, also removes empty attributes like <code>foo=""</code> for extra cleaning and works for any XML—nested or flat.
          </div>
        </div>
        <div style="text-align:center; margin-top:24px;">
          <label class="output-label" for="output_format" style="display:inline-block; margin-bottom:6px;">
            Output selector
          </label><br>
          <select name="output_format" class="format-select" id="output_format" style="display:inline-block;">
            <option value="xml" selected>XML</option>
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
          </select>
        </div>
        <div style="display:flex; justify-content:center; align-items:center; margin-top:18px;">
          <button type="submit" class="btn" style="min-width:160px;">
            Zen out!
          </button>
        </div>
      </div>
    </form>
    {% if outfn %}
      <div style="display:flex; justify-content:center;">
        <a class="btn" href="{{ url_for('download', fname=outfn) }}">Download cleaned {{ outfmt }}</a>
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

def clean_xml(xml_str, remove_empty):
    try:
        parser = ET.XMLParser(encoding="utf-8")
        root = ET.fromstring(xml_str, parser=parser)
        for elem in root.iter():
            # Remove all attributes
            elem.attrib.clear()
        # Optionally, remove empty elements if requested
        if remove_empty:
            def remove_empty_children(parent):
                for child in list(parent):
                    remove_empty_children(child)
                    # Remove if empty (no attrib, no text, no children)
                    if (not child.attrib) and (child.text is None or not child.text.strip()) and (len(child) == 0):
                        parent.remove(child)
            remove_empty_children(root)
        xml_bytes = ET.tostring(root, encoding='utf-8')
        parsed = minidom.parseString(xml_bytes)
        pretty_xml = parsed.toprettyxml(indent="  ", encoding='utf-8')
        # Remove xml declaration to match style
        pretty_xml = b"\n".join(pretty_xml.split(b"\n")[1:]).decode('utf-8')
        return pretty_xml
    except Exception as e:
        return xml_str  # fallback if error (so you see something)

@app.route("/", methods=["GET", "POST"])
def index():
    outfn = None
    outfmt = None
    if request.method == "POST":
        file = request.files['xmlfile']
        remove_empty = 'remove_empty' in request.form
        outfmt = request.form.get('output_format', 'xml')
        content = file.read().decode('utf-8')
        cleaned = clean_xml(content, remove_empty)
        fname = file.filename
        dot = fname.rfind('.')
        base = fname[:dot] if dot != -1 else fname
        if outfmt == "xml":
            output_bytes = cleaned.encode('utf-8')
            newfn = f"{base}_cleaned.xml"
        elif outfmt == "json":
            output_bytes = b'{"message": "JSON output is coming soon!"}'
            newfn = f"{base}_cleaned.json"
        elif outfmt == "csv":
            output_bytes = b"CSV output is coming soon!"
            newfn = f"{base}_cleaned.csv"
        else:
            output_bytes = cleaned.encode('utf-8')
            newfn = f"{base}_cleaned.xml"
        with open(newfn, "wb") as f:
            f.write(output_bytes)
        outfn = newfn
    return render_template_string(HTML, outfn=outfn, outfmt=(outfmt or '').upper())

@app.route("/download/<fname>")
def download(fname):
    return send_file(fname, as_attachment=True)

# Serve static files for logo and favicon
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_file(os.path.join('static', filename))

if __name__ == "__main__":
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(host="0.0.0.0", port=8080)
