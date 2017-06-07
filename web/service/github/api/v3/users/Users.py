#!python3
#encoding:utf-8
import requests
import datetime
import time
import json
import web.service.github.api.v3.Response
class Users:
    def __init__(self, reqp, response):
        self.__reqp = reqp
        self.__response = response
        
    def Get(self):
        method = 'GET'
        endpoint = 'users/:username'
        params = self.__reqp.Get(method, endpoint)
        url = 'https://api.github.com/users/{username}'.format(username=username)
        print(url)
        r = requests.get(url, **params)
        return self.__response.Get(r)

