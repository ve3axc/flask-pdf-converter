import os
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas

def convert_to_17x11():
    # Define the folder on the Desktop
    desktop_path = os.path.expanduser("~/Desktop/print")
    
    if not os.path.exists(desktop_path):
        print(f"Error: The folder '{desktop_path}' does not exist.")
        return

    # Look for PDF files in the folder
    for file_name in os.listdir(desktop_path):
        if file_name.endswith(".pdf") and file_name != "convert_to_17x11.py":
            input_path = os.path.join(desktop_path, file_name)
            output_path = os.path.join(desktop_path, f"{os.path.splitext(file_name)[0]}_17x11.pdf")
            
            # Convert PDF pages to images for rendering
            pages = convert_from_path(input_path, dpi=300)  # High DPI for print quality
            
            if len(pages) < 1:
                print(f"Error: No pages found in '{file_name}'.")
                continue

            # Create the new 17x11 PDF (landscape orientation)
            c = canvas.Canvas(output_path, pagesize=(1224, 792))  # Landscape: 17x11 inches

            # Define positions for 8.5x11 pages on 17x11 layout
            positions = [(36, 36), (612 + 36, 36)]  # Left and right sides

            for i in range(0, len(pages), 2):
                for j in range(2):  # Process two pages per 17x11 sheet
                    if i + j < len(pages):
                        page_image = pages[i + j]
                        x, y = positions[j]
                        
                        # Save the image temporarily for ReportLab
                        temp_image_path = f"/tmp/page_{i + j}.png"
                        page_image.save(temp_image_path, "PNG")
                        
                        # Draw the image onto the canvas
                        c.drawImage(temp_image_path, x, y, width=576, height=756)

                # Complete the current 17x11 page and move to the next
                c.showPage()

            # Save the combined 17x11 PDF
            c.save()
            print(f"Saved combined 17x11 PDF as '{output_path}'")

if __name__ == "__main__":
    convert_to_17x11()
