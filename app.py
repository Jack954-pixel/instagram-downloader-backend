from flask import Flask, request, jsonify, send_file
import instaloader
import os
import uuid

app = Flask(__name__)

# Initialize Instaloader
L = instaloader.Instaloader()

# Directory to store downloaded files temporarily
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route("/download", methods=["POST"])
def download_post():
    try:
        # Get the Instagram URL from the form data
        post_url = request.form.get("post_url").strip()

        # Validate URL
        if "instagram.com" not in post_url or not post_url:
            return jsonify({"error": "Invalid Instagram URL"}), 400

        # Extract the shortcode from the URL
        shortcode = post_url.split("/")[-2]

        # Define a unique folder name to avoid conflicts
        unique_id = str(uuid.uuid4())
        target_folder = os.path.join(DOWNLOAD_FOLDER, unique_id)
        os.makedirs(target_folder)

        # Download the Instagram post
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_folder)

        # Find the downloaded file (image or video)
        for file in os.listdir(target_folder):
            if file.endswith((".jpg", ".mp4")):
                file_path = os.path.join(target_folder, file)

                # Serve the file directly to the client
                return send_file(file_path, as_attachment=True)

        return jsonify({"error": "Failed to download post"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)
