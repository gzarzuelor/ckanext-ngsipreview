CKAN ckanext-ngsipreview
=====================

CKAN extension that will give you the ability to generate real-time resources provided by a Context broker. Some resources may need your IDM token, so you must be logged in to be able to see those resources properly.

Requirements
------------

* [OAuth2 CKAN Extension](https://github.com/conwetlab/ckanext-oauth2/). OAuth2 CKAN Extension. This extension might be needed since some the requests sent to the ContextBroker must include the OAuth2 credentials to identify the user that is creating the offering.

Installation
------------
Install this extension in your CKAN is instance is as easy as intall any other CKAN extension.

* Download the source from this GitHub repo.
* Activate your virtual environment (generally by running `. /usr/lib/ckan/default/bin/activate`)
* Install the extension by running `python setup.py develop`
* Modify your configuration file (generally in `/etc/ckan/default/production.ini`) and add `ngsipreview` in the `ckan.plugins` setting. 
* Restart your apache2 reserver (`sudo service apache2 restart`)

How it works?
------------
[How it works?](https://github.com/gzarrub/ckanext-ngsipreview/blob/master/ckanext/ngsipreview/instructions/how-it-works.md)
