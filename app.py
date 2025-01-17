from flask import Flask, request, jsonify, send_file
import instaloader
import os
import uuid
import shutil

app = Flask(__name__)

# Initialize Instaloader
L = instaloader.Instaloader()

# Directory to store downloaded files temporarily
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Login to Instagram (optional but recommended for private or restricted posts)
USERNAME = os.getenv("INSTAGRAM_USERNAME")  # Set your Instagram username in environment variables
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")  # Set your Instagram password in environment variables

if USERNAME and PASSWORD:
    try:
        L.login(USERNAME, PASSWORD)
        print("Logged in successfully")
    except instaloader.exceptions.BadCredentialsException:
        print("Error: Invalid Instagram credentials")
    except Exception as e:
        print(f"Login error: {e}")


@app.route("/download", methods=["POST"])
def download_post():
    try:
        # Get the Instagram URL from the request
        post_url = request.form.get("post_url")
        if not post_url or "instagram.com" not in post_url:
            return jsonify({"error": "Invalid Instagram URL"}), 400

        # Extract the shortcode from the URL
        shortcode = post_url.split("/")[-2]

        # Create a unique folder to avoid filename conflicts
        unique_id = str(uuid.uuid4())
        target_folder = os.path.join(DOWNLOAD_FOLDER, unique_id)
        os.makedirs(target_folder)

        # Download the Instagram post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_folder)

        # Find the downloaded file (image or video)
        downloaded_file = None
        for file in os.listdir(target_folder):
            if file.endswith((".jpg", ".mp4")):
                downloaded_file = os.path.join(target_folder, file)
                break

        if not downloaded_file:
            return jsonify({"error": "Failed to download post content"}), 500

        # Serve the downloaded file to the client
        response = send_file(downloaded_file, as_attachment=True)

        # Clean up temporary files after serving the file
        shutil.rmtree(target_folder, ignore_errors=True)

        return response

    except instaloader.exceptions.InstaloaderException as e:
        return jsonify({"error": f"Instaloader error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
