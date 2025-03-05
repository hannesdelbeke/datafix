from datafix.core.collector import Collector


class CurrentTime(Collector):
    def collect(self):
        from datetime import datetime
        return [datetime.now()]
