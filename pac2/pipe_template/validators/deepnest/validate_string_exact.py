def main(string, match=None):
    """check if string matches another string"""
    match = match or "hello"
    return string == match
