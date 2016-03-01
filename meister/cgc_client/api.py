#!/usr/bin/env python
# -* coding: utf-8 -*-

"""API client to talk to the CGC API."""

from __future__ import print_function, unicode_literals, absolute_import, \
                       division

import glob
import base64
import os
import os.path
import sys

# pylint: disable=import-error,no-name-in-module
if sys.version_info < (3,):
    from urlparse import urljoin
else:
    from urllib.parse import urljoin
# pylint: enable=import-error,no-name-in-module

import requests
from requests.auth import HTTPDigestAuth

import meister.cgc_client
from .errors import CGCAPIError

LOG = meister.cgc_client.LOG.getChild('api')


def from_env():
    """Create a CGC API Object from environment variables."""
    LOG.debug("Creating configuration from environment variables")
    url = os.environ.get('CGC_API_URL', 'localhost')
    user = os.environ.get('CGC_API_USER', 'shellphish')
    password = os.environ.get('CGC_API_PASS', 'shellphish')
    binaries_path = os.environ.get('CGC_CB_PATH', '/tmp/')

    return CGCAPI(url, user, password, binaries_path)


class CGCAPI(object):
    """Wrapper to talk to the CGC API."""

    def __init__(self, url, user, password, binaries_path):
        """Create the CGC API wrapper."""
        self.url = url
        self.user = user
        self.password = password
        self.binaries_path = binaries_path

    def _url(self, path):
        return urljoin(self.url, path)

    def _get(self, path):
        resp = requests.get(self._url(path),
                            auth=HTTPDigestAuth(self.user, self.password))
        if resp.status_code == 200:
            return resp.json()
        else:
            reason = "Error {} on GET {}".format(resp.status_code, path)
            raise CGCAPIError(reason)

    def status(self):
        """Retrieve the current status."""
        LOG.debug("Fetching current game status")
        return self._get('/status')

    def binaries(self, round_n):    # pylint: disable=unused-argument
        """Return all available binaries."""
        LOG.debug("Fetching binaries: %s", self.binaries_path)
        # NOTE: Why is this happening on disk instead of at the API?
        binaries_files = glob.glob(os.path.join(self.binaries_path,
                                                'qualifier_event/*/*'))
        binaries_names = (os.path.basename(b) for b in binaries_files)
        LOG.debug("Binaries available: %s", ", ".join(binaries_names))
        binaries = []
        for binary in binaries_files:
            with open(binary, 'rb') as bin_file:
                binaries.append({'cbid': os.path.basename(binary),
                                 'data': base64.b64encode(bin_file.read())})
        return {'binaries': binaries}