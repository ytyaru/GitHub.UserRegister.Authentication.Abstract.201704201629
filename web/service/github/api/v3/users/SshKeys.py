#!python3
#encoding:utf-8
import requests
import datetime
import time
import json
import web.service.github.api.v3.Response
class SshKeys(object):
    def __init__(self, reqp, response):
        self.__reqp = reqp
        self.__response = response

    """
    SSH鍵の生成。
    @params {string} public_keyはSSH公開鍵。
    @params {string} titleはSSH公開鍵。
    """
    def Create(self, public_key, title=None):
        method = 'POST'
        endpoint = 'users/:username/keys'
        params = self.__reqp.Get(method, endpoint)
        params['data'] = json.dumps({'title': title, 'key': public_key})
        url = 'https://api.github.com/user/keys'
        print(url)
        print(data)
        r = requests.post(url, **params)
        return self.__response.Get(r)
        
    def Gets(self, username):
        method = 'GET'
        endpoint = 'users/:username/keys'
        params = self.__reqp.Get(method, endpoint)
        keys = []
        url = 'https://api.github.com/users/{username}/keys'.format(username=username)
        while None is not url:
            print(url)
            r = requests.get(url, **params)
            keys += self.__response.Get(r)
            url = self.__response.Headers.Link.Next(r)
            params = self.__reqp.Get(method, endpoint)
        return keys
        
    def Get(self, key_id):
        method = 'GET'
        endpoint = 'user/keys/:id'
        params = self.__reqp.Get(method, endpoint)
        url = 'https://api.github.com/user/keys/{key_id}'.format(key_id=key_id)
        print(url)
        r = requests.get(url, **params)
        return self.__response.Get(r)
        
    """
    GitHubに設定したSSH公開鍵を削除する。
    BASIC認証でしか使えない。
    """
    def Delete(self, key_id):
        method = 'DELETE'
        endpoint = 'user/keys/:id'
        params = self.__reqp.Get(method, endpoint)
        url = 'https://api.github.com/user/keys/{key_id}'.format(key_id=key_id)
        print(url)
        r = requests.delete(url, **params)
        return self.__response.Get(r)

