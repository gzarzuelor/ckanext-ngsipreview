import urllib2
import urllib
from ckan.common import json

from logging import getLogger
import urlparse
import requests

import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins.toolkit as toolkit
import ckan.plugins as p

log = getLogger(__name__)

MAX_FILE_SIZE = 1024 * 1024  # 1MB
CHUNK_SIZE = 512

######################################
def GetAuthToken(user,password):
#This function is no need at ckan extension owing to X-Auth-Token is provided by another ex$
        data = {
                "auth": {
                        "passwordCredentials":{
                                "username":user,
                                "password":password,
                        }
                }
        }
        payload = json.dumps(data)
        request = urllib2.Request("http://cloud.lab.fi-ware.org:4730/v2.0/tokens",payload)
        request.add_header("Content-Type","application/json")
        response = urllib2.urlopen(request)
        assert response.code == 200
        jresponse = json.loads(response.read())
        return jresponse['access']['token']['id']

######################################


def proxy_ngsi_resource(context, data_dict):
    # Chunked proxy for ngsi resources.
    resource_id = data_dict['resource_id']
    log.info('Proxify resource {id}'.format(id=resource_id))
    resource = logic.get_action('resource_show')(context, {'id': resource_id})
    url = resource['url']
    #token = p.toolkit.c.usertoken['access_token']
    token = GetAuthToken("guillermo-zarzuelo-1","29Zarzu")
    parts = urlparse.urlsplit(url)
    if not parts.scheme or not parts.netloc:
        base.abort(409, detail='Invalid URL.')

    try:
        count = 0
        while True:
            headers = {'X-Auth-Token': token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
            if url.lower().find('/querycontext') != -1:
                payload = resource['payload']
                r = requests.post(url, headers=headers, data=payload, stream=True)
            else:
                r = requests.get(url, headers=headers, stream=True)
#            r.raise_for_status()
            base.response.content_type = r.headers['content-type']
            base.response.charset = r.encoding
            if r.status_code == 401:
                log.info('ERROR 401 token expired. Retrieving new token and retrying...')
#                p.toolkit.c.usertoken_refresh()
                if count == 2:
                    base.abort(409, detail='Cannot retrieve a new token.')
                    break
                count += 1
            else:
                break
        length = 0
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            base.response.body_file.write(chunk)
            length += len(chunk)
            if length >= MAX_FILE_SIZE:
                details = 'Content is too large to be proxied. Complete the Context Broker query \nwith pagination parameters to resolve this issue.'
                base.abort(409, headers={'content-encoding': ''}, detail=details)

    except:
        details = 'Could not proxy ngsi_resource.\nWe are working to resolve this issue as quickly as possible'
        base.abort(409, detail=details)


class ProxyNGSIController(base.BaseController):
    def proxy_ngsi_resource(self, resource_id):
        data_dict = {'resource_id': resource_id}
        context = {'model': base.model, 'session': base.model.Session, 'user': base.c.user or base.c.author}
        return proxy_ngsi_resource(context, data_dict)
