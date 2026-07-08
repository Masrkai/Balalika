import useragentgen


def make_headers() -> dict[str, str]:
    return {
        "Host": "www.linkedin.com",
        "User-Agent": useragentgen.generate(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
    }
