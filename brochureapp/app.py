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

        # Convert PDF to images
        pages = convert_from_path(input_path, dpi=200)

        # Create the output PDF with 17x11 pages
        c = canvas.Canvas(output_path, pagesize=(1224, 792))  # 17x11 in points (landscape)

        for i in range(0, len(pages), 2):
            if i < len(pages):
                # First page on the left (8.5x11)
                left_image = pages[i]
                left_temp_path = f"/tmp/left_page_{i}.png"
                left_image.save(left_temp_path, "PNG")
                c.drawImage(left_temp_path, 0, 0, width=612, height=792)  # No padding

            if i + 1 < len(pages):
                # Second page on the right (8.5x11)
                right_image = pages[i + 1]
                right_temp_path = f"/tmp/right_page_{i + 1}.png"
                right_image.save(right_temp_path, "PNG")
                c.drawImage(right_temp_path, 612, 0, width=612, height=792)  # No padding

            c.showPage()

        c.save()
        return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Use PORT env variable or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)
