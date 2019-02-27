"""
This app aims to fill in some gaps left by the Ninite Pro web interface,
such as the lack of an API from which to fetch reports, add/remove machines, modify policies, etc.

By scheduling or scripting this app, you could also automate the process of
running reports on a regular schedule, or install the agent silently in the background
without needing to first log in and download the agent installer.

Kat Winter 2019
"""

from os import getcwd
import argparse
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

import settings

# Ideally the driver setup might be separated out rather than setting this all globally
options = webdriver.FirefoxOptions()
options.add_argument("-headless")

fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList", 2)
fp.set_preference("browser.download.manager.showWhenStarting", False)
fp.set_preference("browser.download.dir", getcwd())
fp.set_preference("browser.download.useDownloadDir", True)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/csv")

driver = webdriver.Firefox(executable_path="geckodriver.exe", options=options, firefox_profile=fp)


def main():
    parser = argparse.ArgumentParser(description=
                                     "Utility to provide a command-line interface for installing the Ninite agent or "
                                     "running reports. Please note that the install option is Windows-only, and that "
                                     "at this time, Ninite accounts with two-factor authentication are not supported.")
    parser.add_argument("email", help="Your Ninite login email")
    parser.add_argument("password", help="Your Ninite login password")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-r", "--reports", help="Download .csv reports from Apps and Machine Details",
                       action="store_true")
    group.add_argument("-i", "--install", help="Download and install the agent .msi", action="store_true")

    args = parser.parse_args()

    email = args.email
    pw = args.password

    if login(email, pw):
        print("Login successful")
        if args.reports:
            _download_reports()

        if args.install:
            _install_agent()
    else:
        print("There was a problem logging in. Please ensure you do NOT have two-factor authentication enabled.")

    driver.quit()


def login(email, pw):
    signin_url = "https://ninite.com/signin/"
    driver.get(signin_url)

    email_field = driver.find_element_by_css_selector(settings.USERNAME_SELECTOR)
    email_field.send_keys(email)

    password_field = driver.find_element_by_css_selector(settings.PASSWORD_SELECTOR)
    password_field.send_keys(pw)

    login = driver.find_element_by_xpath(settings.LOGIN_BUTTON_XPATH)
    login.click()

    driver.get('https://ninite.com/pro-interface')
    # Page title changes once successfully logged in, so this can help us verify
    # that login was successful (Selenium does not provide the HTTP status code)
    return driver.title == "Ninite Pro"


# Navigate to the Apps tab and download the .csv,
# then navigate to the Machine Details tab and download the .csv.
def _download_reports():
    if _element_present("XPATH", settings.APPS_XPATH):
        app_button = driver.find_element_by_xpath(settings.APPS_XPATH)
        app_button.click()

        if _element_present("CSS_SELECTOR", settings.CSV_SELECTOR):
            apps_csv_button = driver.find_element_by_css_selector(settings.CSV_SELECTOR)
            apps_csv_button.click()
            print("downloading apps report...")
            time.sleep(5)

    if _element_present("XPATH", settings.MACHINES_XPATH):
        machines_button = driver.find_element_by_xpath(settings.MACHINES_XPATH)
        machines_button.click()

        if _element_present("CSS_SELECTOR", settings.CSV_SELECTOR):
            machines_csv_button = driver.find_element_by_css_selector(settings.CSV_SELECTOR)
            machines_csv_button.click()
            if machines_csv_button.get_attribute("download") == "machines.csv":
                print("downloading machine details report...")
                time.sleep(5)

    print("Report downloads complete.")


# Download the agent.msi file and run using msiexec
def _install_agent():
    if _element_present("XPATH", settings.DOWNLOAD_AGENT_XPATH):
        download_button = driver.find_element_by_xpath(settings.DOWNLOAD_AGENT_XPATH)
        download_button.click()

        if _element_present("XPATH", settings.MSI_INSTALLER_XPATH):
            msi_download = driver.find_element_by_xpath(settings.MSI_INSTALLER_XPATH)
            msi_download.click()
            print("downloading agent...")
            time.sleep(5)

            print("installing...")
            subprocess.call('msiexec /i agent.msi', shell=True)
            print("Agent installer downloaded and run. Please verify that installation was successful.")


# Helper function to ensure that elements have time to load, because after login,
# the pages are all rendered entirely through Javascript and sometimes loads too
# slowly an immediate check to be successful.
# This function alleviates this issue by allowing up to 10 seconds before reporting
# if the element is present, and will throw an exception if it times out and the
# element still wasn't found.
def _element_present(element_type, element):
    element_present = expected_conditions.presence_of_element_located((getattr(By, element_type), element))
    WebDriverWait(driver, 10).until(element_present)
    return True


if __name__ == '__main__':
    main()
