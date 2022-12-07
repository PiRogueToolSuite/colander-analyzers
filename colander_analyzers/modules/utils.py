import ipaddress
import re, os
from tempfile import NamedTemporaryFile

from IPy import IP
from urllib.parse import urlparse
from datetime import date, datetime

from minio import Minio


def unbracket(domain):
    """Remove protective bracket from a domain"""
    return domain.replace("[.]", ".")


def bracket(domain):
    """Add protective bracket to a domain"""
    last_dot = domain.rfind(".")
    return domain[:last_dot] + "[.]" + domain[last_dot+1:]


def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def same_url(url1, url2):
    """
    Check for minor differences between url1 and url2, return True if they are the same
    Currently only consider extra www. in domain, https/http and extra fragment
    """
    if url1 == url2:
        return True
    # Dirty hacks
    if not url1.startswith('http'):
        url1 = 'http://' + url1
    if not url2.startswith('http'):
        url2 = 'http://' + url2
    if not url1.endswith('/'):
        url1 += '/'
    if not url2.endswith('/'):
        url2 += '/'
    purl2 = urlparse(url2)
    purl1 = urlparse(url1)

    if purl1.path == purl2.path and purl1.params == purl2.params and \
            purl1.query == purl2.query:
        if purl1.netloc == purl2.netloc:
            return True
        else:
            if ("www." + purl1.netloc) == purl2.netloc:
                return True
            if ("www." + purl2.netloc) == purl1.netloc:
                return True
    return False


def typeguess(indicator):
    """
    Guess the type of the indicator
    returns string in "IPv4", "IPv6", "md5", "sha1", "sha256", "domain"
    """
    if re.match(r"^\w{32}$", indicator):
        return "md5"
    elif re.match(r"^\w{40}$", indicator):
        return "sha1"
    elif re.match(r"^\w{64}$", indicator):
        return "sha256"
    else:
        try:
            i = IP(indicator)
            if i.version() == 4:
                return "IPv4"
            else:
                return "IPv6"
        except ValueError:
            return "domain"


def is_ip(target):
    """
    Test if a string is an IP address
    """
    if isinstance(target, str):
        try:
            IP(target)
            return True
        except ValueError:
            return False
    else:
        return False


def is_ipv4(target):
    if is_ip(target):
        return IP(target).version() == 4


def is_ipv6(target):
    if is_ip(target):
        return IP(target).version() == 6


def is_ip_routable(ip):
    try:
        return ipaddress.ip_address(ip).is_global
    except:
        return False


def ts_to_str(ts):
    return datetime.fromtimestamp(ts).isoformat()


def is_sha256(string):
    return re.match(r"^\w{64}$", string) is not None


class LocalFile:
    def __init__(self, config):
        self.config = config
        self.local_file = NamedTemporaryFile(delete=False)

    def __enter__(self):
        if self.config.get('engine') == 's3':
            if 'host' not in self.config or 'access_key' not in self.config or 'secret_key' not in self.config:
                raise Exception('The provided S3 configuration is invalid')
            if 'bucket' not in self.config or 'object' not in self.config:
                raise Exception('The provided S3 bucket configuration is invalid')
            client = Minio(self.config.get('host'),
                           secure=False,
                           access_key=self.config.get('access_key'),
                           secret_key=self.config.get('secret_key'))
            client.fget_object(self.config.get('bucket'), self.config.get('object'), self.local_file.name)
            return self.local_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.local_file.close()
        os.unlink(self.local_file.name)
