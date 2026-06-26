import ssl
import socket

def get_cert_san_names(host: str, sni_host: str = None, timeout: int = 5):
    """
    Retrieve TLS certificate SAN names.

    Returns:
    {
        "ok": True/False,
        "san": [],
        "subject": [],
        "issuer": [],
        "error": ""
    }
    """

    if not sni_host:
        sni_host = host

    context = ssl.create_default_context()

    result = {
        "ok": False,
        "san": [],
        "subject": [],
        "issuer": [],
    }

    try:
        with socket.create_connection((host, 443), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=sni_host) as ssock:
                cert = ssock.getpeercert()

        san = []
        if "subjectAltName" in cert:
            for entry in cert["subjectAltName"]:
                if entry[0] == "DNS":
                    san.append(entry[1])

        subject = []
        for item in cert.get("subject", []):
            for k, v in item:
                subject.append(f"{k}={v}")

        issuer = []
        for item in cert.get("issuer", []):
            for k, v in item:
                issuer.append(f"{k}={v}")

        result["ok"] = True
        result["san"] = san
        result["subject"] = subject
        result["issuer"] = issuer

        return result

    except Exception as e:
        result["error"] = str(e)
        return result