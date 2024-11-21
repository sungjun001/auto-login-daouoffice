import argparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from datetime import datetime
from dotenv import load_dotenv
import time
import os
import sys
import logging
import traceback

# 로그 파일 설정
logging.basicConfig(
    filename='auto_checkin.log',  # 로그 파일 이름
    level=logging.INFO,  # 로그 레벨
    format='%(asctime)s - %(levelname)s - %(message)s',  # 로그 포맷
    encoding='utf-8'  # UTF-8 인코딩
)

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

# 다우오피스 사용자 ID
USER_ID=your_id

# 다우오피스 비밀번호
USER_PASSWORD=your_password
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
    
    # 값이 하나라도 없으면 에러 발생
    if not all([home_url, user_id_input, user_password_input]):
        missing_vars = [var for var, value in {"HOME_URL": home_url, "USER_ID": user_id_input, "USER_PASSWORD": user_password_input}.items() if not value]
        logging.error(f"환경 변수 {', '.join(missing_vars)}가 설정되지 않았습니다.")    
        raise ValueError(f"환경 변수 {', '.join(missing_vars)}가 설정되지 않았습니다.")    

    # 드라이버 초기화 및 다우오피스 로그인
    driver = get_driver()
    driver.get(home_url)

    # 아이디와 비밀번호 입력
    user_id = driver.find_element(By.ID, "username")
    user_password = driver.find_element(By.ID, "password")
    user_id.send_keys(user_id_input)
    user_password.send_keys(user_password_input)
    user_password.send_keys(Keys.RETURN)

    # 페이지 로딩 대기
    time.sleep(5)

    # 현재 시간 및 요일 확인
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()  # 월요일=0, 금요일=4, 주말=5, 6

    # 월~금요일 동안에만 출근/퇴근 버튼 클릭 로직 실행
    if current_day < 5:  # 주말이 아닌 경우만 실행
        if 8 <= current_hour < 12:
            # 출근 버튼 클릭
            try:
                check_in_button = driver.find_element(By.ID, "workIn")
                check_in_button_status = check_in_button.get_attribute("class")
                if "off" not in check_in_button_status:
                    check_in_button.click()
                    logging.info("출근 기록 완료")
                else:
                    logging.info("이미 출근 기록이 되어 있습니다.")
            except Exception as e:
                logging.error("출근 버튼을 찾을 수 없습니다:", e)

        elif 18 <= current_hour < 24:
            # 퇴근 버튼 클릭
            try:
                work_out_button = driver.find_element(By.ID, "workOut")
                work_out_button_status = work_out_button.get_attribute("class")
                if "off" not in work_out_button_status:
                    work_out_button.click()
                    logging.info("퇴근 기록 완료")
                else:
                    logging.info("이미 퇴근 기록이 되어 있습니다.")
            except Exception as e:
                logging.error("퇴근 버튼을 찾을 수 없습니다:", e)
        else:
            logging.info("현재는 출퇴근 시간이 아닙니다.")
    else:
        logging.info("주말에는 출퇴근 기록을 하지 않습니다.")
except Exception as e:
    # 오류 발생 시 traceback 정보를 포함하여 로그에 기록
    error_message = f"An error occurred: {str(e)}\n"
    error_message += "Traceback:\n"
    error_message += traceback.format_exc()
    logging.error(error_message)        
    logging.error("실행중 에러가 발생하였습니다.:", e)    
    # 완료 후 브라우저 닫기
    
time.sleep(3)
driver.quit()
sys.exit("프로그램을 종료합니다.")
sys.exit(0)
