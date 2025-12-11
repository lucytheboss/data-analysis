import pandas as pd
import re
import glob
from datetime import datetime

# 로그 파일 경로 (logs 폴더 안의 모든 .txt 파일)
file_paths = glob.glob("logs/log_*.txt")

# 로그 정규 표현식
log_pattern = re.compile(
    r"(?P<utc_time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z) "
    r"\[(?P<local_time>.*?)\] "
    r"IP=(?P<ip>[\d\.]+) "
    r"METHOD=(?P<method>\w+) "
    r"URI=(?P<uri>\S+) "
    r"STATUS=(?P<status>\d{3}) "
    r"TIME=(?P<time>\d+)ms "
    r"UA=(?P<user_agent>.+)"
)

# 로그 수집
logs = []

for path in file_paths:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = log_pattern.match(line.strip())
            if match:
                logs.append(match.groupdict())

# DataFrame으로 변환
df = pd.DataFrame(logs)

# 로그 총 개수
print(f"총 요청 수: {len(df)}")

# 시간대별 요청 수
df["hour"] = pd.to_datetime(df["local_time"]).dt.hour
print("\n시간대별 요청 수:")
print(df["hour"].value_counts().sort_index())


# 1. 디바이스 모델 추출
def extract_device_type(ua):
    ua = ua.lower()
    if "iphone" in ua:
        return "iPhone"
    elif "ipad" in ua:
        return "iPad"
    elif "macintosh" in ua:
        return "Mac"
    elif "windows" in ua:
        return "Windows PC"
    elif "android" in ua:
        match = re.search(r"android [\d\.]+; ([^;)]+)", ua)
        if match:
            device = match.group(1).strip()
            device = re.sub(r"build.*", "", device).strip()  # build 이후 제거
            if len(device) < 3:  # 'K' 같은 이상값 걸러냄
                return "Unknown Android"
            return device
        else:
            return "Unknown Android"
    else:
        return "Other"


# 2. 접속 플랫폼 추출 (브라우저나 앱)
def extract_app_or_browser(ua):
    ua = ua.lower()
    if "kakaotalk" in ua:
        return "KakaoTalk"
    elif "naver" in ua:
        return "NaverApp"
    elif "crios" in ua:
        return "Chrome (iOS)"
    elif "chrome" in ua:
        return "Chrome"
    elif "samsungbrowser" in ua:
        return "Samsung Browser"
    elif "safari" in ua and "version" in ua:
        return "Safari"
    elif "everytimeapp" in ua:
        return "EverytimeApp"
    elif "whale" in ua:
        return "Naver Whale"
    elif "windows" in ua:
        return "Windows Browser"
    elif "macintosh" in ua:
        return "Mac Browser"
    else:
        return "Other"


# 3. OS 타입 분류 (iOS / Android / PC)
def classify_os(device):
    device = device.lower()
    if "iphone" in device or "ipad" in device:
        return "iOS"
    elif "windows" in device or "mac" in device:
        return "PC"
    else:
        return "Android"


# 4. 컬럼 추가
df["device_type"] = df["user_agent"].apply(extract_device_type)
df["agent_type"] = df["user_agent"].apply(extract_app_or_browser)
df["os_type"] = df["device_type"].apply(classify_os)

# 5. 결과 출력
print("\n📱 기기 종류별 요청 수 (상위 10개):")
print(df["device_type"].value_counts().head(10))

print("\n🌐 접속 플랫폼별 요청 수 (상위 10개):")
print(df["agent_type"].value_counts().head(10))

print("\n🧠 운영체제(OS)별 요청 수:")
print(df["os_type"].value_counts())
