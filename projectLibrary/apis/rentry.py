"""RENTRY API"""
import http.cookiejar, urllib.parse, urllib.request
from http.cookies import SimpleCookie
from json import loads as json_loads

_headers = {"Referer": "https://rentry.co"}


class UrllibClient:
    def __init__(self):
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        urllib.request.install_opener(self.opener)

    def get(self, url, headers={}):
        request = urllib.request.Request(url, headers=headers)
        return self._request(request)

    def post(self, url, data=None, headers={}):
        postdata = urllib.parse.urlencode(data).encode()
        request = urllib.request.Request(url, postdata, headers)
        return self._request(request)

    def _request(self, request):
        response = self.opener.open(request)
        response.status_code = response.getcode()
        response.data = response.read().decode("utf-8")
        return response


def raw(url):
    client = UrllibClient()
    return json_loads(client.get("https://rentry.co/api/raw/{}".format(url)).data)


def new(url, edit_code, text):
    client, cookie = UrllibClient(), SimpleCookie()
    cookie.load(vars(client.get("https://rentry.co"))["headers"]["Set-Cookie"])
    csrftoken = cookie["csrftoken"].value
    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "url": url,
        "edit_code": edit_code,
        "text": text,
    }
    return json_loads(
        client.post("https://rentry.co/api/new", payload, headers=_headers).data
    )


def edit(url, edit_code, text):
    client, cookie = UrllibClient(), SimpleCookie()
    cookie.load(vars(client.get("https://rentry.co"))["headers"]["Set-Cookie"])
    csrftoken = cookie["csrftoken"].value
    payload = {"csrfmiddlewaretoken": csrftoken, "edit_code": edit_code, "text": text}
    return json_loads(
        client.post(
            "https://rentry.co/api/edit/{}".format(url), payload, headers=_headers
        ).data
    )
