#!/usr/bin/env python
#
# Copyright Daniel Liljeberg 2018

import os
import sys
import logging
import requests
import json

from base64 import b64encode

# Enable verified HTTPS requests on older Pythons
# http://urllib3.readthedocs.org/en/latest/security.html
if sys.version_info[0] == 2:
    try:
        requests.packages.urllib3.contrib.pyopenssl.inject_into_urllib3()
    except AttributeError:
        # see https://github.com/certbot/certbot/issues/1883
        import urllib3.contrib.pyopenssl
        urllib3.contrib.pyopenssl.inject_into_urllib3()

# Setup logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

# Setup log level
if os.environ.get('DEBUG'):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

# Setup headers for our requests
try:
    authstr = 'Basic ' + b64encode(b':'.join((os.environ['ONAPP_EMAIL'], os.environ['ONAPP_KEY']))).strip()
    ONAPP_HEADERS = {
        'Authorization': authstr,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    ONAPP_URL = "https://{0}/".format(os.environ['ONAPP_URL'])
except KeyError:
    logger.error(" + Unable to locate OnApp credentials in environment!")
    sys.exit(1)

# Method for deploying cert
def deploy_cert(args):
    domain, privkey_pem, cert_pem, fullchain_pem, chain_pem, timestamp = args
    logger.debug(' + ssl_certificate: {0}'.format(fullchain_pem))
    logger.debug(' + ssl_certificate_key: {0}'.format(privkey_pem))

    # Get the ID for the custom cert
    cdn_id = get_cdn_ssl_id(domain)
    if(cdn_id == None):
        return

    logger.debug(' + cdn_ssl_certificate_id: {0}'.format(cdn_id))
    
    # Update cert on onapp
    url = '{0}cdn_ssl_certificates/{1}.json'.format(ONAPP_URL, cdn_id)
    cert = open(fullchain_pem, 'r')
    key = open(privkey_pem, 'r')
    payload = {
        'cdn_ssl_certificate': {
            'name': domain,
            'cert': cert.read().replace('\n', '\r\n').strip(),
            'key': key.read().replace('\n', '\r\n').strip()
        }
    }
    cert.close()
    key.close()

    # Perform request to update cert
    r = requests.put(url, data=json.dumps(payload), headers=ONAPP_HEADERS)
    r.raise_for_status()
    logger.info(' + custom_ssl_update: {0}'.format(r.ok))
    return

# Gets the SSL cert id
def get_cdn_ssl_id(domain):
    url = "{0}cdn_ssl_certificates.json".format(ONAPP_URL)
    r = requests.get(url, headers=ONAPP_HEADERS)
    r.raise_for_status()
    json = r.json()
    for index, item in enumerate(json):
        if item['cdn_ssl_certificate']['name'] == domain:
            return item['cdn_ssl_certificate']['id']
    
    return None

# Main function to redirect to proper method
def main(argv):
    ops = {
        'deploy_cert'     : deploy_cert,
    }
    if argv[0] in ops:
        logger.info(" + OnApp hook executing: {0}".format(argv[0]))
        ops[argv[0]](argv[1:])

if __name__ == '__main__':
    main(sys.argv[1:])