#!/usr/bin/python
#
# Copyright (C) 2010 Google Inc.

""" Fusion Tables Client.

Issue requests to Fusion Tables.
"""

__author__ = 'kbrisbin@google.com (Kathryn Brisbin)'

import urllib2, urllib
try:
  import oauth2
  import authorization.oauth
except: pass

import httplib2
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from urllib import urlencode

class FTClient():
  def _get(self, query): pass
  def _post(self, query): pass

  def query(self, query, request_type=None):
    """ Issue a query to the Fusion Tables API and return the result. """

    #encode to UTF-8
    try: query = query.encode("utf-8")
    except: query = query.decode('raw_unicode_escape').encode("utf-8")

    lowercase_query = query.lower()
    if lowercase_query.startswith("select") or \
       lowercase_query.startswith("describe") or \
       lowercase_query.startswith("show") or \
       request_type=="GET":

      return self._get(urllib.urlencode({'sql': query}))

    else:
      return self._post(urllib.urlencode({'sql': query}))


class ClientLoginFTClient(FTClient):

  def __init__(self, token):
    self.auth_token = token
    self.request_url = "https://www.google.com/fusiontables/api/query"

  def _get(self, query):
    headers = {
      'Authorization': 'GoogleLogin auth=' + self.auth_token,
    }
    serv_req = urllib2.Request(url="%s?%s" % (self.request_url, query),
                               headers=headers)
    serv_resp = urllib2.urlopen(serv_req)
    return serv_resp.read()

  def _post(self, query):
    headers = {
      'Authorization': 'GoogleLogin auth=' + self.auth_token,
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    serv_req = urllib2.Request(url=self.request_url, data=query, headers=headers)
    serv_resp = urllib2.urlopen(serv_req)
    return serv_resp.read()


class OAuthFTClient(FTClient):

  def __init__(self, consumer_key, consumer_secret):
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.scope = "https://www.google.com/fusiontables/api/query"
    self._set_flow()

  def _set_flow(self):
    self.FLOW = OAuth2WebServerFlow(
      client_id=self.consumer_key,
      client_secret=self.consumer_secret,
      scope=self.scope,
      user_agent="fusion-tables-client-python/1.0")
    
  def _authorize(self):
     storage = Storage("fusion_tables.dat")
     credentials = storage.get()
     if credentials is None or credentials.invalid:
       self._set_flow()
       credentials = run(self.FLOW, storage)
     http = httplib2.Http()
     http = credentials.authorize(http)
     return http

  def _get(self, query):    
    url = "%s?%s" % (self.scope, query)    
    resp, content = self._authorize().request(url, method="GET")                                              
    return content

  def _post(self, query):
    url = self.scope
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    resp, content = self._authorize().request(
      url, method="POST", body=query, headers=headers)
    return content
