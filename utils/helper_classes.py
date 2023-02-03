
import config
import requests


class APIException(Exception):
    
    def __init__(self, message, status_code):
        super().__init__(message)
        self.status_code = status_code


class RandomNameGenerator:
    def __init__(self, gender="m", country_code="US"):
        self.gender = gender
        self.country_code = country_code

    def make_api_call(self) -> tuple:
        payload = {"api_key": config.API_KEY,
                   "endpoint": "generate",
                   "gender": self.gender,
                   "country_code": self.country_code,
                   }

        # Counter for retries
        retries = 0

        # Maximum number of retries
        max_retries = 3

      
        response = None

        while retries < max_retries:
            try:
                response = requests.get(config.URL,
                                        params=payload)
                response.raise_for_status()
                # If the request was successful, break out of the while loop
                break

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                retries += 1
                if retries == max_retries:
                    # Raise an exception if the maximum number of retries is reached
                    raise APIException("Connection/Timeout error", 503)

            except requests.exceptions.RequestException as e:
                raise APIException(str(e), 500)

        body = response.json()

        name = body["data"][0]["name"]
        first_name = name["firstname"]["name"] if name["firstname"] else "NULL"
        last_name = name["lastname"]["name"] if name["lastname"] else "NULL"

        return first_name, last_name
