import getpass
import logging
import os
import errno
import shutil
import time
from urllib.parse import urlparse
from contextlib import ContextDecorator

import requests
from selenium import webdriver
import selenium

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from aristo.core.setup_logger import setup_log


class Ck12CorpusCreater(ContextDecorator):
    def __init__(self,userid, password, out_dir, logger=None):
        self.userid=userid
        self.password = password
        self.logger =logger
        if logger is None:
            log_dir = os.path.join(os.path.dirname(__file__),"../../../outputdata/Ck12CorpusCreater_{}".format(time.strftime('%Y%m%d_%H%M%S')))
            self.ensure_dir(log_dir)
            self.logger = setup_log(log_dir, "Ck12CorpusCreater")

        self.ensure_dir(out_dir)

        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList',2) #custom location
        self.profile.set_preference('browser.download.dir',os.path.abspath( out_dir))
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference("pdfjs.disabled", True)
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk',"application/pdf")
        self.profile.set_preference('plugin.scan.plid.all',False)
        self.profile.set_preference("plugin.scan.Acrobat","99.0")
        self.driver = webdriver.Firefox(self.profile)

    def _download_lesson_pdf(self, lesson_url):
        self.driver.get(lesson_url)
        WebDriverWait(self.driver, 20).until(lambda s: s.find_element(By.ID, "pdfonecolumndownload").is_enabled())
        pdf_element = self.driver.find_element_by_id(
            "pdfonecolumndownload")  # EC.visibility_of_element_located ((By.CLASS_NAME, "toc_list")))
        href = pdf_element.get_attribute('href')
        self.logger.info("Downloading lesson: {}, pdf href {}".format(lesson_url, href))
        self.logger.info(href)
        pdf_element = self.driver.find_element_by_id("pdfonecolumndownload")
        pdf_element.send_keys(Keys.ENTER)
        time.sleep(5)
        pass
        # if href.endswith("#"):
        #
        #     pass
        # else :
        #     self._download_url(href, out_dir)

    def _download_url(self, url, out_dir):
        r = requests.get(url, stream=True)
        self.ensure_dir(out_dir)
        if r.status_code == 200:
            filename = os.path.join(out_dir, url.rsplit('/', 1)[-1])
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print("failed for " + url)
            self.logger.warn("failed for " + url)

    def download_book(self, base_url):
        #base_url="https://www.ck12.org/book/CK-12-Life-Science-Concepts-For-Middle-School/section/1.3"
        self.logger.info("Downloading book {} ".format(base_url))
        self.sign_in(base_url)
        self.driver.get(base_url)
        for chapter_url in [url for url in self.get_toc_urls()]:
            self.logger.info("Get chapter: {}".format(chapter_url))
            self.driver.get(chapter_url)
            lesson_urls = [url for url in self.get_toc_urls()]
            for lesson_url in lesson_urls:
                self.logger.info("Get lesson: {}".format(lesson_url))
                self._download_lesson_pdf(lesson_url)
            if len(lesson_urls) == 0:
                self._download_lesson_pdf(chapter_url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()

    def get_toc_urls(self):
        WebDriverWait(self.driver, 10).until(lambda s: s.find_element(By.CLASS_NAME,
                                                                 "toc_list").is_displayed())  # EC.visibility_of_element_located ((By.CLASS_NAME, "toc_list")))
        toc_list_element = self.driver.find_element_by_class_name("toc_list")
        try:
            WebDriverWait(self.driver, 5).until(lambda s: toc_list_element.find_element(By.XPATH, "./li").is_displayed())
        except selenium.common.exceptions.TimeoutException as ex:
            self.logger.warn("Timeout exception {}, assumming no toc for url {}..".format(ex, self.driver.current_url))

            return []
        toc_elements = toc_list_element.find_elements(By.XPATH, "./li")
        for toc_element in toc_elements:
            url = toc_element.find_element(By.XPATH, "./a").get_attribute('href')
            yield url

    def sign_in(self, url):
        self.driver.get(url)
        if len(self.driver.find_elements_by_id("top_nav_signin")) == 0 :
            self.logger.debug("Already signed in")
            return
        sign_in = self.driver.find_element_by_id("top_nav_signin")
        sign_in.click()
        WebDriverWait(self.driver, 5).until(lambda s: self.driver.find_element(By.NAME, "login").is_enabled())
        login_name_element = self.driver.find_element(By.NAME, "login")
        login_name_element.send_keys(self.userid)
        pwd_element = self.driver.find_element(By.NAME, "token")
        pwd_element.send_keys(self.password)
        sign_in_btn = self.driver.find_element_by_xpath("//input[@value='Sign In' and @type='button']")
        time.sleep(3)
        sign_in_btn.click()
        time.sleep(20)

    @staticmethod
    def ensure_dir(dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


def download(url, credentials, logger ):
    (userid, password) = credentials
    folder_name =  urlparse(url).path.replace("/","").replace("%","")
    with Ck12CorpusCreater(userid, password, os.path.join(os.path.dirname(__file__), "../../../corpus/{}".format(folder_name)),
                           logger=logger)   as  ck12CorpusCreater :
        ck12CorpusCreater.download_book(url)


def GetCredentialsForCorpus():
    userid = input("Enter the login name for ck12\n")
    password = getpass.getpass();
    return (userid, password)


log_dir = os.path.join(os.path.dirname(__file__),"../../../outputdata/Ck12CorpusCreater_{}".format(time.strftime('%Y%m%d_%H%M%S')))
Ck12CorpusCreater.ensure_dir(log_dir)
log = setup_log(log_dir, "Ck12CorpusCreater")


credentialsCk12 = GetCredentialsForCorpus()


download("https://www.ck12.org/book/CK-12-Life-Science-Concepts-For-Middle-School",credentialsCk12, log)
download("https://www.ck12.org/book/CK-12-Earth-Science-Concepts-For-High-School", credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Earth-Science-Concepts-For-Middle-School", credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Physical-Science-Concepts-For-Middle-School",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Biology-Concepts",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Chemistry-Basic",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Chemistry-Concepts-Intermediate",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Physics-Concepts---Intermediate",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Understanding-Biodiversity",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-Biology-Advanced-Concepts/",credentialsCk12,log)
download("https://www.ck12.org/book/CK-12-21st-Century-Physics-A-Compilation-of-Contemporary-and-Emerging-Technologies/",credentialsCk12,log)
download("https://www.ck12.org/book/Peoples-Physics-Book-Basic/",credentialsCk12,log)
download("https://www.ck12.org/book/Peoples-Physics-Concepts/",credentialsCk12,log)
download("https://www.ck12.org/book/Physics-From-Stargazers-to-Starships/",credentialsCk12,log)
download("https://www.ck12.org/book/From-Vitamins-to-Baked-Goods%253A-Real-Applications-of-Organic-Chemistry/",credentialsCk12,log)