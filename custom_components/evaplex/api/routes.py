from urllib.parse import urlencode

AUTHORIZE = "/oauth/authorize"
TOKEN = "/oauth/token"
ME = "/api/v1/users/me"
DEVICES = "/api/v1/devices"

HEADER_IDEMPOTENCY = "Idempotency-Key"
HEADER_REQUEST_ID = "X-Request-Id"


def authorize_url(api_base: str) -> str:
    return f"{api_base}{AUTHORIZE}"


def token_url(api_base: str) -> str:
    return f"{api_base}{TOKEN}"


def device_path(device_id: str) -> str:
    return f"{DEVICES}/{device_id}"


def features_path(device_id: str) -> str:
    return f"{device_path(device_id)}/features"


def feature_config_path(device_id: str, feature: str) -> str:
    return f"{features_path(device_id)}/{feature}/config"


def feature_data_path(device_id: str, feature: str) -> str:
    return f"{features_path(device_id)}/{feature}/data"


def feature_report_path(device_id: str, feature: str, report: str) -> str:
    return f"{features_path(device_id)}/{feature}/reports/{report}"


def feature_action_path(device_id: str, feature: str, action: str) -> str:
    return f"{features_path(device_id)}/{feature}/actions/{action}"


def settings_path(device_id: str) -> str:
    return f"{device_path(device_id)}/settings"


def day_window_query(start: str, end: str) -> str:
    return urlencode({"from": start, "to": end, "bucket": "day"})
