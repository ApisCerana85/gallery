import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

from flask import Flask, request, abort, render_template
from werkzeug.utils import secure_filename
from pathlib import Path
#from dataclasses import dataclass
import argparse
import os
from image import AlbumManager, Image, ImageCreationError
import json

album_mngr = AlbumManager(Path(__file__).parent/"static"/"photos")

app = Flask(__name__)
@app.route("/")
def index():
    try:
        albums = album_mngr.get_albums()
    except Exception as e:
        log.error(f"error loading images from path: {e}")
        abort(404, f"error loading images from path: {e}")
    return render_template("index.html", albums=albums)

TEMP_PHOTO_PATH = Path("/tmp/photos/")
CAN_UPLOAD=True
@app.route("/add_photo/", methods=["POST", "GET"])
def add_photo():
    if request.method == "GET":
        return render_template("photo_form.html")

    if not CAN_UPLOAD:
        abort(400, "forbidden")

    title  = request.form.get("title", "").strip()
    album  = request.form.get("album", "").strip()
    author = request.form.get("author", "").strip()
    file   = request.files.get("image")

    if not all([title, album, author]):
        abort(400, "all fields are required")

    if file is None or not file.filename:
        abort(400, "image is required")

    #if len(request.files.getlist("file")) != 1:
    #        log.error(f"only one image at a time supported: <{request.files.getlist("file")}>")
    #        abort(400, f"only one image at a time supported")
    filename = secure_filename(file.filename)

    # try:
    #     data = request.get_json(force=True)["data"]
    #     title = str(data["title"])
    #     author = str(data["author"])
    #     album_title = str(data["album_title"])
    # except (KeyError, json.JSONDecodeError) as e:
    #     log.error(f"invalid metadata: <{data}>")
    #     abort(400, f"invalid metadata: <{e}>")

    for a in album_mngr.get_albums():
        if a.title == album:
            album = a
            break
    if not album: abort(400, f"no such album: <{album}>")

    try: os.makedirs(TEMP_PHOTO_PATH/secure_filename(title))
    except FileExistsError: pass
    filepath = Path(TEMP_PHOTO_PATH)/secure_filename(title)/filename
    file.save(filepath)
    log.info(f"saved: <{filepath}>")

    try:
        Image().save(album.path, title, author, filepath)
    except ImageCreationError as e:
        abort(500, "could not create image")
    album_mngr.update()
    return "OK", 200

@app.route("/update" methods=["GET"])
def update():
    album_mngr.update()
    return "OK", 200

def main():
    # parser = argparse.ArgumentParser()
    
    # parser.add_argument("-v", "--verbose", help="verbose output for debugging purpouses", action="store_true")

    app.run(debug=True)