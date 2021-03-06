#!/usr/bin/python3

import base64
import hashlib
import hmac
import json
import requests
import time

from .endpoints import EndpointsMixin
from .defaults import DEFAULTS
from .fields import FIELDS

class Pyscape(EndpointsMixin):
    "Facilitate grabbing data from Moz API."

    def __init__(self, access_id, secret_key):
        "generates basic auth credentials"
        self.api_url = 'http://lsapi.seomoz.com/linkscape/'         
        self.access_id = access_id
        self.secret_key = secret_key
        
    def __repr__(self):
        return '<Pyscape: %s>' % (self.access_id)

    def _add_signature(self, params = {}):
        """Adds key value pairs necessary to authenticate a Moz API request.
        
        See documentation:
        http://moz.com/help/guides/moz-api/mozscape/getting-started-with-mozscape/signed-authentication
        """

        expires = int(time.time() + 300)
        toSign  = '%s\n%i' % (self.access_id, expires)

        params['AccessID'] = self.access_id
        params['Expires'] = expires
        params['Signature'] = base64.b64encode(hmac.new(self.secret_key.encode('ascii'), toSign.encode('ascii'), hashlib.sha1).digest())

        return params
    
    def get(self, endpoint, url = '', params = {}):
        params = self._add_signature(params)
        # Filters are passed as a list, but need to be separated
        # with '+' when put in URL.
        if 'Filters' in params:
            params['Filters'] = '+'.join(params['Filters'])
        call = ''.join([self.api_url, endpoint, '/', url])
        
        return requests.get(call, params = params)
    
    def post(self, endpoint, urls = [], params = {}):
        params = self._add_signature(params)
        call = ''.join([self.api_url, endpoint, '/'])
        
        return requests.post(call, params = params, data=json.dumps(urls))
        
    def _get_bitflag(self, field):
        return FIELDS[field]['flag']
        
    def _add_smart_fields(self, endpoint, params = {}):
        """If no fields are requested, adds default fields to supply
        a meaningful response."""
        # Want to avoid adding 'Scope' as a parameter if it doesn't
        # exist, but need to use it as key for looking up defaults
        # regardless.
        if 'Scope' in params:
            scope = params['Scope']
        else:
            scope = None

        if all(k not in params for k in ['Cols','SourceCols','TargetCols','LinkCols']):

            # Shortcut for readability
            field_groups = DEFAULTS[endpoint][scope]['Fields']
            for group in field_groups:
                bit_field = 0
                for field in field_groups[group]:
                    bit_field = bit_field | self._get_bitflag(field)
                params[group] = bit_field
        
        if 'Sort' in DEFAULTS[endpoint][scope] and 'Sort' not in params:
            params['Sort'] = DEFAULTS[endpoint][scope]['Sort']

        return params