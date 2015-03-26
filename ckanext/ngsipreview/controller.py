#!/usr/bin/env python
# Copyright 2015 Telefonica Investigacion y Desarrollo, S.A.U
#
# This file is part of ckanext-ngsipreview.
#
# Ckanext-ngsipreview is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# FlaskContextProvider is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion Context Broker. If not, see http://www.gnu.org/licenses/.

from logging import getLogger
import urlparse
import requests
import json
import ckan.logic as logic
import ckan.lib.base as base
import ckan.plugins as p

log = getLogger(__name__)

MAX_FILE_SIZE = 1024 * 1024  # 1MB
CHUNK_SIZE = 512


def proxy_ngsi_resource(context, data_dict):
    # Chunked proxy for ngsi resources.
    resource_id = data_dict['resource_id']
    log.info('Proxify resource {id}'.format(id=resource_id))
    resource = logic.get_action('resource_show')(context, {'id': resource_id})

    if 'oauth_req' in resource and resource['oauth_req'] == 'true':
        token = p.toolkit.c.usertoken['access_token']
        headers = {'X-Auth-Token': token, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    else:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    if 'tenant' in resource:
        headers['Fiware-Service'] = resource['tenant']
    if 'service_path' in resource:
        headers['Fiware-ServicePath'] = resource['service_path']

    url = resource['url']
    parts = urlparse.urlsplit(url)

    if not parts.scheme or not parts.netloc:
        base.abort(409, detail='Invalid URL.')

    try:
        for i in range(2):
            if url.lower().find('/querycontext') != -1:
                resource['payload'] = resource['payload'].replace("'", '"')
                resource['payload'] = resource['payload'].replace(" ", "")

                payload = json.dumps(json.loads(resource['payload']))

                r = requests.post(url, headers=headers, data=payload, stream=True)
            else:
                r = requests.get(url, headers=headers, stream=True)

            if r.status_code == 401 and 'oauth_req' in resource and resource['oauth_req'] == 'true':
                details = 'ERROR 401 token expired. Retrieving new token and retrying...'
                log.info(details)
                p.toolkit.c.usertoken_refresh()
            else:
                break

        if r.status_code == 401:
            if 'oauth_req' not in resource or resource['oauth_req'] == 'false':
                details = 'This query may need Oauth-token, please check if the token field on resource_edit is correct.'
                log.info(details)
                base.abort(409, detail=details)
            else:
                base.abort(409, detail='Cannot retrieve a new token.')

        else:
            r.raise_for_status()
            base.response.content_type = r.headers['content-type']
            base.response.charset = r.encoding


        length = 0
        for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
            base.response.body_file.write(chunk)
            length += len(chunk)
            if length >= MAX_FILE_SIZE:
                details = 'Content is too large to be proxied. Complete the Context Broker query with pagination parameters to resolve this issue.'
                base.abort(409, headers={'content-encoding': ''}, detail=details)

    except ValueError:
        details = 'There is a problem with the payload, please check if the query is properly parsed.'
        base.abort(409, detail=details)
    except requests.HTTPError:
        details = 'Could not proxy ngsi_resource. We are working to resolve this issue as quickly as possible'
        base.abort(409, detail=details)
    except requests.ConnectionError:
        details = 'Could not proxy ngsi_resource because a connection error occurred.'
        base.abort(502, detail=details)
    except requests.Timeout:
        details = 'Could not proxy ngsi_resource because the connection timed out.'
        base.abort(504, detail=details)


class ProxyNGSIController(base.BaseController):
    def proxy_ngsi_resource(self, resource_id):
        data_dict = {'resource_id': resource_id}
        context = {'model': base.model, 'session': base.model.Session, 'user': base.c.user or base.c.author}
        return proxy_ngsi_resource(context, data_dict)
