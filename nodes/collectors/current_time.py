from datafix.collector import Collector


class CurrentTime(Collector):
    def logic(self):
        from datetime import datetime
        return [datetime.now()]
