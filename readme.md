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

### Application Onboarding

1. When Application Starts, Neccessary permissions must be accepted. After accept, Login page appears.

2. Login must contain ip address, port number, user id, and authentication code.

3. Please enter the server information. Open http://server:3000/connect to get authentication code. For more info, read Onboarding document above.

4. When authentication succeed, Lobby screen opens. Click on the hamburger menu at top right to open settings.

5. In settings, you can find dark mode, gps test feature, check session key for application, and logout button.

### Application Features

- Dark mode
  Dark mode can be on and off, When dark mode is active, the application theme changes dark.

- GPS test
  GPS test feature can turn off GPS tracking. Also, you can check the current coordiness.

- Session key
  Show session key button shows the application session key.

- Logout

9. You can log out using logout button.

# Contributers

정현욱(Hyunwook Chung) - chw910@chungbuk.ac.kr
류건길(Geongil Ryu) - fbrjsrlf@gmail.com
안효관(Hyogwan An) - acg030809@naver.com

# License

This software is under GPL-3.0 License
