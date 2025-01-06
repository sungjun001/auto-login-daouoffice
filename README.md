# auto-login-daouoffice
# 다우오피스 홈페이지에 로그인하여 출/퇴근 자동화 한다.

# python  가상환경 생성 명령어
python -m venv venv

# 가상 환경 실행
.\venv\Scripts\activate

# 필요 패키지 install
pip install -r .\requirements.txt

# 하나의 exe 파일로 만드는 방법 (바이러스 프로그램에 걸림.)
## pyinstaller 설치
pip install pyinstaller

## pyinstaller로 exe 파일 생성 명령어
pyinstaller --onefile --name <실행파일명> autologin.py
ex : pyinstaller --onefile --clean --noupx --name autologin autologin.py

## 파일 생성 명령어로 파일 생성 (default)
pyinstaller --onefile --clean --noupx --name autologin --hidden-import holidays --hidden-import holidays.countries --hidden-import holidays.constants --hidden-import holidays.holiday_base --hidden-import holidays.utils --hidden-import holidays.countries.korea autologin.py

<!-- # exe 파일로 만들지만 여러 파일이 필요한 방법 (바이러스 프로그램에 걸리지 않음.)
# nuitka 설치 
pip install -U nuitka

# nuitka 로 exe 파일 생성
python -m nuitka --mingw64 --standalone autologin.py -->

# 가상 환경 종료
.\venv\Scripts\deactivate