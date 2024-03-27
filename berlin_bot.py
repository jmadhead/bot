import time
import os
import logging
from platform import system

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

# click a.ui-state-default

system = system()

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    level=logging.INFO,
)

class WebDriver:
    def __init__(self):
        self._driver: webdriver.Chrome
        self._implicit_wait_time = 20

    def __enter__(self) -> webdriver.Chrome:
        logging.info("Open browser")
        # some stuff that prevents us from being locked out
        options = webdriver.ChromeOptions() 
        options.add_argument('--disable-blink-features=AutomationControlled')
        self._driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        #self._driver = webdriver.Chrome(options=options)
        self._driver.implicitly_wait(self._implicit_wait_time) # seconds
        self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        return self._driver

    def __exit__(self, exc_type, exc_value, exc_tb):
        logging.info("Close browser")
        self._driver.quit()

class BerlinBot:
    def __init__(self):
        self.wait_time = 20
        self._error_message = """Für die gewählte Dienstleistung sind aktuell keine Termine frei! Bitte"""

    @staticmethod
    def enter_start_page(driver: webdriver.Chrome):
        logging.info("Visit start page")
        driver.get("https://otv.verwalt-berlin.de/ams/TerminBuchen")
        driver.find_element(By.XPATH, '//*[@id="mainForm"]/div/div/div/div/div/div/div/div/div/div[1]/div[1]/div[2]/a').click()
        time.sleep(5)

    @staticmethod
    def tick_off_some_bullshit(driver: webdriver.Chrome):
        logging.info("Ticking off agreement")
        driver.find_element(By.XPATH, '//*[@id="xi-div-1"]/div[4]/label[2]/p').click()
        time.sleep(1)
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        time.sleep(5)

    @staticmethod
    def enter_form(driver: webdriver.Chrome):
        logging.info("Fill out form")
        # select china
        s = Select(driver.find_element(By.ID, 'xi-sel-400'))
        s.select_by_visible_text("Russische Föderation")
        # eine person
        s = Select(driver.find_element(By.ID, 'xi-sel-422'))
        s.select_by_visible_text("eine Person")

        s = Select(driver.find_element(By.ID, 'xi-sel-427' ))
        s.select_by_visible_text("ja")
        
        s = Select(driver.find_element(By.ID, 'xi-sel-428' ))
        s.select_by_visible_text("Russische Föderation")
        
        time.sleep(5)

        
        elementToBeClicked = driver.find_element(By.XPATH, '//*[@id="xi-div-30"]/div[2]/label/p')
        print(elementToBeClicked.text)
        elementToBeClicked.click()
        time.sleep(2)

        #elementToBeClicked = driver.find_element(By.XPATH, '//*[@id="inner-479-0-2"]/div/div[3]/label/p')
        elementToBeClicked = driver.find_element(By.XPATH, "//*[contains(text(), 'Familiäre Gründe')]")
        print(elementToBeClicked.text)
        elementToBeClicked.click()
        time.sleep(2)

        #elementToBeClicked = driver.find_element(By.XPATH, '//*[@id="inner-479-0-2"]/div/div[3]/div/div[3]/label')
        elementToBeClicked = driver.find_element(By.XPATH, "//*[contains(text(), 'Aufenthaltserlaubnis für Ehepartner, Eltern und Kinder von ausländischen Familienangehörigen (§§ 29-34)')]")
        print(elementToBeClicked.text)
        elementToBeClicked.click()        
        time.sleep(4)

        # submit form
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        time.sleep(10)
    
    def _success(self):
        logging.info("!!!SUCCESS - do not close the window!!!!")
        os.system('afplay -v 30 -t 0.5 /System/Library/Sounds/Ping.aiff')
        os.system('afplay -v 30 -t 0.5 /System/Library/Sounds/Ping.aiff')
        os.system('afplay -v 30 -t 0.5 /System/Library/Sounds/Ping.aiff')
        while True:
            time.sleep(30)

    def run_once(self):
        print('\n')
        with WebDriver() as driver:

            try:
                self.enter_start_page(driver)
                self.tick_off_some_bullshit(driver)
                self.enter_form(driver)
            except Exception as e:
                print('Error: ')
                print(e)
                return

            # retry submit
            for _ in range(20):
#                if not self._error_message in driver.page_source:
#                    self._success()
                if "Auswahl Termin" in driver.page_source:
                    try:
                       driver.find_element(By.XPATH, "//*[@class='ui-state-default']").click()
                    except Exception as e:
                       print('Error clicking: ')
                       print(e)
# click a.ui-state-default
                    self._success()
                logging.info("Retry submitting form")
                driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
                time.sleep(self.wait_time)

    def run_loop(self):        
        while True:
            logging.info("One more round")
            self.run_once()
            time.sleep(self.wait_time)

if __name__ == "__main__":
    BerlinBot().run_loop()
