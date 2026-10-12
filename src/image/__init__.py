import logging
import json
import shutil
import os

log = logging.getLogger(__name__)

class ImageError(Exception):
    """imageError"""

class ImageCreationError(Exception):
    """an error occured while serializing and/or saving a image object"""

class Image:
    """a image that will be displayed on the webpage"""
    title: str
    author: str
    image_path: Path

    # def __init__(self, path: Path):
    #     self.load(path)

    def load(self, path: Path):
        """load an Image object from a dir containing an image and a metadata.json file"""
        
        log.info(f"loading photo: {path}")
        try:
            with open(path/"metadata.json", 'r') as f:
                data = json.load(f)
                self.image_path = (path / data["filename"]).relative_to(path.parent.parent.parent) # ummmmmmmmmm
                log.debug(self.image_path)
                self.title = data["title"]
                self.author = data["author"]
        except OSError as err:
            raise ImageError from err
        except json.JSONDecodeError as err:
            raise ImageError from err
        except KeyError as err:
            raise ImageError from err

    def save(self, album_path: Path, title: str, author: str, image_path: Path):
        """save an Image object to a folder containing an image and a metadata.json file"""
        log.info(f"saving a photo: {image_path}")

        path = album_path/title

        try:
            os.mkdir(path)
        except FileExistsError as e:
            log.error(f"{path} already exists!")
            raise ImageCreationError from e
        except OSError as e:
            log.error(f"os error: {e}")
            raise ImageCreationError from e

        try:
            shutil.move(image_path, path/image_path.name)
        except OSError as e:
            log.error(f"couldn't rename <{image_path}> to:<{path/image_path.name}>")
            raise ImageCreationError from e

        self.image_path = path/image_path.name
        self.title = title
        self.author = author

        log.debug(f"creating metadata.json")
        try:
            with open(path/"metadata.json", 'a') as f:
                json.dump({
                    "filename": self.image_path.name,
                    "title": self.title,
                    "author": self.author
                }, f)
        except OSError as error:
            log.error(f"error creating and/or saving matadata.json for: {self.image_path}")
            raise ImageCreationError from error
    
    def get_image_path(self) -> Path:
        return self.image_path
            

class AlbumError(Exception):
    """generic album error"""
class AlbumKeyError(Exception):
    """raised when a key value in the albums metadata is incorrect"""
class AlbumNotFoundError(Exception):
    """raised when an album couldn't be found by path"""

class Album:
    title: str
    authors: str
    images: [Image]
    background: Path
    showcase: bool
    path: Path
    def load(self, path: Path) -> self:
        """load an Album object from a dir containing Images and a metadata.json file"""
        
        log.info(f"loading album: {path}")
        try:
            with open(path/"metadata.json", 'r') as f:
                data = json.load(f)
                self.background = (path / data["background"]).relative_to(path.parent.parent) # ummmmmmmmmm
                self.title = data["title"]
                self.authors = data["authors"]
        except OSError as err:
            log.error(f"error reading album metadata: {err}")
            raise AlbumNotFoundError from err
        except json.JSONDecodeError as err:
            log.error(f"invalid json in album metadata: {err}")
            raise AlbumError from err
        except KeyError as err:
            log.error(f"key not found in album metadata (please update): {err}")
            raise AlbumKeyError from err

        self.images = []
        try:
            posts = [p for p in path.iterdir() if p.is_dir()]
            log.debug(posts)
        except OSError as err:
            raise err
        for post in posts:
            try:
                image = Image()
                image.load(post)
            except Exception as e:
                log.error(f"{post} cannot load: {e}")
                pass
            else:
                log.info(f"added image: <{image.title}> to album: <{self.title}>")
                self.images.append(image)
        
        if path.name=="showcase": self.showcase=True
        else: self.showcase=False
        self.path=path
    
    # def create(self, path: Path, title: str, author: str, images: [Image]):
    #     """save an Image object to a folder containing an image and a metadata.json file"""
    #     log.info(f"creating album: {path}")

    #     path = album_path/title

    #     try:
    #         os.mkdir(path)
    #     except FileExistsError as e:
    #         log.error(f"{path} already exists!")
    #         raise ImageCreationError from e
    #     except OSError as e:
    #         log.error(f"os error: {e}")
    #         raise ImageCreationError from e

    #     try:
    #         shutil.move(image_path, path/image_path.name)
    #     except OSError as e:
    #         log.error(f"couldn't rename <{image_path}> to:<{path/image_path.name}>")
    #         raise ImageCreationError from e

    #     self.image_path = path/image_path.name
    #     self.title = title
    #     self.author = author
    #     self.path = path

    #     log.debug(f"creating metadata.json")
    #     try:
    #         with open(path/"metadata.json", 'a') as f:
    #             json.dump(f, {
    #                 "filename": self.image_path.name,
    #                 "title": self.title,
    #                 "author": self.author
    #             })
    #     except OSError as error:
    #         log.error(f"error creating and/or saving matadata.json for: {self.image_path}")
    #         raise ImageCreationError from error

class AlbumManager:
    albums: [Album]
    path: Path
    def __init__(self, path: Path) -> [Album]:
        self.path=path
        self.update()
    
    def update(self):
        log.info(f"updating AlbumManager")
        self.albums = []
        showcase = None
        try:
            for a in self.path.iterdir():
                log.info(f"loading album: {a}")
                if a.is_dir:
                    try:
                        album = Album()
                        album.load(a)
                        if album.showcase: showcase = album
                        else: self.albums.append(album)
                    except AlbumError as err:
                        raise AlbumError from err
        except OSError as err:
            raise err
    
    def get_albums(self) -> [Album]:
        return self.albums

# def main():
#     """do not run manually pleaseee"""
#     log.info("hello world")
#     import argparse

#     parser = argparse.ArgumentParser()
    
#     parser.add_argument("-v", "--verbose", help="verbose output for debugging purpouses", action="store_true")
    
#     args = parser.parse_args()
    
#     loglevel = logging.INFO
#     if args.verbose: loglevel = logging.DEBUG

#     logging.basicConfig(level=loglevel)