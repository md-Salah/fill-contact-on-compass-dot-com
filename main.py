from sys import exit
import os
import random
import time
from selenium.webdriver.common.keys import Keys

from helpers.scraper import Scraper
from helpers.utility import formatted_time, data_countdown, countdown, execution_time
from helpers.files import read_csv, read_txt, write_to_csv, write_to_txt, read_contact_info
from helpers.numbers import formatted_number_with_comma, numbers_within_text, str_to_int

def is_visited(href):
    for prev in visited:
        if prev == [href]:
            return True
    return False

def fill_contact():
    name, email, phone = contact_info['name'], contact_info['email'], contact_info['phone']
    d.sleep(10, 12, True)
    contact_box = d.find_element('div[class^="contact-agent-box"]', loop_count=4, exit_on_missing_element=False)
    if contact_box:
        d.element_send_keys(name, 'input[name="name"]')
        d.element_send_keys(email, 'input[name="email"]')
        d.element_send_keys(phone, 'input[name="phone"]')
        d.sleep(1, 2)
        d.element_click('button[data-tn="listing-page-contact-agent-form-send-message"]')
        d.sleep(2, 3)
        d.sleep(5, 6, True)
        success_div = d.find_element('p[class="textIntent-title2"]', loop_count=3, exit_on_missing_element=False)
        if success_div and success_div.text.strip() == "Your message is sent.":
            return True
    
    return False        

def search():
    d.go_to_page('https://www.compass.com/')
    d.element_send_keys(contact_info['location'], '#location-lookup-input', loop_count=5)
    d.sleep(4, 5)
    d.element_click('ul[aria-label="Places suggestions"] li', loop_count=5)
    d.sleep(5, 8)    

def main():
    search()
    
    total_result_div = d.find_element('strong[data-tn="resultsBar-totalItemsCount"]', wait_element_time=10)
    total_result = str_to_int(total_result_div.text.strip())
    print('Total result: ', total_result)
    base_url, start = d.driver.current_url, 1
    
    page, count = 1, 0
    while True:
        homes = d.find_elements('h2[data-tn="uc-listingCard-title"] a')
        # print(f'\nPage: {page} Data Len: {len(homes)}')
        i = 0
        while i < len(homes):
            try:
                href = homes[i].get_attribute('href')
            except:
                homes = d.find_elements('h2[data-tn="uc-listingCard-title"] a')
                continue
            
            if is_visited(href):
                i += 1
                continue
                            
            d.element_click(element=homes[i], exit_on_missing_element=False)

            d.switch_to_tab(1)
            d.sleep(3, 4)
            success = fill_contact()
            if success:
                count += 1
                data_countdown(f'{count} contact filled.')
                visited.append([href])
                write_to_csv(visited, None, 'visited.csv')
            d.close_tab_and_back_homepage()
            i += 1
        
        page += 1
        start += 40
        if start >= total_result:
            print('\nEnd of result.')
            break
        else:
            next_page_url = base_url + f'start={start}/'
            d.go_to_page(next_page_url)
            d.sleep(7, 8)

            
if __name__ == "__main__":
    START_TIME = time.time()

    # Global variables
    visited = read_csv('visited.csv', header=None, exit_on_empty=False)
    contact_info = read_contact_info('inputs/contact_info.txt', '=')

    d = Scraper(exit_on_missing_element=False, profile='CompassDotCom')
    d.print_executable_path()
    
    main()
    
    # Footer for reporting
    execution_time(START_TIME)

    # Finally Close the browser
    input('Press any key to exit the browser...')
    d.driver.quit()
