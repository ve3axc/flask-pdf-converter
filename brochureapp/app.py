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
    # Debugging: Ensure the request contains a file
    if 'file' not in request.files:
        app.logger.error("No file part in the request")
        return "No file part in the request", 400

    file = request.files['file']
    if file.filename == '':
        app.logger.error("No selected file")
        return "No selected file", 400

    if file:
        # Debugging: Log file processing
        app.logger.info(f"Processing file: {file.filename}")

        # Define paths
        input_path = os.path.join(UPLOAD_FOLDER, file.filename)
        output_path = os.path.join(RESULT_FOLDER, f"{os.path.splitext(file.filename)[0]}_17x11.pdf")

        # Debugging: Log file paths
        app.logger.info(f"Input path: {input_path}")
        app.logger.info(f"Output path: {output_path}")

        # Save the uploaded file
        file.save(input_path)

        # Convert PDF to images
        try:
            pages = convert_from_path(input_path, dpi=100)
        except Exception as e:
            app.logger.error(f"Error converting PDF to images: {e}")
            return f"Error processing file: {e}", 500

        # Create the output PDF with 17x11 pages
        try:
            c = canvas.Canvas(output_path, pagesize=(1224, 792))  # 17x11 in points (landscape)

            for i in range(0, len(pages), 2):
                if i < len(pages):
                    # First page on the left
                    left_image = pages[i]
                    left_temp_path = f"/tmp/left_page_{i}.png"
                    left_image.save(left_temp_path, "PNG")
                    c.drawImage(left_temp_path, 0, 0, width=612, height=792)  # No padding

                if i + 1 < len(pages):
                    # Second page on the right
                    right_image = pages[i + 1]
                    right_temp_path = f"/tmp/right_page_{i + 1}.png"
                    right_image.save(right_temp_path, "PNG")
                    c.drawImage(right_temp_path, 612, 0, width=612, height=792)  # No padding

                c.showPage()

            c.save()
        except Exception as e:
            app.logger.error(f"Error creating 17x11 PDF: {e}")
            return f"Error creating output file: {e}", 500

        # Debugging: Confirm output file existence
        if not os.path.exists(output_path):
            app.logger.error(f"Output file not found: {output_path}")
            return "Failed to create output file", 500

        app.logger.info(f"File successfully converted and saved to: {output_path}")
        return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)

    # Debugging: Ensure the paths are logged
    app.logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    app.logger.info(f"Result folder: {RESULT_FOLDER}")

    # Start the server
    port = int(os.environ.get('PORT', 5000))  # Use PORT env variable or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)
