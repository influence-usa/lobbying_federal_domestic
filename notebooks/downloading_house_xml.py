# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

!pip install selenium

# <codecell>

import json
import os
import sys
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

# <codecell>

sys.path.append(os.path.realpath(os.pardir))
sys.path

# <codecell>

import re

import settings
from tasks.utils import mkdir_p

# <codecell>

OUT_DIR = os.path.join(settings.CACHE_DIR,'house_clerk')

if not os.path.exists(OUT_DIR):
    mkdir_p(OUT_DIR)

# <codecell>

def go_to_url(driver, url):
    driver.get(search_url)
    
def print_current_page(driver):
    with open('tmp_pg_source','w') as fout:
        fout.write(driver.page_source.encode('utf-8'))

# <markdowncell>

# ### Firefox profile for auto-downloading

# <codecell>

fp = webdriver.FirefoxProfile()

fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.manager.showWhenStarting",False)
fp.set_preference("browser.download.dir", OUT_DIR)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                  "application/x-octet-stream")

driver = webdriver.Firefox(firefox_profile=fp)

# <codecell>

search_url = "http://disclosures.house.gov/ld/ldsearch.aspx"

# <codecell>

begin_time = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')

go_to_url(driver, search_url)

# <codecell>

dl_button = driver.find_element_by_css_selector(
                'html body div#search_container div#downloadLink p a')

# <codecell>

dl_button.click()

# <codecell>

driver.switch_to_frame('TB_iframeContent')

# <codecell>

filing_selector = driver.find_element_by_css_selector('select#selFilesXML')
for option in filing_selector.find_elements_by_tag_name('option'):
    print option.get_attribute("value")

# <codecell>

year=r''
space=r'(\ )'
filing_type=r'(?P<filing_type>(?P<filing_type_year>\d{4})\ (?P<filing_type_form>MidYear|Registrations|YearEnd|(1st|2nd|3rd|4th)Quarter))'
space=r'(\ )'
xml = '(XML)'
space = r'(\ )'
date=r'(\(\ (?P<updated_date>(?P<updated_date_day>\d{1,2})\/(?P<updated_date_month>\d{2})\/(?P<updated_date_year>\d{4})))'
space=r'(\ )'
time=r'(?P<updated_time>(?P<updated_time_hour>\d{1,2}):(?P<updated_time_min>\d{2}):(?P<updated_time_sec>\d{2})\ (?P<updated_time_am_pm>PM|AM)\))'

option_rgx = re.compile(filing_type+space+xml+space+date+space+time)

# <codecell>

options = [o for o in filing_selector.find_elements_by_tag_name('option')]

# <codecell>

options[0]

# <codecell>

options[0].get_attribute('value')

# <codecell>

test_set = zip(options, (re.match(option_rgx, o.get_attribute('value')) for o in options))

# <codecell>

for source, result in test_set:
    print source.get_attribute('value')
    try:
        print json.dumps(result.groupdict(), indent=2)
    except Exception as e:
        print "ERROR:",e

# <codecell>

options_with_metadata = zip(options, (re.match(option_rgx, o.get_attribute('value')).groupdict() for o in options))

# <codecell>

options_with_metadata

# <codecell>

option, metadata = options_with_metadata[3]

# <codecell>

option.click()

# <codecell>

driver.find_element_by_css_selector('#btnDownloadXML').click()

# <codecell>

for option, metadata in options_with_metadata:
    option.click()
    driver.find_element_by_css_selector('#btnDownloadXML').click()

# <codecell>


