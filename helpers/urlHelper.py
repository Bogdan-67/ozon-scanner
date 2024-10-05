from urllib.parse import urlencode, urlparse, urlunparse, parse_qs


def add_params_url(url: str, params: dict):
    parsed_url = urlparse(url)
    new_query = urlencode(params, encoding='utf-8')

    url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query,
        parsed_url.fragment
    ))

    return url
