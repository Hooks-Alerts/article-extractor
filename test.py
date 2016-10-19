
from urllib.parse import urlparse

import time
import cgi
import re



url_original = "http://meneame.net"

url_devuelta = "//blandiblue/amp"


print 

orig_scheme = (urlparse(url_original).scheme)

if url_devuelta.startswith('//'):
    print (orig_scheme+":"+url_devuelta)