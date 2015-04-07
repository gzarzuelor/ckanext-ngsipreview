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
# Ckanext-ngsipreview is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Orion Context Broker. If not, see http://www.gnu.org/licenses/.

import logging
import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.plugins import toolkit
from ckan.common import _, request

log = logging.getLogger(__name__)

try:
    import ckanext.resourceproxy.plugin as proxy
except ImportError:
    pass


class NGSIPreview(p.SingletonPlugin):
    # This extension previews NGSI10 and NGSI9 resources.

    p.implements(p.IRoutes, inherit=True)
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IResourcePreview, inherit=True)

    NGSI_FORMATS = ['ngsi9', 'ngsi10']
    proxy_is_enabled = False
    oauth2_is_enabled = False

    def before_map(self, m):
        m.connect('/dataset/{id}/resource/{resource_id}/ngsiproxy',
                  controller='ckanext.ngsipreview.controller:ProxyNGSIController', action='proxy_ngsi_resource')
        return m

    def get_proxified_ngsi_url(self, data_dict):
        url = h.url_for(action='proxy_ngsi_resource', controller='ckanext.ngsipreview.controller:ProxyNGSIController',
                        id=data_dict['package']['name'], resource_id=data_dict['resource']['id'])
        log.info('Proxified url is {0}'.format(url))
        return url

    def update_config(self, config):
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_resource('theme/public', 'ckanext-ngsipreview')

    def configure(self, config):
        self.proxy_is_enabled = config.get('ckan.resource_proxy_enabled')
        if config.get('ckan.plugins').find('oauth2') != -1:
            self.oauth2_is_enabled = True

    def check_query(self, resource):
        if (resource['url'].lower().find('/querycontext') != -1
                or resource['url'].lower().find('/contextentities/') != -1):
            return True
        else:
            return False

    def can_preview(self, data_dict):
        resource = data_dict['resource']
        if 'oauth_req' not in resource:
            oauth_req = 'false'
        else:
            oauth_req = resource['oauth_req']

        format_lower = resource['format'].lower()
        pattern = "/dataset/"+data_dict['package']['name']+"/resource/"
        if format_lower in self.NGSI_FORMATS:
            if resource['on_same_domain'] or self.proxy_is_enabled:
                if self.check_query(resource) and request.path.find(pattern) != -1 and oauth_req == 'true' and not toolkit.c.user:
                    details = "In order to see this resource properly, you need to be logged in"
                    h.flash_error(details, allow_html=False)
                    return {'can_preview': False, 'fixable': details, 'quality': 2}
                elif self.check_query(resource) and request.path.find(pattern) != -1 and oauth_req == 'true' and not self.oauth2_is_enabled:
                   details = "Enable oauth2 extension"
                   h.flash_error(details, allow_html=False)
                   return {'can_preview': False, 'fixable': details, 'quality': 2}
                elif (resource['url'].lower().find('/querycontext') != -1
                      and request.path.find(pattern) != -1 and 'payload' not in resource):
                    details = "Add a payload to complete the query"
                    h.flash_error(details, allow_html=False)
                    return {'can_preview': False, 'fixable': details, 'quality': 2}
                else:
                    return {'can_preview': True, 'quality': 2}
            else:
                return {'can_preview': False, 'fixable': 'Enable resource_proxy', 'quality': 2}
        else:
            return {'can_preview': False}

    def setup_template_variables(self, context, data_dict):
        if self.proxy_is_enabled and not data_dict['resource']['on_same_domain']:
            if self.check_query(data_dict['resource']):
                url = self.get_proxified_ngsi_url(data_dict)
                p.toolkit.c.resource['url'] = url
            else:
                url = proxy.get_proxified_resource_url(data_dict)
                p.toolkit.c.resource['url'] = url

    def preview_template(self, context, data_dict):
        return 'ngsi.html'
