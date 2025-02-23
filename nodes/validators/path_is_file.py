import datafix
from datafix.validator import Validator
from pathlib import Path


class PathIsFile(Validator):
    """check if path is a file"""
    required_type = Path

    def logic(self, data):
        # expects pathlib.Path for data
        path = data
        if not path.is_file():
            raise Exception(f'{path} is not a file')


if __name__ == '__main__':
    from nodes.collectors.paths_in_folder import PathsInFolder
    from nodes.collectors.current_time import CurrentTime

    PathsInFolder.folder_path = 'C:/'
    datafix.active_session.add(CurrentTime)
    datafix.active_session.add(PathsInFolder)
    datafix.active_session.add(PathIsFile)
    datafix.active_session.run()
    print(datafix.active_session.report())