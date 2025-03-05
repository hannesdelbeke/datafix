from datafix.core.collector import Collector
from pathlib import Path


class PathsInFolder(Collector):
    folder_path = None  # settings that control the behavior of the collector

    def collect(self):
        """get all paths in a folder"""
        folder = Path(self.folder_path)
        return [p for p in folder.iterdir()]