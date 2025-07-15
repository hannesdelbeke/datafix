from datafix.core import Validator
from pathlib import Path


class NodelessValidator(Validator):
    """
    Example of a validator that doesn't require a Collector.
    usually the 'logic' method of a validator would only run if any data was collected
    """
    required_type = Path

    def run(self):
        # to validate without a collector,
        # override the _run method instead of the logic method
        ...

