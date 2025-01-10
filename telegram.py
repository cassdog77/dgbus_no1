import requests
import time
import os

# 텔레그램 봇 API 설정
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')  # 봇 API 토큰을 환경 변수에서 가져옴
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')      # 메시지를 보낼 채팅 ID

# 버스 도착 정보 가져오기
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
url = "https://businfo.daegu.go.kr:8095/dbms_web_api/realtime/arr/7061038700?_={}".format(str(int(time.time() * 1000)))
response = requests.get(url, headers=headers)
data = response.json()

buses = []
for bus in data.get('body', {}).get('list', []):
    if bus.get("routeNo") == "425" and bus.get("bsGap") < 4:
        # 텔레그램 메시지 전송 함수
        def send_telegram_message(message):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message
            }
            response = requests.post(url, data=payload)
            return response

        # 메시지 보내기
        message = "버스 425번이 도착했습니다!"
        send_telegram_message(message)