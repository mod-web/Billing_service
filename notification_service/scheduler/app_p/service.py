import os
import requests
from dotenv import load_dotenv
load_dotenv()


class NotificationService:

    def send_info_json_to_notification(self, **kwargs) -> bool:
        response = requests.post(
            f'http://{os.environ.get("FASTAPI_HOST")}:{os.environ.get("FASTAPI_PORT")}/api/v1/notifications/delayed',
            json=kwargs,
            timeout=5
        )
        if response.status_code is not requests.codes.ok:
            return True
        return False
