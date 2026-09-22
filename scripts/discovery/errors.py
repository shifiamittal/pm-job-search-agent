"""Shared adapter failure carrying original crawl telemetry."""

class CrawlError(RuntimeError):
    """A failed crawl with its original request and extraction telemetry."""

    def __init__(self, telemetry):
        super().__init__(telemetry["errors"][-1])
        self.telemetry = telemetry
