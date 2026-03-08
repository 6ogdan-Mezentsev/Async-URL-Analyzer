from urllib.parse import urlparse, urlunparse
import ipaddress

def normalize_and_validate_url(raw_url: str) -> str:
    """
    Нормализует и валидирует URL.
    Удаляет лишние пробелы, проверяет схему, хост и порт.
    """
    url = raw_url.strip()
    if not url:
        raise ValueError("empty url")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("invalid scheme")

    if not parsed.hostname:
        raise ValueError("missing host")

    host = parsed.hostname.lower()

    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            raise ValueError("private or local address is not allowed")
    except ValueError:
        if host in ("localhost",):
            raise ValueError("localhost is not allowed")

    normalized = urlunparse((
        parsed.scheme,
        host if parsed.port is None else f"{host}:{parsed.port}",
        parsed.path or "/",
        parsed.params,
        parsed.query,
        "",
    ))
    return normalized
