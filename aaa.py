from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_experimental_option("detach", True)
options.add_experimental_option("prefs", {
  "download.default_directory": r'/Users/wj/himedia/pdf_files',
  "download.prompt_for_download": False,
  "download.directory_upgrade": True,
  "safebrowsing.enabled": True
})

# driver_path = "/Users/wj/chromedriver_mac_arm64/chromedriver"
# service = Service(driver_path)
driver = webdriver.Chrome(options=options)

# 웹 페이지 열기
# url = "https://ampos.nanet.go.kr:7443/materialPolicyDetail.do?control_no=MONO1202051952"
url = "http://kmanifesto.or.kr/index.php/front/localList?mtype=assembly"
driver.get(url)
time.sleep(3)

# 다운로드 버튼 클릭
# button = driver.find_element(By.CLASS_NAME, "btn_file_download")

# button.click()

# 파일 다운로드를 위해 시간 대기
# time.sleep(5)

# 웹 드라이버 종료
# driver.quit()


try:
    # 홈 -> 국회의원 공약정보
    button = driver.find_element(By.CLASS_NAME, "ui-main-assembly")
    button.click()
    time.sleep(3)

    
    button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[memberid='4027']"))
    )
    button.click()
    time.sleep(3)

finally:
    # 작업이 끝나면 브라우저 닫기
    driver.quit()
