import logging
import os

agent = {
    "log_level": logging.INFO,
    "nivel_paralelismo": 2,
    "total_request": 400,
    "tiempo_espera_sec": 0,
    "use_keep_alive": True,
    "name_file_csv": r"load-tests",
}

post_oauth_token = {
    "Url": "https://api.demo/oauth/token",
    "Host": "api.demo",
    "User_Agent": "pdominguez-load-tests/1.0.0",
    "grant_type": "credentials",
    "client_id": "1988dfdf",
    "client_secret": "aaaaaaaaaaaaaaaaaa",
    "scope": "trasaccion session pages",
}
