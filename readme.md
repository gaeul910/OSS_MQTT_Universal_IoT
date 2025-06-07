# Saja Project

Saja project is a Opensource-University Project, the goal of this project is to make user living-pattern based fully automated IoT system.

# How to install

## Server

```
git clone https://github.com/gaeul910/OSS_MQTT_Universal_IoT.git
cd OSS_MQTT_Universal_IoT/OSS_MQTT_Universal_IoT/
docker compose up -d
```

## Application

Please download package from release

# Dependencies

## Server

## Operating System

Windows, macOS, Linux

### Docker

The System with docker desktop/docker installed

### Container Dependencies

**Intrgration-Server**
PyMySQL >= 1.1.1
Flask >= 3.1.1
cryptography >= 45.0.3
bcrypt >= 4.3.0
flask-bcrypt >= 1.0.1
paho_mqtt >= 2.1.0

**Analytics-Server**
charset-normalizer==3.4.2
idna==3.10
joblib==1.5.0
numpy==2.2.4
pandas==2.2.3
python-dateutil==2.9.0.post0
pytz==2025.2
requests==2.32.3
scikit-learn==1.6.1
scipy==1.15.3
six==1.17.0
threadpoolctl==3.6.0
tzdata==2025.2
urllib3==2.4.0

# Application Dependencies
dependencies:
flutter:
sdk: flutter
geolocator: ^14.0.0
permission_handler: ^11.3.1
flutter_local_notifications: 19.2.1
cupertino_icons: ^1.0.8
verification_code_field: ^1.0.8
pinput: ^5.0.1
intl: ^0.18.0

dev_dependencies:
flutter_test:
sdk: flutter
mockito: ^5.0.0
# How to use
1. 어플리케이션 실행 시 위치 및 알림 권한 제공에 관한 권한을 요청합니다. 이를 모두 수락하면 로그인 페이지가 나옵니다.
2. 로그인 페이지에서는 ip, port번호, uid, 인증코드를 입력해야 합니다. 
3. 접속하고자 하는 서버의 ip와 port번호를 입력한 후, 서버 주소의 /connect로 접근해 나온 인증코드를 입력합니다. uid는 본인이 원하는 값을 입력합니다.
4. 올바른 인증코드를 입력했다면 로비 화면으로 넘어갑니다. 오른쪽 위의 햄버거 버튼을 통해 설정 기능에 들어갈 수 있습니다.
5. 설정 기능에는 다크모드, gps테스트, 본인의 세션 키 확인, 로그아웃이 존재합니다.
6. 다크모드는 on/off 형태로 끄고 켤 수 있으며, 활성화시 앱의 전체적인 테마가 어둡게 변합니다.
7. gps 테스트 기능은 gps 위치 추적을 끌 수 있으며, 현재 본인의 좌표를 위도와 경도로 확인할 수 있습니다.
8. 본인의 세션 키 확인 버튼을 눌러 현재 본인의 세션키를 확인할 수 있습니다. 매 자정 어플리케이션에서 자동으로 서버에서 새 세션 키를 받아옵니다.
9. 로그아웃 버튼을 눌러 2번의 과정으로 돌아갈 수 있습니다.
## Onboarding

1.  Please Install the server software at the 24/7 running server.
    The server must be connected to the IoT System network where the devices commuincate.

2.  Install Android Application to start tracking

3.  Navigate to http://server:3000/register to create root user.

4.  Navigate to http://server:3000/root_auth to authenticate as root.

5.  Navigate to http://server:3000/register to register a new user. As you're authenticated as root, you would be allowed to access user registration page.

6.  Create a new user. Administrator have a privillage to modify users in app.

7.  Finally, navigate to http://server:3000/connect, the application authentication code could be found here.

## Application Usage

#

# Contributers

정현욱(Hyunwook Chung) - chw910@chungbuk.ac.kr
류건길(Geongil Ryu) - fbrjsrlf@gmail.com
안효관(Hyogwan An) - acg030809@naver.com

# License

This software is under GPL-3.0 License
