import logging
from requests import get
from requests.exceptions import RequestException
from contextlib import closing


def simple_get(url: str, options) -> bytes:
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    result = b""
    try:
        with closing(get(url, stream=True, **options)) as resp:
            if is_good_response(resp):
                result = resp.content
    except RequestException as e:
        logger = logging.getLogger()
        logger.exception(e)
    finally:
        return result


def is_good_response(resp) -> bool:
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers["Content-Type"].lower()
    return resp.status_code == 200 and content_type is not None and content_type.find("html") > -1
