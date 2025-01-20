import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime
from dotenv import load_dotenv

import time
import os
import sys
import logging
import traceback
import random
import requests
import holidays


# 로그 파일 설정
logging.basicConfig(
    filename='auto_checkin.log',  # 로그 파일 이름
    level=logging.INFO,  # 로그 레벨
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 포맷
    encoding='utf-8'  # UTF-8 인코딩
)


def send_slack_message(webhook_url, message):
    try:
        payload = {"text": message}
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            logging.info("슬랙 메시지 전송 성공")
        else:
            logging.error(f"슬랙 메시지 전송 실패: {response.status_code}")
    except Exception as e:
        logging.error(f"슬랙 메시지 전송 중 오류 발생: {str(e)}")

def is_holiday():
    kr_holidays = holidays.KR()  # 한국 공휴일 정보
    today = datetime.now().date()
    return today in kr_holidays

try:



    # 실행 파일과 동일한 디렉토리에서 .env 파일을 찾습니다.
    if getattr(sys, 'frozen', False):
        # PyInstaller로 실행되는 경우, 임시 디렉토리 경로
        application_path = os.path.dirname(sys.argv[0])
    else:
        # 개발 중이라면 현재 실행 파일의 경로
        application_path = os.path.dirname(os.path.abspath(__file__))

    # .env 파일 경로 설정 (실행 디렉토리에서 생성)
    env_file_path = os.path.join(application_path, '.env')

    # .env 파일이 없으면 생성하고 예제 데이터를 추가합니다.
    if os.path.exists(env_file_path):
        logging.info(".env 파일이 존재합니다.")
    else:
        logging.info(".env 파일이 없습니다. 생성합니다.")
        
        # .env.example 파일 생성 및 예제 내용 작성
        example_content = """
# .env 파일 예제

# 회사 다우오피스 홈페이지 URL
HOME_URL="https://<subpath>.daouoffice.com/login?returnUrl=%2Fapp%2Fehr"

# 다우오피스 출퇴근 기록 페이지 URL
CHECK_IN_URL="https://<subpath>.daouoffice.com/app/ehr"

# 다우오피스 사용자 ID
USER_ID=your_id

# 다우오피스 비밀번호
USER_PASSWORD=your_password

# Slack Webhook URL
SLACK_WEBHOOK_URL=your_slack_webhook_url
    """
        # 파일을 생성하고 예제 내용을 쓴다
        with open(env_file_path, 'w', encoding='utf-8') as file:
            file.write(example_content)
        
        logging.info(".env 파일이 생성되었습니다.")
        logging.info(".env에 id/pwd 입력후 다시 실행해 주세요.")
        sys.exit("프로그램을 종료합니다.")
        sys.exit(0)

    def get_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument("disable-gpu")
        options.add_argument("window-size=1200,1100")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
        options.add_argument('--log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        driver = webdriver.Chrome(options=options)
        return driver

    # 명령줄 인자로 아이디와 비밀번호를 받기 위한 설정
    # parser = argparse.ArgumentParser(description="Daou Office 출퇴근 자동화")
    # parser.add_argument("--id", required=True, help="다우오피스 아이디")
    # parser.add_argument("--pwd", required=True, help="다우오피스 비밀번호")
    # args = parser.parse_args()

    # .env 파일 로드
    load_dotenv()

    # 환경변수에서 ID와 비밀번호 가져오기
    home_url = os.getenv("HOME_URL")
    user_id_input = os.getenv("USER_ID")
    user_password_input = os.getenv("USER_PASSWORD")
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    check_in_url = os.getenv("CHECK_IN_URL")
    
    # 값이 하나라도 없으면 에러 발생
    if not all([home_url, user_id_input, user_password_input]):
        missing_vars = [var for var, value in {"HOME_URL": home_url, "USER_ID": user_id_input, "USER_PASSWORD": user_password_input}.items() if not value]
        logging.error(f"환경 변수 {', '.join(missing_vars)}가 설정되지 않았습니다.")    
        raise ValueError(f"환경 변수 {', '.join(missing_vars)}가 설정되지 않았습니다.")    

    # 드라이버 초기화 및 다우오피스 로그인
    driver = get_driver()
    driver.get(home_url)
    
    # 페이지 로딩 대기
    element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))  # 여기에 대기할 요소의 ID를 넣습니다.
    )    
    
    if element:
        logging.info("LoginPage is fully loaded.")    
    else:
        logging.info("LoginPage is not fully loaded.")    

    # 아이디와 비밀번호 입력 및 로그인
    user_id = driver.find_element(By.ID, "username")
    user_password = driver.find_element(By.ID, "password")
    time.sleep(random.uniform(1, 2))
    user_id.send_keys(user_id_input)
    time.sleep(random.uniform(1, 2))
    user_password.send_keys(user_password_input)
    time.sleep(random.uniform(1, 2))
    user_password.send_keys(Keys.RETURN)

    # 비밀번호 변경 요청 페이지 처리
    try:
        # 비밀번호 변경 나중에 하기 버튼 찾기 (10초 동안 시도)
        change_later_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "changeLater"))
        )
        logging.info("비밀번호 변경 요청 페이지 발견")
        change_later_button.click()
        logging.info("나중에 변경하기 버튼 클릭")
        slack_message = f"🚨 비밀번호 변경 요청 페이지 발견\n"
        send_slack_message(slack_webhook_url, slack_message)
        time.sleep(2)  # 페이지 전환 대기
        driver.get(check_in_url)
    except Exception as e:
        # 비밀번호 변경 페이지가 없으면 그냥 진행
        logging.info("비밀번호 변경 요청 페이지 없음")
        driver.get(check_in_url)
        pass

    # 현재 시간 및 요일 확인
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()  # 월요일=0, 금요일=4, 주말=5, 6

    # workIn 버튼 찾기
    element = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.ID, "workIn"))
    )    
    
    if element:
        logging.info("WorkIn Page is fully loaded.")    
    else:
        logging.info("WorkIn Page is not fully loaded.")

    # 공휴일 체크
    if is_holiday():
        logging.info("오늘은 공휴일입니다.")
        if slack_webhook_url:
            slack_message = "🎉 오늘은 공휴일입니다. 출퇴근 기록을 하지 않습니다."
            send_slack_message(slack_webhook_url, slack_message)
        driver.quit()
        sys.exit("프로그램을 종료합니다.")

    # 월~금요일 동안에만 출근/퇴근 버튼 클릭 로직 실행
    if current_day < 5:  # 주말이 아닌 경우만 실행
        if 7 <= current_hour < 12:
            # 출근 버튼 클릭
            try:
                check_in_button = driver.find_element(By.ID, "workIn")
                check_in_button_status = check_in_button.get_attribute("class")
                if "off" not in check_in_button_status:
                    check_in_button.click()
                    logging.info("출근 기록 완료")
                    if slack_webhook_url:
                        slack_message = f"✅ 출근 기록 완료\n"
                        send_slack_message(slack_webhook_url, slack_message)                    
                else:
                    logging.info("이미 출근 기록이 되어 있습니다.")
                    if slack_webhook_url:
                        slack_message = f"🚨 이미 출근 기록이 되어 있습니다.\n"
                        send_slack_message(slack_webhook_url, slack_message)                    
            except Exception as e:
                logging.error("출근 버튼을 찾을 수 없습니다:", e)
                if slack_webhook_url:
                    slack_message = f"🚨 출근 버튼을 찾을 수 없습니다\n"
                    send_slack_message(slack_webhook_url, slack_message)                

        elif 16 <= current_hour < 24:
            # 퇴근 버튼 클릭
            try:
                work_out_button = driver.find_element(By.ID, "workOut")
                work_out_button_status = work_out_button.get_attribute("class")
                if "off" not in work_out_button_status:
                    work_out_button.click()
                    logging.info("퇴근 기록 완료")
                    if slack_webhook_url:
                        slack_message = f"✅ 퇴근 기록 완료\n"
                        send_slack_message(slack_webhook_url, slack_message)
                else:
                    logging.info("이미 퇴근 기록이 되어 있습니다.")
                    if slack_webhook_url:
                        slack_message = f"🚨 이미 퇴근 기록이 되어 있습니다.\n"
                        send_slack_message(slack_webhook_url, slack_message)                    
            except Exception as e:
                logging.error("퇴근 버튼을 찾을 수 없습니다:", e)
                if slack_webhook_url:
                    slack_message = f"🚨 퇴근 버튼을 찾을 수 없습니다\n"
                    send_slack_message(slack_webhook_url, slack_message)                
        else:
            logging.info("현재는 출퇴근 시간이 아닙니다.")
            if slack_webhook_url:
                slack_message = f"🚨 현재는 출퇴근 시간이 아닙니다.\n"
                send_slack_message(slack_webhook_url, slack_message)            
    else:
        logging.info("주말에는 출퇴근 기록을 하지 않습니다.")
except Exception as e:
    # 오류 발생 시 traceback 정보를 포함하여 로그에 기록
    error_message = f"An error occurred: {str(e)}\n"
    error_message += "Traceback:\n"
    error_message += traceback.format_exc()
    logging.error(error_message)        
    logging.error("실행중 에러가 발생하였습니다.: %s", str(e))    
    # 완료 후 브라우저 닫기
    
    # 슬랙으로 에러 메시지 전송
    if slack_webhook_url:
        slack_message = f"🚨 다우오피스 자동 출퇴근 오류 발생\n```{error_message}```"
        send_slack_message(slack_webhook_url, slack_message)

time.sleep(3)
driver.quit()
sys.exit("프로그램을 종료합니다.")
sys.exit(0)

