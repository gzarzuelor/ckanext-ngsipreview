import urllib2
import urllib
import logging
import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.plugins import toolkit
from ckan.common import json
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
        format_lower = resource['format'].lower()
        pattern = "/dataset/"+data_dict['package']['name']+"/resource/"
        if format_lower in self.NGSI_FORMATS:
            if self.check_query(resource) and 'payload' in resource:
                resource['payload'] = resource['payload'].replace("'", '"')
                resource['payload'] = resource['payload'].replace(" ", "")

            if resource['on_same_domain'] or self.proxy_is_enabled:
                if self.check_query(resource) and request.path.find(pattern) != -1 and not toolkit.c.user:
                    details = "In order to see this resource properly, you need to be logged in"
                    h.flash_error(details, allow_html=False)
                    return {'can_preview': False, 'fixable': details, 'quality': 2}
#                elif self.check_query(resource) and request.path.find(pattern) != -1 and not self.oauth2_is_enabled:
#                    details = "Enable oauth2 extension"
#                    h.flash_error(details, allow_html=False)
#                    return {'can_preview': False, 'fixable': details, 'quality': 2}
                elif (resource['url'].lower().find('/querycontext') != -1
                      and request.path.find(pattern) != -1 and 'payload' not in resource):
                    details = "Add a payload to complete the query"
                    h.flash_error(details, allow_html=False)
                    return {'can_preview': False, 'fixable': details, 'quality': 2}
                else:
                    return {'can_preview': True, 'quality': 2}
            else:
                return {'can_preview': False, 'fixable': 'Enable resource_proxy', 'quality': 2}
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
