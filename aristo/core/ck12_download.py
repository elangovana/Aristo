import logging
import os
import errno
import shutil
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from aristo.core.setup_logger import setup_log


class Ck12CorpusCreater:
    def __init__(self, out_dir, logger=None):
        self.logger =logger
        if logger is None:
            log_dir = os.path.join(os.path.dirname(__file__),"../../../outputdata/Ck12CorpusCreater_{}".format(time.strftime('%Y%m%d_%H%M%S')))
            self._ensure_dir(log_dir)
            self.logger = setup_log(log_dir, "Ck12CorpusCreater")

        self._ensure_dir(out_dir)

        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList',2) #custom location
        self.profile.set_preference('browser.download.dir',os.path.abspath( out_dir))
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference("pdfjs.disabled", True)
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk',"application/pdf")
        self.profile.set_preference('plugin.scan.plid.all',False)
        self.profile.set_preference("plugin.scan.Acrobat","99.0")
        self.driver = webdriver.Firefox(self.profile)

    def _download_lesson_pdf(self, lesson_url, out_dir):
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
        self._ensure_dir(out_dir)
        if r.status_code == 200:
            filename = os.path.join(out_dir, url.rsplit('/', 1)[-1])
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print("failed for " + url)
            self.logger.warn("failed for " + url)

    def download_book(self, base_url, out_dir):
        #base_url="https://www.ck12.org/book/CK-12-Life-Science-Concepts-For-Middle-School/section/1.3"
        self.logger.info("Downloading book {} to {}".format(base_url, out_dir))
        self.sign_in(base_url)
        self.driver.get(base_url)
        for chapter_url in [url for url in self.get_toc_urls()]:
            self.driver.get(chapter_url)
            for lesson_url in [url for url in self.get_toc_urls()]:

                self._download_lesson_pdf(lesson_url, out_dir)


    def get_toc_urls(self):
        WebDriverWait(self.driver, 10).until(lambda s: s.find_element(By.CLASS_NAME,
                                                                 "toc_list").is_displayed())  # EC.visibility_of_element_located ((By.CLASS_NAME, "toc_list")))
        toc_list_element = self.driver.find_element_by_class_name("toc_list")
        WebDriverWait(self.driver, 5).until(lambda s: toc_list_element.find_element(By.XPATH, "./li").is_displayed())
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
        login_name_element.send_keys("aparnaelangovan@yahoo.com")
        pwd_element = self.driver.find_element(By.NAME, "token")
        pwd_element.send_keys("Ck12123")
        sign_in_btn = self.driver.find_element_by_xpath("//input[@value='Sign In' and @type='button']")
        time.sleep(3)
        sign_in_btn.click()
        time.sleep(20)

    def _ensure_dir(self, dirname):
        """
        Ensure that a named directory exists; if it does not, attempt to create it.
        """
        try:
            os.makedirs(dirname)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


creater = Ck12CorpusCreater(os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/ck-12-downloads"))

creater.download_book("https://www.ck12.org/book/CK-12-Life-Science-Concepts-For-Middle-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Life-Science-Concepts-For-Middle-School"))

creater.download_book("https://www.ck12.org/book/CK-12-Earth-Science-Concepts-For-High-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Earth-Science-Concepts-For-High-School"))
creater.download_book("https://www.ck12.org/book/CK-12-Earth-Science-Concepts-For-Middle-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Earth-Science-Concepts-For-Middle-School"))
creater.download_book("https://www.ck12.org/book/CK-12-Physical-Science-Concepts-For-Middle-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Physical-Science-Concepts-For-Middle-School"))
creater.download_book("https://www.ck12.org/book/CK-12-Biology-Concepts/",
                                  os.path.join(os.path.dirname(__file__), "../../../corpus/CK-12-Biology-Concepts"))
creater.download_book("https://www.ck12.org/book/CK-12-Chemistry-Basic/",
                                  os.path.join(os.path.dirname(__file__), "../../../corpus/CK-12-Chemistry-Basic"))
creater.download_book("https://www.ck12.org/book/CK-12-Chemistry-Concepts-Intermediate/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Chemistry-Concepts-Intermediate"))
creater.download_book("https://www.ck12.org/book/CK-12-Physics-Concepts---Intermediate/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Physics-Concepts-Intermediate"))
creater.download_book(
    "https://www.ck12.org/book/CK-12-Modeling-and-Simulation-for-High-School-Teachers%253A-Principles-Problems-and-Lesson-Plans/",
    os.path.join(os.path.dirname(__file__),
                 "../../../corpus/CK-12-Modeling-and-Simulation-for-High-School-Teachers-Principles-Problems-and-Lesson-Plans/"))
