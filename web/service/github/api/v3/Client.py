#!python3
#encoding:utf-8
import web.http.Response
import web.service.github.api.v3.Response
import web.service.github.api.v3.RequestParameter
from web.service.github.api.v3.miscellaneous.Licenses import Licenses
from web.service.github.api.v3.repositories.Repositories import Repositories
from web.service.github.api.v3.authorizations.Authorizations import Authorizations
from web.service.github.api.v3.users.Users import Users
from web.service.github.api.v3.users.SshKeys import SshKeys
from web.service.github.api.v3.users.Emails import Emails
class Client(object):
    def __init__(self, db, authentications, authData=None, repo=None):
        self.__db = db
        self.__repo = repo
        self.__authData = authData
        self.__reqp = web.service.github.api.v3.RequestParameter.RequestParameter(self.__db, authentications)
        self.__response = web.service.github.api.v3.Response.Response()

        self.__license = Licenses(self.__reqp, self.__response)
        self.__repo = Repositories(self.__reqp, self.__response, self.__authData, self.__repo)
        self.__authorization = Authorizations(self.__reqp, self.__response)
        self.__user = Users(self.__reqp, self.__response)
        self.__sshkey = SshKeys(self.__reqp, self.__response)
        self.__email = Emails(self.__reqp, self.__response)

    @property
    def Repositories(self):
        return self.__repo
    @property
    def Licenses(self):
        return self.__license
    @property
    def Authorizations(self):
        return self.__authorization
    @property
    def Users(self):
        return self.__user
    @property
    def SshKeys(self):
        return self.__sshkey
    @property
    def Emails(self):
        return self.__email
