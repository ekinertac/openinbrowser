import os
import webbrowser
import tempfile
from pathlib import Path

# Read the HTML template and replace {{IMAGES}} with the dynamically generated images
def create_html_from_template(folder_path, template_path):
    # Supported image extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

    # Get list of images in the folder and its subfolders recursively
    images = []
    for root, dirs, files in os.walk(folder_path):
        images.extend([os.path.join(root, file) for file in files if os.path.splitext(file)[1].lower() in image_extensions])

    # Generate the HTML for the images
    image_html = ""

    images.reverse()

    for idx, image in enumerate(images):
        image_path = Path(image).as_posix()  # Convert to POSIX format for web browsers
        image_name = os.path.basename(image)
        image_html += f'''
        <div class="gallery-item">
            <a href="file:///{image_path}" class="gallery-link" target="_blank">
                <img src="file:///{image_path}" alt="{image_name}" class="gallery-image">
                <div class="image-caption">{image_name}</div>
            </a>
        </div>
        '''

    # Read the HTML template
    with open(template_path, 'r') as template_file:
        html_template = template_file.read()

    # Get the title from the folder name
    title = os.path.basename(folder_path)

    # Replace the token {{IMAGES}} in the template with the generated image HTML
    final_html = html_template.replace('{{IMAGES}}', image_html)
    final_html = final_html.replace('{{TITLE}}', title)

    # Create a temporary HTML file to save the final output
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    with open(temp_file.name, 'w') as f:
        f.write(final_html)

    return temp_file.name

def open_html_in_browser(file_path):
    webbrowser.open(f'file://{file_path}')

if __name__ == "__main__":
    import sys
    folder_path = sys.argv[1]  # Get the folder path from the command line argument
    template_path = os.path.join(os.path.dirname(__file__), 'gallery.html')  # Assume gallery.html is in the same directory as the script
    html_file = create_html_from_template(folder_path, template_path)
    open_html_in_browser(html_file)
