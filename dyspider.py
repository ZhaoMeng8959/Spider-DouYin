#!/usr/bin/env/ python
# -*- coding:utf-8 -*-

import os
import json
import time
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

file_path = os.path.dirname(__file__)
with open(os.path.join(file_path, 'config.json'), encoding='UTF-8') as fp:
    CONFIG = json.load(fp)

tik_tok_prefix_url = 'https://www.douyin.com/user/'

file_save_path = file_path + r'/spider/'

display = Display(visible=0, size=(1920, 1080))
display.start()


# http://chromedriver.storage.googleapis.com/index.html
chrome_driver_path = file_path + '/chromedriver'
service = Service(executable_path=chrome_driver_path)
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(service=service, options=chrome_options)
browser.maximize_window()


def start():
    try:
        for tik_tok_id in CONFIG['tik_tok_id_list']:
            req_url = tik_tok_prefix_url + tik_tok_id
            browser.get(req_url)
            browser.implicitly_wait(10)
            handle_page_lazy_loading()
            save_userinfo()
            save_works()
    finally:
        browser.close()
        browser.quit()
        display.stop()


def handle_page_lazy_loading():
    window_height = [browser.execute_script('return document.body.scrollHeight;')]
    while True:
        browser.execute_script('scroll(0,100000)')
        time.sleep(3)
        half_height = int(window_height[-1]) / 2
        browser.execute_script('scroll(0,{0})'.format(half_height))
        browser.execute_script('scroll(0,100000)')
        time.sleep(3)
        check_height = browser.execute_script('return document.body.scrollHeight;')
        if check_height == window_height[-1]:
            break
        else:
            window_height.append(check_height)


def save_userinfo():
    username = browser.find_element(By.XPATH,
                                    '//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]/div[2]/h1/span/span/span/span/span').text
    filepath = file_save_path + username
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    os.chdir(filepath)
    file_name = '主页信息.txt'
    with open(file_name, 'a+', encoding='UTF-8') as file:
        file.write(browser.find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div[2]/div[1]').text)
        file.close()


def save_works():
    ul = browser.find_element(By.XPATH, "//*[@id='root']/div/div[2]/div/div/div[4]/div[1]/div[2]/ul")
    lis = ul.find_elements_by_xpath('li')
    li_len = len(lis)
    i = 0
    while i < li_len:
        try:
            forward_element = lis[i].find_element(By.XPATH, '//*[@id="root"]/div/div[2]/div/div/div[4]/div[1]/div[2]/ul/li[3]/a')
            browser.execute_script("arguments[0].scrollIntoView();", forward_element)
            forward_element.click()
        except:
            browser.find_element(By.XPATH, '//*[@id="login-pannel"]/div[2]').click()
            continue
        browser.switch_to.window(browser.window_handles[1])
        title = browser.find_element(By.XPATH,
                                     "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[1]/div/h1/span[2]").text
        favorite_num = browser.find_element(By.XPATH,
                                            "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[1]/div/span").text
        comment_num = browser.find_element(By.XPATH,
                                           "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[2]/span").text
        collect_num = browser.find_element(By.XPATH,
                                           "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[1]/div[3]/span").text
        release_time = browser.find_element(By.XPATH,
                                            "//*[@id='root']/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div[2]/span").text
        file_name = '抖音作品.txt'
        with open(file_name, 'a+', encoding='UTF-8') as file:
            print('----- 第' + str(i + 1) + '个抖音作品 -----')
            file.write('----- 第' + str(i + 1) + '个抖音作品 -----\n')
            file.write('标题: ' + title + '\n')
            file.write('获赞: ' + str(favorite_num) + '\n')
            file.write('评论: ' + str(comment_num) + '\n')
            file.write('收藏: ' + str(collect_num) + '\n')
            file.write(release_time + '\n')
            file.write('链接: ' + browser.current_url + '\n\n')
            file.close()
        browser.close()
        browser.switch_to.window(browser.window_handles[0])
        i = i + 1
        if i % 10 == 0:
            time.sleep(3)


if __name__ == '__main__':
    start()
