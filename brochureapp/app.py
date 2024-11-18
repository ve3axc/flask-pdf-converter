from flask import Flask, request, render_template, send_file
import os
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/convert', methods=['POST'])
def convert_to_17x11():
    if 'file' not in request.files:
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    if file:
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(RESULT_FOLDER, f"{os.path.splitext(file.filename)[0]}_17x11.pdf")

        # Save the uploaded file
        file.save(input_path)

        # Convert PDF to 17x11 layout
        pages = convert_from_path(input_path, dpi=300)
        c = canvas.Canvas(output_path, pagesize=(1224, 792))  # Landscape: 17x11 inches
        positions = [(36, 36), (612 + 36, 36)]  # Left and right sides

        for i in range(0, len(pages), 2):
            for j in range(2):  # Process two pages per 17x11 sheet
                if i + j < len(pages):
                    page_image = pages[i + j]
                    x, y = positions[j]
                    temp_image_path = f"/tmp/page_{i + j}.png"
                    page_image.save(temp_image_path, "PNG")
                    c.drawImage(temp_image_path, x, y, width=576, height=756)
            c.showPage()
        c.save()

        return send_file(output_path, as_attachment=True)

# This is the part you need to add
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Use PORT env variable or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)
