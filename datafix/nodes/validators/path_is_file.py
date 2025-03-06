from datafix.core import Validator, active_session
from pathlib import Path


class PathIsFile(Validator):
    """check if path is a file"""
    required_type = Path

    def validate(self, data):
        # expects pathlib.Path for data
        path = data
        if not path.is_file():
            raise Exception(f'{path} is not a file')


if __name__ == '__main__':
    from datafix.nodes.collectors.paths_in_folder import PathsInFolder
    from datafix.nodes.collectors.current_time import CurrentTime

    PathsInFolder.folder_path = 'C:/'
    active_session.append(CurrentTime)
    active_session.append(PathsInFolder)
    active_session.append(PathIsFile)
    active_session.run()
    print(active_session.report())