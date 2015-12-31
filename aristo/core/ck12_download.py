import os
import errno
import shutil
import time

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class Ck12CorpusCreater:
    def _download_lesson_pdf(self, driver, lesson_url):
        driver.get(lesson_url)
        WebDriverWait(driver, 20).until(lambda s: s.find_element(By.ID, "pdfonecolumndownload").is_enabled())
        pdf_element = driver.find_element_by_id(
            "pdfonecolumndownload")  # EC.visibility_of_element_located ((By.CLASS_NAME, "toc_list")))
        href = pdf_element.get_attribute('href')
        print(href)
        if href.endswith("#"):
            print("obtaining element pdfonecolumndownload")
            driver.find_element_by_id("pdfonecolumndownload")
            pdf_element.click()
            pdf_element.click()
        else :
            self._download_url(href)

    def _download_url(self, url):

        r = requests.get(url, stream=True)
        self._ensure_dir(self.out_dir)
        if r.status_code == 200:
            filename = os.path.join(self.out_dir, url.rsplit('/', 1)[-1])
            with open(filename, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print("failed for " + url)
            Warning("failed for " + url)

    def download_book(self, base_url, out_dir):
        #base_url="https://www.ck12.org/book/CK-12-Life-Science-Concepts-For-Middle-School/section/1.3"
        self.out_dir = out_dir
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList',2) #custom location
        profile.set_preference('browser.download.dir', out_dir)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk',"application/vnd.fd")
        driver = webdriver.Firefox(profile)
        driver.get(base_url)
        self.sign_in(driver)
        driver.get(base_url)
        for chapter_url in [url for url in self.get_toc_urls(driver)]:
            driver.get(chapter_url)
            for lesson_url in [url for url in self.get_toc_urls(driver)]:
                print(lesson_url)
                self._download_lesson_pdf(driver, lesson_url)
        driver.quit()

    def get_toc_urls(self, driver):
        WebDriverWait(driver, 10).until(lambda s: s.find_element(By.CLASS_NAME,
                                                                 "toc_list").is_displayed())  # EC.visibility_of_element_located ((By.CLASS_NAME, "toc_list")))
        toc_list_element = driver.find_element_by_class_name("toc_list")
        WebDriverWait(driver, 5).until(lambda s: toc_list_element.find_element(By.XPATH, "./li").is_displayed())
        toc_elements = toc_list_element.find_elements(By.XPATH, "./li")
        for toc_element in toc_elements:
            url = toc_element.find_element(By.XPATH, "./a").get_attribute('href')
            yield url

    def sign_in(self, driver):
        sign_in = driver.find_element_by_id("top_nav_signin")
        sign_in.click()
        WebDriverWait(driver, 5).until(lambda s: driver.find_element(By.NAME, "login").is_enabled())
        login_name_element = driver.find_element(By.NAME, "login")
        login_name_element.send_keys("aparnaelangovan@yahoo.com")
        pwd_element = driver.find_element(By.NAME, "token")
        pwd_element.send_keys("Ck12123")
        sign_in_btn = driver.find_element_by_xpath("//input[@value='Sign In' and @type='button']")
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


Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Life-Science-Concepts-For-Middle-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Life-Science-Concepts-For-Middle-School"))
#exit()
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Earth-Science-Concepts-For-High-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Earth-Science-Concepts-For-High-School"))
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Earth-Science-Concepts-For-Middle-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Earth-Science-Concepts-For-Middle-School"))
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Physical-Science-Concepts-For-Middle-School/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Physical-Science-Concepts-For-Middle-School"))
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Biology-Concepts/",
                                  os.path.join(os.path.dirname(__file__), "../../../corpus/CK-12-Biology-Concepts"))
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Chemistry-Basic/",
                                  os.path.join(os.path.dirname(__file__), "../../../corpus/CK-12-Chemistry-Basic"))
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Chemistry-Concepts-Intermediate/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Chemistry-Concepts-Intermediate"))
Ck12CorpusCreater().download_book("https://www.ck12.org/book/CK-12-Physics-Concepts---Intermediate/",
                                  os.path.join(os.path.dirname(__file__),
                                               "../../../corpus/CK-12-Physics-Concepts-Intermediate"))
Ck12CorpusCreater().download_book(
    "https://www.ck12.org/book/CK-12-Modeling-and-Simulation-for-High-School-Teachers%253A-Principles-Problems-and-Lesson-Plans/",
    os.path.join(os.path.dirname(__file__),
                 "../../../corpus/CK-12-Modeling-and-Simulation-for-High-School-Teachers-Principles-Problems-and-Lesson-Plans/"))
