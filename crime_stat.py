import os
import time
import regex as re
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
import pandas as pd
import crime_stat.crime_consts as const
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


class CrimeStat(uc.Chrome):

    def __init__(self, driver_path=r"C:\Program Files (x86)\chromedriver_win32", teardown=False, headless=False):
        self.driver_path = driver_path
        self.teardown = teardown
        os.environ['PATH'] += self.driver_path
        self.headless = headless
        opt = webdriver.ChromeOptions()
        if self.headless:
            opt.add_argument('--headless=new')
            super(CrimeStat, self).__init__(options=opt)
        else:
            super(CrimeStat, self).__init__(options=opt)
        self.implicitly_wait(20)
        self.maximize_window()

    '''
    function: page
        the function opens the web on the main page.
    '''

    def page(self):
        time.sleep(2)
        self.get(const.CRIME_URL)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    '''
    function: search_crime_bar
    @param name of a city
        the function gets name of a city and searching for it.
    '''
    def search_crime_bar(self, city=""):
        action = ActionChains(self)
        search = self.find_element(By.ID, "intelligent_search")
        action.move_to_element(search)
        action.click(search)
        time.sleep(4)
        search.clear()
        action.send_keys(city)
        action.move_to_element(self.find_element(By.CSS_SELECTOR, "input[value='Go']")).click()
        action.perform()

    '''
    function: search_crime_bar
    @param crime_scrap
        the function gets name of a city and flag.
    return  data frame with the crime statistics on the city.
    '''
    def crime_scrap(self, city,flag):
        self.search_crime_bar(city[0])
        time.sleep(2)
        flag = 0
        action = ActionChains(self)
        try:
            table = self.find_element(By.ID, "crimeTab")
        except TimeoutException:
            return None, flag
        except NoSuchElementException:
            return None, flag
        except Exception:
            return None, flag

        action.move_to_element(table).perform()
        head = table.find_element(By.TAG_NAME, 'thead')
        years = head.find_elements(By.CLASS_NAME, 'head')
        col_years = list()
        city_name = list()
        for year in years:
            city_name.append(city[1])
            col_years.append(year.text)
        rows = list()
        rows.append(city_name)
        rows.append(col_years)
        table_body = table.find_element(By.TAG_NAME, 'tbody')
        cols = list()
        cols.append("city_name")
        cols.append("Year")
        table_rows = table_body.find_elements(By.TAG_NAME, 'tr')
        for tr in table_rows:
            row = []
            cells = tr.find_elements(By.TAG_NAME, 'td')
            cols.append(cells[0].text.replace("\n", " "))
            for cell in cells[1:]:
                pattern = "\((.*)\)"
                value = cell.text.splitlines()[1].replace(",", "")
                txt = re.search(pattern, value)
                if txt:
                    row.append(float(txt.group(1)))
                else:
                    row.append(float(value))

            rows.append(row)

        foot = table.find_element(By.TAG_NAME, 'tfoot')
        foot_row = foot.find_element(By.TAG_NAME, 'tr')
        tds = foot_row.find_elements(By.TAG_NAME, 'td')
        row = []
        cols.append(tds[0].text.replace("\n", " "))
        for td in tds[1:]:
            row.append(float(td.text.replace(",", "")))

        rows.append(row)
        table = dict()

        for col, row in zip(cols, rows):
            table[col] = row
        return pd.DataFrame(table), flag



