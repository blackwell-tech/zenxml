# ZenXML

**ZenXML** is a universal XML attribute remover, provided in two flavors:
- An instant HTML5 version (runs fully in your browser—no install required).
- A Python Flask web app for self-hosting or advanced integrations.

**Tagline:**  
_Flatten the curve of your data structure. 🧘_

---

## ⚠️ License & Usage Notice

This project is **proprietary**.  
Source code is shared here for demonstration and evaluation purposes **only**.  
**Do not copy, distribute, or reuse any code or assets from this repository without explicit written permission from the owner.**

Recruiters, employers, and potential collaborators:  
Feel free to browse and evaluate my code as part of your review.  
If you’d like to discuss access, contributions, or usage, please contact me directly.

---

## Project Structure

zenxml/
├─ python/
│ ├─ app.py
│ ├─ requirements.txt
│ └─ static/
│ ├─ zenxml-logo.png
│ └─ zenxml-favicon.svg
├─ html/
│ ├─ index.html
│ └─ assets/
│ ├─ zenxml-logo.png
│ └─ zenxml-favicon.svg
├─ README.md
├─ LICENSE.txt


- The `/python` folder contains the **Python Flask** version.
    - To run locally: see instructions below.
- The `/html` folder contains the **HTML5 version**.
    - Just open `index.html` in your browser.

---

## What is ZenXML?

ZenXML is a tool that strips all attributes from every XML tag, no matter what the tag is called—helping your data “let go of attachments” and become more streamlined.

---

## Features

- **HTML5 Version:** Drag-and-drop XML files, remove attributes instantly, works offline.
- **Python Flask Version:** For server use, can be integrated into larger workflows.
- **Clean, modern UI**
- **Theme toggle, fun zen quotes, and more**

---

## Quickstart

### **HTML Version**
1. Go to `/html/` and open `index.html` in your web browser.
2. No install needed!

### **Python Version**
1. Go to `/python/` folder.
2. (Recommended) Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the Flask app:
    ```bash
    python app.py
    ```
5. Open `http://localhost:5000` in your browser.

---

## Demo

*Not hosted publicly at this time.*  
Please contact me for a live demo or preview link.

---

## Contact

**Alyse Z.**  
Blackwell Technological Solutions  
Email: support@blackwell-tech.online

---

## License

See [`LICENSE.txt`](LICENSE.txt) for full terms.


