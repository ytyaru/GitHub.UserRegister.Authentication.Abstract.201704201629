#!python3
#encoding:utf-8
from abc import ABCMeta, abstractmethod

class ASubCommand(metaclass=ABCMeta):
    """
    GitHubUserRegister.pyのサブコマンド実行抽象メソッド。
    @param {argsparse.ArgumentParser().parse_args()} argsはCUI起動引数一式。
    """
    @abstractmethod
    def Run(self, args):
        pass
