from datafix.core import Validator
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
    from datafix.core import get_active_session

    session = get_active_session()
    PathsInFolder.folder_path = 'C:/'
    session.append(CurrentTime)
    session.append(PathsInFolder)
    session.append(PathIsFile)
    session.run()
    print(session.report())