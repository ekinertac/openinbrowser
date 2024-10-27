import os
import signal
import sys
import time
import threading
import webbrowser
from pathlib import Path
from flask import Flask, jsonify, send_from_directory, render_template
from flask_socketio import SocketIO, emit

# Initialize Flask and SocketIO
app = Flask(__name__, static_folder="static")
socketio = SocketIO(app)
folder_path = None  # Variable to store the root folder path
exit_flag = False  # Flag to signal server shutdown


# Endpoint to serve images and folders as JSON data
@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        if not folder_path or not Path(folder_path).is_dir():
            raise ValueError(f"Invalid or missing folder path: {folder_path}")

        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        items = []

        print(f"Listing items in root folder: {folder_path}")
        for item in Path(folder_path).iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                file_path = item.relative_to(folder_path).as_posix()
                print(f"Found image file: {file_path}")
                items.append(
                    {
                        "type": "file",
                        "name": item.name,
                        "path": f"images/{file_path}",
                    }
                )
            elif item.is_dir():
                collage_images = []
                for sub_item in item.iterdir():
                    if (
                        sub_item.is_file()
                        and sub_item.suffix.lower() in image_extensions
                    ):
                        file_path = sub_item.relative_to(folder_path).as_posix()
                        collage_images.append(f"images/{file_path}")
                        print(f"Adding collage preview image: {file_path}")
                    if len(collage_images) == 9:
                        break
                relative_folder_path = item.relative_to(folder_path).as_posix()
                print(f"Found folder: {relative_folder_path} with preview images")
                items.append(
                    {
                        "type": "folder",
                        "name": item.name,
                        "path": f"folder/{relative_folder_path}",
                        "preview_images": collage_images,
                    }
                )

        items.reverse()  # Optional: reverse order for display
        return jsonify(items)
    except Exception as e:
        print(f"Error retrieving items: {str(e)}")
        return jsonify({"error": str(e)}), 500


# Serve individual images
@app.route("/images/<path:filename>")
def serve_image(filename):
    print(f"Serving image: {filename}")
    return send_from_directory(folder_path, filename)


# API endpoint to serve folder contents as JSON for dynamic loading
@app.route("/api/folder/<path:folder_path>")
def api_serve_folder(folder_path):
    print(f"Accessing folder: {folder_path}")
    absolute_path = Path(folder_path)
    if not absolute_path.is_dir():
        print(f"Folder not found: {folder_path}")
        return jsonify({"error": "Folder not found."}), 404

    folder_items = []
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

    for item in absolute_path.iterdir():
        if item.is_file() and item.suffix.lower() in image_extensions:
            relative_image_path = f"images/{folder_path}/{item.name}"
            print(f"Adding image from folder: {relative_image_path}")
            folder_items.append(
                {
                    "type": "file",
                    "name": item.name,
                    "path": relative_image_path,
                }
            )
        elif item.is_dir():
            relative_folder_path = f"{folder_path}/{item.name}"
            print(f"Found subfolder: {relative_folder_path}")
            folder_items.append(
                {
                    "type": "folder",
                    "name": item.name,
                    "path": f"folder/{relative_folder_path}",
                }
            )

    return jsonify({"items": folder_items})


# Render HTML template for the gallery
@app.route("/")
def gallery():
    items = get_items().json  # Get item paths and data for rendering in the template
    if "error" in items:
        print("Error loading gallery items")
        return items["error"], 500

    print("Rendering main gallery page")
    return render_template("gallery.html", TITLE="My Gallery", ITEMS=items)


# Custom "close" event to explicitly set exit flag and shut down the server
@socketio.on("disconnect")
def handle_disconnect():
    global exit_flag
    print("Client disconnected. Setting shutdown flag.")
    exit_flag = True


# Background thread to monitor exit_flag and send SIGTERM to shut down server
def monitor_exit():
    global exit_flag
    while not exit_flag:
        time.sleep(1)
    print("Shutting down server.")
    os.kill(os.getpid(), signal.SIGTERM)  # Send SIGTERM to the current process


if __name__ == "__main__":
    # Get the folder path from the command-line argument
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if not os.path.isdir(folder_path):
            print(f"Error: {folder_path} is not a valid directory.")
            sys.exit(1)
    else:
        print("Usage: python script.py <folder_path>")
        sys.exit(1)

    # Start the exit monitor thread
    threading.Thread(target=monitor_exit, daemon=True).start()

    # Open the browser only if this is the initial run
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        url = "http://127.0.0.1:5000"
        webbrowser.open(url)

    # Run the SocketIO server
    try:
        print("Starting SocketIO server on port 5000")
        socketio.run(app, port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
