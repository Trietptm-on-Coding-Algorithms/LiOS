"""
__author__ = 'LuoCheng'
This file contain the class and method of ipa file operation
"""

import zipfile

class IPAFile():
    """
    IPA file operation
    """
    def __init__(self, fname):
        self.file_name = fname
        self.zip_file = zipfile.ZipFile(self.file_name)
        if self.zip_file.testzip() != None:
            print "IPA file (%s) damaged!" %self.file_name
        self.app_name = self._get_app_name()
        if self.app_name == None:
            print "Get app_name in archive error!"
        self.app_path = self._get_app_path()
        if self.app_path == None:
            print "Get app_path error!"

    def _get_app_name(self):
        namelist = self.zip_file.namelist()
        if len(namelist) < 2:
            return None
        else:
            path = self.zip_file.namelist()[1]
            appfold = path.split(r'/')[1]
            return appfold.split(r'.')[0]

    def _get_app_path(self):
        namelist = self.zip_file.namelist()
        if len(namelist) < 2:
            return None
        else:
            path = self.zip_file.namelist()[1]
            return path + self._get_app_name()

    def _extract_app(self):
        app_info = self.zip_file.getinfo(self.app_path)
        #this step last longer than extracting file, considering not using file header
        file_header = self.zip_file.read(app_info)[:4]
        if file_header == '\xce\xfa\xed\xfe' or file_header == '\xca\xfe\xba\xbe':
            self.zip_file.extract(app_info)
        else:
            print "extract app error"

    def ExtractApp(self):
        self._extract_app()
        self.zip_file.close()

def test():
    import os
    os.chdir(r'D:\Soft\iPhone\IPA')
    for fname in os.listdir('.'):
        if fname.endswith('.ipa'):
            ipa = IPAFile(fname)
            ipa.ExtractApp()

if __name__ == "__main__":
    test()
