class EvaplexApiError(Exception):
    def __init__(self, status: int) -> None:
        self.status = status
        super().__init__(f"request failed ({status})")


class EvaplexAuthError(EvaplexApiError):
    pass


class EvaplexRateLimited(EvaplexApiError):
    def __init__(self, status: int, retry_after: int | None) -> None:
        super().__init__(status)
        self.retry_after = retry_after


class EvaplexUnavailable(EvaplexApiError):
    pass
