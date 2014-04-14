# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

import parse
import json
import os
import sys

from datetime import datetime

# <codecell>

OUT_DIR = os.path.join(os.getcwd(),'house_clerk_search_results')
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

# <codecell>

def go_to_url(driver, url):
    driver.get(search_url)

def search_begin(driver):
    search_button = driver.find_element_by_name('ctl00$cphMain$btnSearch')
    search_button.click()
    
def next_page(driver):
    paging_row = driver.find_element_by_css_selector('.pagingRow')
    paging_row_td = paging_row.find_element_by_tag_name('td')
    data_pager = paging_row_td.find_element_by_tag_name('span')
    pages = data_pager.find_elements_by_xpath('*')
    page_tags = [e.tag_name for e in pages]
    next_page = pages[page_tags.index('span') + 1]
    next_page.click()

def end_count(driver):
    search_records = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "searchRecords")))
    #search_records = driver.find_element_by_class_name('')
    search_records_text = search_records.text
    results = parse.parse("Records {} through {} of {}", search_records_text)
    if results[1] == results[2]:
        return True
    else:
        return False

def select_search_results_element(driver):
    search_results = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "search_results")))
    search_results_body = search_results.find_element_by_tag_name('tbody')
    return search_results_body
    
def scrape_rows(row_elements):
    for tr in row_elements:
        row = {'texts':tuple(),'urls':tuple()}
        for td in tr.find_elements_by_tag_name('td'):
            cell_text = td.text
            row['texts'] += (cell_text,)
            url = None
            try: 
                url = td.find_element_by_tag_name('a').get_attribute('href')
            except:
                pass
            row['urls'] += (url,)
        yield row
    
def scrape_table(table_element):
    search_results = table_element.find_elements_by_tag_name('tr')
    header_row = search_results[0]
    data_rows = [row for row in scrape_rows(search_results[1:-1])]
    paging_row = search_results[-1]
    headers = [td.text for td in header_row.find_elements_by_tag_name('font')]
    table = []
    for row in data_rows:
        row_dict = {k:{} for k in headers}
        for key,text_val,url_val in zip(headers,row['texts'],row['urls']):
            row_dict[key]['text'] = text_val
            row_dict[key]['url'] = url_val
        table.append(row_dict)
    return table

# <codecell>

search_url = 'http://clerk.house.gov/public_disc/financial-search.aspx'

# <codecell>

driver = webdriver.Firefox()
begin_time = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

go_to_url(driver, search_url)
search_begin(driver)

page = 1

done = False

while not done:
    table = scrape_table(select_search_results_element(driver))
    #should have zfill'd to three characters, probably more!
    out_fname = 'results_{begin_time}_{page}.json'.format(begin_time=begin_time, page=str(page).zfill(2))
    json.dump(table, open(os.path.join(OUT_DIR, out_fname),'w'))
    done = end_count(driver)
    next_page(driver)
    page += 1

#result_count = count_results(
#while row_count == 20:

