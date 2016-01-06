import getpass
import os
import errno

__author__ = 'aparnaelangovan'

class Utilities:


    @staticmethod
    def get_credentials( url):
        userid = input("Enter the login name for url {}\n".format(url))
        password = getpass.getpass();
        return (userid, password)


    @staticmethod
    def create_dir(dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
