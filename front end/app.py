from flask import Flask, render_template, request, make_response, jsonify

app = Flask(__name__, template_folder = "templates/", static_folder = "static")
@app.route("/upload-video", methods=["GET", "POST"])
def upload_video():

    if request.method == "POST":

        file = request.files["file"]

        print("File uploaded")
        print(file)

        res = make_response(jsonify({"message": "File uploaded"}), 200)

        return res

    return render_template("upload_video.html")