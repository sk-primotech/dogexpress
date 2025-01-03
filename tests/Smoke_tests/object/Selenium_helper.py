# In a file named selenium_helper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from concurrent.futures import ThreadPoolExecutor
from selenium.common.exceptions import TimeoutException
import inspect
import logging
import requests
import asyncio
import aiohttp
import time


class SeleniumHelper:
    def __init__(self, driver):
        self.driver = driver

    def getLogger(self):
        loggerName = inspect.stack()[1][3]
        logger = logging.getLogger(loggerName)
        fileHandler = logging.FileHandler("logfile.log")
        formatter = logging.Formatter(
            "%(asctime)s :%(levelname)s : %(name)s :%(message)s"
        )
        fileHandler.setFormatter(formatter)

        logger.addHandler(fileHandler)  # filehandler object

        logger.setLevel(logging.DEBUG)
        return logger

    def fetch_css_properties_for_element(self, element, css_properties_list):
        """
        Helper function to fetch all specified CSS properties for a given element.
        :param element: Web element
        :param css_properties_list: List of CSS properties to fetch
        :return: Set of fetched CSS property values
        """
        return {
            element.value_of_css_property(css_property)
            for css_property in css_properties_list
        }

    async def fetch_css_properties_async(self, element, css_properties_list):
        """
        Asynchronously fetch CSS properties by offloading the blocking task to a thread pool.
        :param element: Web element
        :param css_properties_list: List of CSS properties to fetch
        :return: Fetched CSS properties as a set
        """
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor()
        return await loop.run_in_executor(
            executor,
            self.fetch_css_properties_for_element,  # use instance method directly
            element,
            css_properties_list,
        )

    async def fetch_and_check_css_properties(
        self, css_selector, expected_css_properties, css_properties_list
    ):
        """
        Optimized with asyncio: Fetches CSS properties from elements using the given CSS selector
        and checks them against expected values.
        :param css_selector: CSS selector to locate elements
        :param expected_css_properties: Set of expected CSS properties
        :param css_properties_list: List of CSS properties to fetch
        :return: True if the fetched properties match the expected properties, False otherwise
        """
        wait = WebDriverWait(self.driver, 20)
        elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
        )

        try:
            fetched_css_properties = set()

            # Create a thread pool executor
            with ThreadPoolExecutor() as executor:
                # Schedule async tasks to fetch CSS properties for each element
                tasks = [
                    self.fetch_css_properties_async(element, css_properties_list)
                    for element in elements
                ]

                # Wait for all tasks to complete and gather results
                results = await asyncio.gather(*tasks)

            # Merge all fetched CSS properties
            for result in results:
                fetched_css_properties.update(result)

                # Early exit if all expected properties are fetched
                if fetched_css_properties == expected_css_properties:
                    return True

            # Final comparison after fetching all properties
            return fetched_css_properties == expected_css_properties

        except (StaleElementReferenceException, NoSuchElementException) as e:
            print(f"Error occurred: {str(e)}")
            return False

    def verify_links(self, selectors, additional_links, expected_link_count):
        all_links = []
        log = logging.getLogger()

        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            links = [element.get_attribute("href") for element in elements]
            all_links.extend(links)

        if additional_links:
            all_links.extend(additional_links)

        for link in all_links:
            self.driver.execute_script("window.open(arguments[0])", link)

        handles = self.driver.window_handles
        opened_links = []
        result_broken = []

        for window in handles:
            self.driver.switch_to.window(window)
            try:
                popup = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "#onesignal-slidedown-dialog .primary.slidedown-button",
                )
                popup.click()
            except Exception:
                ()
            opened_links.append(self.driver.current_url)

        assert set(all_links) == set(opened_links) or (
            len(all_links) == len(opened_links) or expected_link_count
        )

        for link in opened_links:
            response = requests.get(link)
            status_code = response.status_code
            if status_code == 404:

                result_broken.append("fail")
                log.info(f"Link {link} is broken with status code {status_code}")

            elif status_code != 404:
                result_broken.append("pass")

        assert all(element == "pass" for element in result_broken)

    def verify_linkscloud(
        self,
        selectors,
    ):
        all_links = []
        log = logging.getLogger()

        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            links = [element.get_attribute("href") for element in elements]
            all_links.extend(links)

        result_broken = []

        for link in all_links:
            response = requests.get(link)
            status_code = response.status_code
            if status_code == 404:

                result_broken.append("fail")
                log.info(f"Link {link} is broken with status code {status_code}")

            elif status_code != 404:
                result_broken.append("pass")

        assert all(element == "pass" for element in result_broken)

    async def check_link(session, link, log):
        try:
            async with session.head(link) as response:  # Using HEAD request
                status_code = response.status
                if status_code == 404:
                    log.info(f"Link {link} is broken with status code {status_code}")
                    return "fail"
                else:
                    return "pass"
        except Exception as e:
            log.error(f"Error checking link {link}: {e}")
            return "fail"

    # Define the asynchronous function to verify all links
    async def verify_links_async(self, selectors):
        all_links = []
        log = logging.getLogger()

        # Extract links using the provided selectors
        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            links = [
                element.get_attribute("href")
                for element in elements
                if element.get_attribute("href")
            ]
            all_links.extend(links)

        # Check links asynchronously
        async with aiohttp.ClientSession() as session:

            tasks = [
                SeleniumHelper.check_link(session, link, log) for link in all_links
            ]
            results = await asyncio.gather(*tasks)

        # Verify if all links are okay
        assert all(result == "pass" for result in results), "Some links are broken."

    def get_pseudo_element_styles(self, element, pseudo_element, property_name):
        return self.driver.execute_script(
            f"""
        var element = arguments[0];
        var pseudo = window.getComputedStyle(element, "{pseudo_element}");
        return pseudo.getPropertyValue("{property_name}");
        """,
            element,
        )
