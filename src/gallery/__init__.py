from flask import Flask, request, abort, render_template
from pathlib import Path
#from dataclasses import dataclass
import argparse
import logging
import os
from image import AlbumManager

log = logging.getLogger(__name__)

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
def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-v", "--verbose", help="verbose output for debugging purpouses", action="store_true")
    
    args = parser.parse_args()
    
    loglevel = logging.INFO
    if args.verbose: loglevel = logging.DEBUG

    logging.basicConfig(level=loglevel)

    app.run(debug=True)