from Smoke_tests.utilities.base_class import BaseClass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HomePage(BaseClass):

    def __init__(self, driver):
        self.driver = driver
        self.view_more = "a.more-link"

    def login(self):

        links = []
        Ac = ActionChains(self.driver)
        wait = WebDriverWait(self.driver, 20)
        view_more = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.view_more))
        )
        time.sleep(10)
        for view in view_more:
            # Ac.move_to_element(view)

            # Ac.key_down(Keys.CONTROL).click(view).key_up(Keys.CONTROL).perform()

            # time.sleep(5)
            all_links = view.get_attribute("href")
            links.append(all_links)
        for li in links:
            self.driver.execute_script("window.open(arguments[0])", li)

    def hover(self):
        Ac = ActionChains(self.driver)
        wait = WebDriverWait(self.driver, 20)
        hover = "a.more-link:hover"
        view_more = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.view_more))
        )
        for view in view_more:
            log = self.getLogger()
            Ac.move_to_element(view).context_click(view).perform()
            hovercolor = self.driver.find_element(By.CSS_SELECTOR, hover)
            hover_value = hovercolor.value_of_css_property("background-color")
            log.info(hover_value)
            assert hover_value == "rgba(119, 119, 119, 1)"

        # script = '''
        #             const element = arguments[0];
        #             const style = window.getComputedStyle(element, '::after');
        #             return style.getPropertyValue('color');  // Replace 'content' with desired property
        #         '''
        # pseudo_content = self.driver.execute_script(script, self.view_more)
