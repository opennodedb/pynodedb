from flask import request
from urllib.parse import urlparse, urljoin
from flask import current_app as app


# Quick log function
def log(var):
    app.logger.info(var)


# Check that URL redirects back to the same host
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc
