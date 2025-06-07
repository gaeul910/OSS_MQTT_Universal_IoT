import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
import secrets
from flask import Flask
from flask_bcrypt import Bcrypt
import sys
import os

# 테스트를 위해 모듈을 임포트하기 전에 필요한 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

access_token = "token"

class TestFlaskApp(unittest.TestCase):
    
    def setUp(self):
        """각 테스트 전에 실행되는 설정"""
        # Mock dependencies
        self.mock_configparser = MagicMock()
        self.mock_pymysql = Mock()
        self.mock_mqtt_client = Mock()

        # Patch external dependencies
        self.patcher_configparser = patch('configparser.ConfigParser')
        self.patcher_pymysql = patch('pymysql.connect')
        self.patcher_mqtt = patch('mqtt_module.MQTTClient')

        self.mock_config = self.patcher_configparser.start()
        self.mock_db = self.patcher_pymysql.start()
        self.mock_mqtt = self.patcher_mqtt.start()

        # config.properties와 mqtt.properties에 맞는 Mock 반환값 설정
        def config_read_side_effect(filename):
            self.mock_configparser._filename = filename

        def config_getitem_side_effect(key):
            if self.mock_configparser._filename == "./config.properties":
                if key == "CONNECTION":
                    return {
                        'host': 'localhost',
                        'port': '3306',
                        'user': 'root',
                        'password': 'defaultpassword1',
                        'db': 'iot-db'
                    }
                elif key == "SERVICES":
                    return {'1': 'service1.domain.com', '2': 'service2.domain.com'}
                elif key == "SERVICES_ID":
                    return {'1': 'svc1', '2': 'svc2'}
            elif self.mock_configparser._filename == "./mqtt.properties":
                if key == "BROKER":
                    return {'host': 'mqtt-broker.local'}
            raise KeyError(key)

        self.mock_config.return_value = self.mock_configparser
        self.mock_configparser.read.side_effect = config_read_side_effect
        self.mock_configparser.__getitem__.side_effect = config_getitem_side_effect

        # Mock database connection and cursor
        self.mock_cursor = Mock()
        self.mock_db.return_value.cursor.return_value = self.mock_cursor

        # Import and setup app after mocking
        from main import app  # Replace with actual filename
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        if 'bcrypt' not in self.app.extensions:
            self.app.extensions['bcrypt'] = Bcrypt(self.app)
            
        
    def tearDown(self):
        """각 테스트 후에 실행되는 정리"""
        self.patcher_configparser.stop()
        self.patcher_pymysql.stop()
        self.patcher_mqtt.stop()

class TestAuthenticationRoutes(TestFlaskApp):
    
    def test_root_auth_get_success(self):
        """Root 인증 페이지 GET 요청 테스트"""
        # Mock user_search to return 1 (user exists)
        with patch('main.user_search', return_value=1):
            response = self.client.get('/root_auth')
            self.assertEqual(response.status_code, 200)
    
    def test_root_auth_get_no_root_user(self):
        """Root 사용자가 없을 때 GET 요청 테스트"""
        with patch('main.user_search', return_value=-2):
            response = self.client.get('/root_auth')
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Root user does not Exist', response.data)
    
    def test_root_auth_post_success(self):
        """Root 인증 POST 성공 테스트"""
        with patch('main.user_search', return_value=1), \
            patch('main.gen_session', return_value='test_session_token_12345'), \
            patch('main.cursor', self.mock_cursor):
            
            # Mock the database response with a properly formatted bcrypt hash
            test_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PJ/...'
            self.mock_cursor.fetchone.return_value = {'password': test_hash}
            self.mock_cursor.execute.return_value = None
            
            # Mock bcrypt to avoid actual hashing/checking
            with patch('main.bcrypt.check_password_hash', return_value=True) as mock_bcrypt:
                response = self.client.post('/root_auth', data={'password': 'test_password'})
                
                # Verify bcrypt was called with correct parameters
                mock_bcrypt.assert_called_once_with(test_hash, 'test_password')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Authentication success', response.data)
                
    def test_register_user_post_success(self):
        """일반 사용자 등록 POST 성공 테스트 (root 존재, 인증 성공)"""
        with patch('main.user_search', return_value=1), \
            patch('main.auth_user', return_value=0), \
            patch('main.gen_id', return_value=123):
            response = self.client.post('/register', data={
                'permission': 'Admin'
            })
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Process Successful', response.data)

    def test_register_user_post_invalid_permission(self):
        """일반 사용자 등록 POST 실패 테스트 (permission 값 잘못됨)"""
        with patch('main.user_search', return_value=1), \
            patch('main.auth_user', return_value=0), \
            patch('main.gen_id', return_value=123):
            response = self.client.post('/register', data={
                'permission': 'InvalidRole'
            })
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Invalid Request', response.data)
            
    def test_auth_user_not_successful(self):
        """auth_user가 인증 실패(-2) 반환 시 케이스"""
        with patch('main.delete_expired_session', return_value=0), \
             patch('main.cursor', self.mock_cursor):
            # 세션이 없을 때 fetchone()이 None 반환
            self.mock_cursor.fetchone.return_value = None
            from main import auth_user
            result = auth_user('invalid_token')
            self.assertEqual(result, -2)

    def test_auth_user_db_error(self):
        """auth_user에서 DB 오류 발생 시 -1 반환"""
        with patch('main.delete_expired_session', return_value=0), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.execute.side_effect = Exception('DB error')
            from main import auth_user
            result = auth_user('any_token')
            self.assertEqual(result, -1)


def test_root_auth_post_invalid_password(self):
    """Root 인증 POST 잘못된 비밀번호 테스트"""
    with patch('main.user_search', return_value=1), \
         patch('main.cursor', self.mock_cursor):
         
        # Use fetchone() and return a single dictionary
        self.mock_cursor.fetchone.return_value = {'password': '$2b$12$test_hash'}
        
        with patch.object(self.app.extensions['bcrypt'], 'check_password_hash', return_value=False):
            response = self.client.post('/root_auth', data={'password': 'wrong_password'})
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Password Invalid', response.data)

class TestAuthFeature(TestFlaskApp):
    def test_getstats_auth_required(self):
        """MQTT getstats 인증 필요"""
        response = self.client.get('/protocol/mqtt/getstats')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_logs_auth_required(self):
        """logs 인증 필요"""
        response = self.client.get('/location/logs')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_latest_auth_required(self):
        """latest 인증 필요"""
        response = self.client.get('/location/latest')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_point_auth_required(self):
        """point 인증 필요"""
        response = self.client.get('/location/fav/point')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_route_auth_required(self):
        """route 인증 필요"""
        response = self.client.get('/location/fav/route')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_visits_auth_required(self):
        """visits 인증 필요"""
        response = self.client.get('/event/visits')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_eventlogs_auth_required(self):
        """eventlogs 인증 필요"""
        response = self.client.get('/event/eventlogs')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_getnoti_auth_required(self):
        """getnoti 인증 필요"""
        response = self.client.get('/notification/getnoti')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_postnoti_auth_required(self):
        """postnoti 인증 필요"""
        response = self.client.post('/notification/postnoti')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_sync_auth_required(self):
        """sync 인증 필요"""
        response = self.client.get('/notification/sync')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Session not found', response.data)

    def test_auth_invalid_token(self):
        """잘못된 토큰"""
        headers = {"Session-Token": "invalidtoken"}
        response = self.client.get('/protocol/mqtt/getstats', headers=headers)
        self.assertIn(response.status_code, [403, 500])  # Invalid Session or Server Error

    def test_auth_valid_token_permission_denied(self):
        """정상 토큰, 권한 없음"""
        with patch('main.auth_user', return_value=1), \
             patch('main.check_permission', return_value=0):
            response = self.client.get('/event/visits', headers={'Session-Token': 'validtoken'}, json={'location_id': 1, 'lookup_days': 1})
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Permission Denied', response.data)
            
class TestGetServicesAddress(TestFlaskApp):
    def test_get_services_address_success(self):
        """서비스 도메인 -> IP 변환 성공 테스트"""
        # services dict mocking
        test_services = {
            '1': {'service_domain': 'service1.domain.com', 'service_id': 'svc1'},
            '2': {'service_domain': 'service2.domain.com', 'service_id': 'svc2'}
        }
        with patch('main.services', test_services), \
             patch('socket.gethostbyname', side_effect=lambda domain: {
                 'service1.domain.com': '10.0.0.1',
                 'service2.domain.com': '10.0.0.2'
             }[domain]):
            from main import get_services_address
            result = get_services_address()
            self.assertEqual(result, {'svc1': '10.0.0.1', 'svc2': '10.0.0.2'})

    def test_get_services_address_dns_fail(self):
        """DNS 변환 실패 시 0 반환 테스트"""
        test_services = {
            '1': {'service_domain': 'service1.domain.com', 'service_id': 'svc1'},
            '2': {'service_domain': 'bad.domain.com', 'service_id': 'svc2'}
        }
        def fake_gethostbyname(domain):
            if domain == 'service1.domain.com':
                return '10.0.0.1'
            else:
                raise Exception("DNS error")
        with patch('main.services', test_services), \
             patch('socket.gethostbyname', side_effect=fake_gethostbyname):
            from main import get_services_address
            result = get_services_address()
            self.assertEqual(result, {'svc1': '10.0.0.1', '2': 0})
            
class TestCheckPermission(TestFlaskApp):
    def test_check_permission_valid(self):
        """권한이 정상적으로 반환되는 경우"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.return_value = {'permission': 1}
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(1, perms_list)
            self.assertEqual(result, 100)

    def test_check_permission_invalid_uid(self):
        """DB에 해당 uid가 없을 때 (fetchone None)"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.return_value = None
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(999, perms_list)
            self.assertEqual(result, -1)

    def test_check_permission_db_error(self):
        """DB 오류 발생 시 -1 반환"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.side_effect = Exception('DB error')
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(1, perms_list)
            self.assertEqual(result, -1)

    def test_check_permission_permission_index_error(self):
        """permission 값이 perms_list 범위를 벗어날 때 IndexError로 -1 반환"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.return_value = {'permission': 10}
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(1, perms_list)
            self.assertEqual(result, -1)
    def test_check_permission_valid(self):
        """권한이 정상적으로 반환되는 경우"""
        with patch('main.cursor', self.mock_cursor):
            # permission=1, perms_list[1]=100
            self.mock_cursor.fetchone.return_value = {'permission': 1}
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(1, perms_list)
            self.assertEqual(result, 100)

    def test_check_permission_invalid_uid(self):
        """DB에 해당 uid가 없을 때 (fetchone None)"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.return_value = None
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(999, perms_list)
            self.assertEqual(result, -1)

    def test_check_permission_db_error(self):
        """DB 오류 발생 시 -1 반환"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.side_effect = Exception('DB error')
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(1, perms_list)
            self.assertEqual(result, -1)

    def test_check_permission_permission_index_error(self):
        """permission 값이 perms_list 범위를 벗어날 때 IndexError로 -1 반환"""
        with patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.return_value = {'permission': 10}
            from main import check_permission
            perms_list = [0, 100, 200]
            result = check_permission(1, perms_list)
            self.assertEqual(result, -1)


class TestConnectRoute(TestFlaskApp):
    def test_connect_get_root_not_exist(self):
        """GET: root user가 없을 때"""
        with patch('main.user_search', return_value=-2):
            response = self.client.get('/connect')
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Root user does not Exist', response.data)

    def test_connect_get_auth_success(self):
        """GET: root user 존재, 인증 성공"""
        with patch('main.user_search', return_value=1), \
             patch('main.auth_user', return_value=0), \
             patch('main.gen_auth_code', return_value='123456'):
            with self.client as c:
                c.set_cookie('session_token', 'test_token')
                response = c.get('/connect')
                self.assertEqual(response.status_code, 200)
                # self.assertIn(b'login.html', response.data)  # 템플릿 이름이 포함되는지 확인

    def test_connect_get_auth_fail(self):
        """GET: root user 존재, 인증 실패"""
        with patch('main.user_search', return_value=1), \
             patch('main.auth_user', return_value=-2):
            with self.client as c:
                c.set_cookie('session_token', 'test_token')
                response = c.get('/connect')
                self.assertEqual(response.status_code, 403)
                self.assertIn(b'Forbidden', response.data)

    def test_connect_post_success(self):
        """POST: 인증코드 일치 시 세션 발급"""
        with patch('main.auth_code', '123456'), \
             patch('main.gen_session', return_value='session_token'):
            response = self.client.post('/connect', json={'uid': 1, 'auth_code': '123456'})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'session_token', response.data)

    def test_connect_post_fail(self):
        """POST: 인증코드 불일치 시"""
        with patch('main.auth_code', '123456'):
            response = self.client.post('/connect', json={'uid': 1, 'auth_code': 'wrong'})
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Invalid code', response.data)

class TestServiceRoutes(TestFlaskApp):
    
    def test_service_connect_authorized_ip(self):
        """서비스 연결 인증된 IP 테스트"""
        with patch('main.get_services_address', return_value={'1': '127.0.0.1'}), \
             patch('main.gen_session', return_value='service_token'):
            
            response = self.client.get(
                '/service_connect',
                environ_overrides={'REMOTE_ADDR': '127.0.0.1'}
            )
            self.assertEqual(response.status_code, 200)
    
    def test_service_connect_unauthorized_ip(self):
        """서비스 연결 비인증 IP 테스트"""
        with patch('main.get_services_address', return_value={'1': '192.168.1.1'}):
            response = self.client.get('/service_connect')
            self.assertEqual(response.status_code, 403)

class TestUserManagement(TestFlaskApp):
    
    def test_register_root_user_get(self):
        """Root 사용자 등록 GET 테스트"""
        with patch('main.user_search', return_value=-2):
            response = self.client.get('/register')
            self.assertEqual(response.status_code, 200)
    
    def test_register_root_user_post_success(self):
        """Root 사용자 등록 POST 성공 테스트"""
        with patch('main.user_search', return_value=-2), \
             patch('main.gen_id', return_value=0):
            
            with patch.object(self.app.extensions['bcrypt'], 'generate_password_hash', return_value='hashed_pw'):
                response = self.client.post('/register', data={
                    'password': 'test123',
                    'confirm_password': 'test123'
                })
                self.assertEqual(response.status_code, 200)
    
    def test_register_root_user_password_mismatch(self):
        """Root 사용자 등록 비밀번호 불일치 테스트"""
        with patch('main.user_search', return_value=-2), \
             patch('main.gen_id', return_value=0):
            
            response = self.client.post('/register', data={
                'password': 'test123',
                'confirm_password': 'different'
            })
            self.assertEqual(response.status_code, 400)
    
    def test_users_get_success(self):
        """사용자 목록 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1):
            self.mock_cursor.fetchall.return_value = [{'uid': 1}, {'uid': 2}]
            
            response = self.client.get('/users', headers={'Content-Type': 'application/json', 'Session-Token': access_token})
            self.assertEqual(response.status_code, 200)
    
    def test_users_get_no_session(self):
        """사용자 목록 조회 세션 없음 테스트"""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 403)

class TestLocationMiddlewares(TestFlaskApp):
    def setUp(self):
        super().setUp()
        self.mock_cursor = MagicMock()
        self.mock_session_uid = 2
    
    def test_location_logs_get_success(self):
        """위치 로그 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.check_permission', return_value=2):
            
            self.mock_cursor.fetchall.return_value = [
                {'id': 1, 'uid': 1, 'coordinate': 'POINT(37.5 127.0)', 'time': '2025-01-01 12:00:00'}
            ]
            
            response = self.client.get('/location/logs', 
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                     json={'uid': 1, 'search_time': '2025-01-01 00:00:00'})
            self.assertEqual(response.status_code, 200)

    def test_location_logs_get_not_found(self):
        """위치 로그 없음 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            
            self.mock_cursor.fetchall.return_value = []
            
            response = self.client.get('/location/logs', 
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                     json={'uid': 1, 'search_time': '2025-01-01 00:00:00'})
            self.assertEqual(response.status_code, 404)
    
    def test_location_logs_post_success(self):
        """위치 로그 추가 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.check_permission', return_value=1), \
             patch('main.gen_id', return_value=1):
            
            self.mock_cursor.execute.return_value = 1
            
            response = self.client.post('/location/logs',
                                      headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                      json={
                                          'coordinate': 'POINT(37.5 127.0)',
                                          'time': '2025-01-01 12:00:00'
                                      })
            self.assertEqual(response.status_code, 200)
    
    def test_location_latest_success(self):
        """최신 위치 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1):
            self.mock_cursor.fetchone.return_value = {
                'id': 1, 'uid': 1, 'coordinate': 'POINT(37.5 127.0)', 'time': '2025-01-01 12:00:00'
            }
            
            response = self.client.get('/location/latest',
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                     json={'uid': 1})
            self.assertEqual(response.status_code, 200)
            
    def test_point_delete_success(self):
        """즐겨찾기 포인트 DELETE 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            # 정상적으로 삭제
            self.mock_cursor.execute.return_value = 1
            response = self.client.delete(
                '/location/fav/point',
                headers={'Session-Token': 'test_token'},
                json={'point_id': 1, 'uid': self.mock_session_uid}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Success', response.data)

    def test_point_delete_permission_denied(self):
        """즐겨찾기 포인트 DELETE 권한 거부 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=0):
            response = self.client.delete(
                '/location/fav/point',
                headers={'Session-Token': 'test_token'},
                json={'point_id': 1, 'uid': 9999}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Permission Denied', response.data)

    def test_point_delete_database_error(self):
        """즐겨찾기 포인트 DELETE DB 오류 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.execute.side_effect = Exception("DB error")
            response = self.client.delete(
                '/location/fav/point',
                headers={'Session-Token': 'test_token'},
                json={'point_id': 1, 'uid': self.mock_session_uid}
            )
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'DELETE unsuccessful', response.data)

class TestFavoriteLocationRoutes(TestFlaskApp):
    
    def test_fav_point_get_success(self):
        """즐겨찾기 장소 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.check_permission', return_value=2):
            
            self.mock_cursor.fetchall.return_value = [
                {'id': 1, 'uid': 1, 'alias': 'Home', 'coordinate': 'POINT(37.5 127.0)', 'status': 1}
            ]
            
            response = self.client.get('/location/fav/point',
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                     json={'uid': 1})
            self.assertEqual(response.status_code, 200)
    
    def test_fav_point_post_success(self):
        """즐겨찾기 장소 추가 성공 테스트"""
        with patch('main.auth_user', return_value=10001), \
             patch('main.check_permission', return_value=1), \
             patch('main.gen_id', return_value=1):
            
            self.mock_cursor.execute.return_value = 1
            
            response = self.client.post('/location/fav/point',
                                      headers={'Session-Token': 'service_token'},
                                      json={
                                          'uid': 1,
                                          'coordinate': 'POINT(37.5 127.0)',
                                          'alias': 'Home',
                                          'status': 1
                                      })
            self.assertEqual(response.status_code, 200)

class TestEventLogs(TestFlaskApp):
    def setUp(self):
        super().setUp()
        self.mock_cursor = MagicMock()
        self.mock_session_uid = 1

    def test_eventlogs_get_success(self):
        """eventlogs GET 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchall.return_value = [{'id': 1, 'location_id': 10, 'about': 'test'}]
            response = self.client.get(
                '/event/eventlogs',
                headers={'Session-Token': 'test_token'},
                json={'location_id': 10}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'location_id', response.data)

    def test_eventlogs_post_success(self):
        """eventlogs POST 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.gen_id', return_value=1), \
             patch('main.cursor', self.mock_cursor):
            # location_id -> uid 매핑
            self.mock_cursor.fetchone.side_effect = [
                {'uid': self.mock_session_uid}  # 첫 번째 fetchone: uid 반환
            ]
            self.mock_cursor.execute.return_value = 1
            response = self.client.post(
                '/event/eventlogs',
                headers={'Session-Token': 'test_token'},
                json={'time': '2024-01-01 00:00:00', 'location_id': 10, 'about': 'test'}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Success', response.data)

    def test_eventlogs_delete_success(self):
        """eventlogs DELETE 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            # event_id -> location_id -> uid 매핑
            self.mock_cursor.fetchone.side_effect = [
                {'location_id': 10},  # 첫 번째 fetchone: location_id 반환
                {'uid': self.mock_session_uid}  # 두 번째 fetchone: uid 반환
            ]
            self.mock_cursor.execute.return_value = 1
            response = self.client.delete(
                '/event/eventlogs',
                headers={'Session-Token': 'test_token'},
                json={'event_id': 1}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Success', response.data)

class TestVisitTimeMiddleware(TestFlaskApp):
    def setUp(self):
        super().setUp()
        self.mock_cursor = MagicMock()
        self.mock_session_uid = 2

    def test_visits_success(self):
        """방문 횟수 조회 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.return_value = {'visit_times': 5}
            response = self.client.get(
                '/event/visits',
                headers={'Session-Token': 'test_token'},
                json={'location_id': 10, 'lookup_days': 7}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'visit_times', response.data)

    def test_visits_permission_denied(self):
        """방문 횟수 조회 권한 거부 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=0):
            response = self.client.get(
                '/event/visits',
                headers={'Session-Token': 'test_token'},
                json={'location_id': 10, 'lookup_days': 7}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Permission Denied', response.data)

    def test_visits_invalid_session(self):
        """방문 횟수 조회 세션 오류 테스트"""
        with patch('main.auth_user', return_value=-2):
            response = self.client.get(
                '/event/visits',
                headers={'Session-Token': 'invalid_token'},
                json={'location_id': 10, 'lookup_days': 7}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Invalid Session', response.data)

    def test_visits_database_error(self):
        """방문 횟수 조회 DB 오류 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
                self.mock_cursor.fetchone.side_effect = Exception("DB error")
                response = self.client.get(
                    '/event/visits',
                    headers={'Session-Token': 'test_token'},
                    json={'location_id': 10, 'lookup_days': 7}
                )
                self.assertEqual(response.status_code, 500)
                self.assertIn(b'Internal Server Error', response.data)

class TestMQTTRoutes(TestFlaskApp):
    
    def test_mqtt_getstats_success(self):
        """MQTT 통계 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('mqtt_module.get_stats_from_clients', return_value={'connected': 5}):
            
            response = self.client.get('/protocol/mqtt/getstats',
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token})
            self.assertEqual(response.status_code, 200)
    
    def test_mqtt_command_success(self):
        """MQTT 명령 전송 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('mqtt_module.operate', return_value=0) as mock_operate:
            
            response = self.client.post('/protocol/mqtt/command',
                                      headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                      json={
                                          'topic': 'broadcast',
                                          'device_id': 'device1',
                                          'command': 'turn_on'
                                      })
            self.assertEqual(response.status_code, 200)
            mock_operate.assert_called_once()
    
    def test_command_internal_server_error(self):
        """MQTT 명령 처리 중 예외 발생 시 500 반환 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.mqtt_module.operate', side_effect=Exception("MQTT Error")):
            response = self.client.post(
                '/protocol/mqtt/command',
                headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                json={
                    'topic': 'test/topic',
                    'device_id': 'device123',
                    'command': 'on'
                }
            )
            self.assertEqual(response.status_code, 500)    

class TestNotificationRoutes(TestFlaskApp):
    
    def test_getnoti_success(self):
        """알림 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1):
            self.mock_cursor.fetchall.return_value = [
                {'id': 1, 'uid': 1, 'content': 'Test notification', 'time': '2025-01-01 12:00:00'}
            ]
            
            response = self.client.get('/notification/getnoti',
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token, 'id': '1'})
            self.assertEqual(response.status_code, 200)
    
    def test_postnoti_success(self):
        """알림 생성 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.check_permission', return_value=2):
            
            self.mock_cursor.fetchone.return_value = {'highest_id': 0}
            self.mock_cursor.execute.return_value = 1
            
            response = self.client.post('/notification/postnoti',
                                      headers={'Content-Type': 'application/json', 'Session-Token': access_token},
                                      json={
                                          'uid': 1,
                                          'content': 'Test notification',
                                          'time': '2025-01-01 12:00:00',
                                          'about': 'test'
                                      })
            self.assertEqual(response.status_code, 200)
    
    def test_notification_sync_get_success(self):
        """알림 동기화 조회 성공 테스트"""
        with patch('main.auth_user', return_value=1):
            self.mock_cursor.fetchall.return_value = [{'id': 1}, {'id': 2}]
            
            response = self.client.get('/notification/sync',
                                     headers={'Content-Type': 'application/json', 'Session-Token': access_token})
            self.assertEqual(response.status_code, 200)

    def test_notification_sync_update_success(self):
        """알림 동기화 상태 업데이트 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.cursor') as mock_cursor, \
             patch('main.check_permission', return_value=2):
            # notification_id -> uid 매핑
            mock_cursor.fetchone.return_value = {'uid': 1}
            mock_cursor.execute.return_value = 1
            response = self.client.post('/notification/sync',
                                        headers={'Session-Token': 'test_token'},
                                        json={'notification_id': 1})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'OK', response.data)

class TestUtilityFunctions(TestFlaskApp):
    
    def test_gen_id_success(self):
        """ID 생성 성공 테스트"""
        with patch('main.cursor') as mock_cursor:
            mock_cursor.fetchone.return_value = {'highest_id': 5}
            
            from main import gen_id
            result = gen_id('users', 'uid')
            self.assertEqual(result, 6)
    
    def test_gen_id_first_record(self):
        """첫 번째 레코드 ID 생성 테스트"""
        with patch('main.cursor') as mock_cursor:
            mock_cursor.fetchone.return_value = {'highest_id': None}
            
            from main import gen_id
            result = gen_id('users', 'uid')
            self.assertEqual(result, 0)
    
    def test_gen_auth_code(self):
        """인증 코드 생성 테스트"""
        from main import gen_auth_code
        
        code = gen_auth_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

class TestSessionManagement(TestFlaskApp):
    
    def test_renew_session_success(self):
        """세션 갱신 성공 테스트"""
        with patch('main.auth_user', return_value=1), \
             patch('main.gen_session', return_value='new_token'):
            
            response = self.client.get('/renew_session',
                                     headers={'Session-Token': 'old_token'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode(), 'new_token')
    
    def test_renew_session_invalid_token(self):
        """세션 갱신 잘못된 토큰 테스트"""
        with patch('main.auth_user', return_value=-2):
            response = self.client.get('/renew_session',
                                     headers={'Session-Token': 'invalid_token'})
            self.assertEqual(response.status_code, 403)
    
    def test_renew_session_missing_token(self):
        """세션 갱신 토큰 누락 테스트"""
        response = self.client.get('/renew_session')
        self.assertEqual(response.status_code, 400)

class TestAuthenticationEdgeCases(TestFlaskApp):
    def test_root_auth_database_error(self):
        """Root 인증 시 데이터베이스 오류 테스트"""
        with patch('main.user_search', return_value=1), \
             patch('main.cursor', self.mock_cursor):
            # Simulate database error
            self.mock_cursor.fetchone.side_effect = Exception("Database connection failed")
            
            response = self.client.post('/root_auth', data={'password': 'test_password'})
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Internel server error', response.data)

    def test_root_auth_missing_password_field(self):
        """Root 인증 시 비밀번호 필드 누락 테스트"""
        with patch('main.user_search', return_value=1):
            response = self.client.post('/root_auth', data={})
            self.assertEqual(response.status_code, 400)
            self.assertIn(b'Request Error', response.data)

    def test_root_auth_session_generation_failure(self):
        """Root 인증 시 세션 생성 실패 테스트"""
        with patch('main.user_search', return_value=1), \
             patch('main.gen_session', return_value=-1), \
             patch('main.cursor', self.mock_cursor):
            test_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.PJ/...'
            self.mock_cursor.fetchone.return_value = {'password': test_hash}
            
            with patch('main.bcrypt.check_password_hash', return_value=True):
                response = self.client.post('/root_auth', data={'password': 'test_password'})
                self.assertEqual(response.status_code, 500)
                self.assertIn(b'Session generation failed', response.data)

    def test_auth_user_database_error(self):
        """사용자 인증 시 데이터베이스 오류 테스트"""
        with patch('main.delete_expired_session', return_value=0), \
             patch('main.cursor') as mock_cursor:
            mock_cursor.execute.side_effect = Exception("Database error")
            
            from main import auth_user
            result = auth_user('test_token')
            self.assertEqual(result, -1)

class TestErrorHandling(TestFlaskApp):
    def test_database_connection_errors(self):
        """데이터베이스 연결 오류 시나리오"""
        with patch('main.cursor') as mock_cursor:
            mock_cursor.execute.side_effect = Exception("Database connection lost")
            
            from main import user_search
            result = user_search(1)
            self.assertEqual(result, -1)

    def test_root_auth_database_fetch_error(self):
        """Root 인증 시 데이터베이스 조회 실패"""
        with patch('main.user_search', return_value=1), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.side_effect = Exception("Query failed")
            
            response = self.client.post('/root_auth', data={'password': 'test'})
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Internel server error', response.data)

    def test_gen_session_database_error(self):
        """세션 생성 시 데이터베이스 오류"""
        with patch('main.cursor') as mock_cursor:
            mock_cursor.execute.side_effect = Exception("Insert failed")
            
            from main import gen_session
            result = gen_session(1, 1)
            self.assertEqual(result, -1)

class TestDatabaseFunctions(TestFlaskApp):
    def test_delete_expired_session_success(self):
        """만료된 세션 삭제 성공 테스트"""
        with patch('main.cursor') as mock_cursor:
            mock_cursor.execute.return_value = None
            
            from main import delete_expired_session
            result = delete_expired_session()
            
            self.assertEqual(result, 0)
            mock_cursor.execute.assert_called_once_with("DELETE FROM clients WHERE expire_time < GETDATE()")

    def test_delete_expired_session_database_error(self):
        """만료된 세션 삭제 데이터베이스 오류 테스트"""
        with patch('main.cursor') as mock_cursor:
            mock_cursor.execute.side_effect = Exception("Database connection failed")
            
            from main import delete_expired_session
            result = delete_expired_session()
            
            self.assertEqual(result, -1)

    def test_register_user_success(self):
        """사용자 등록 성공 테스트"""
        with patch('main.gen_id', return_value=5), \
             patch('main.cursor') as mock_cursor:
            mock_cursor.execute.return_value = None
            
            from main import register_user
            result = register_user(5, 1)
            
            self.assertEqual(result, 5)
            mock_cursor.execute.assert_called_once()

    def test_register_user_gen_id_failure(self):
        """사용자 등록 시 ID 생성 실패 테스트"""
        with patch('main.gen_id', return_value=-1):
            from main import register_user
            result = register_user(5, 1)
            
            self.assertEqual(result, -1)

    def test_register_user_database_error(self):
        """사용자 등록 데이터베이스 오류 테스트"""
        with patch('main.gen_id', return_value=5), \
             patch('main.cursor') as mock_cursor:
            mock_cursor.execute.side_effect = Exception("Insert failed")
            
            from main import register_user
            result = register_user(5, 1)
            
            self.assertEqual(result, -1)

class TestRouteRoutes(TestFlaskApp):
    def setUp(self):
        super().setUp()
        self.mock_cursor = MagicMock()
        self.mock_session_uid = 1

    def test_route_get_success(self):
        """즐겨찾기 경로 GET 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            # startlocation_id -> uid 매핑
            self.mock_cursor.fetchone.side_effect = [
                {'uid': self.mock_session_uid}  # 첫 번째 fetchone: uid 반환
            ]
            self.mock_cursor.fetchall.return_value = [
                {'id': 1, 'startlocation_id': 10, 'endlocation_id': 20, 'route': 'LINESTRING(0 0,1 1)', 'status': 1}
            ]
            response = self.client.get(
                '/location/fav/route',
                headers={'Session-Token': 'test_token'},
                json={'startlocation_id': 10}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'startlocation_id', response.data)

    def test_route_post_success(self):
        """즐겨찾기 경로 POST 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.gen_id', return_value=1), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.execute.return_value = 1
            response = self.client.post(
                '/location/fav/route',
                headers={'Session-Token': 'test_token'},
                json={
                    'route': 'LINESTRING(0 0,1 1)',
                    'startlocation_id': 10,
                    'endlocation_id': 20,
                    'status': 1
                }
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Success', response.data)

    def test_route_delete_success(self):
        """즐겨찾기 경로 DELETE 성공 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=2), \
             patch('main.cursor', self.mock_cursor):
            # route_id -> startlocation_id -> uid 매핑
            self.mock_cursor.fetchone.side_effect = [
                {'startlocation_id': 10},  # 첫 번째 fetchone: startlocation_id 반환
                {'uid': self.mock_session_uid}  # 두 번째 fetchone: uid 반환
            ]
            self.mock_cursor.execute.return_value = 1
            response = self.client.delete(
                '/location/fav/route',
                headers={'Session-Token': 'test_token'},
                json={'route_id': 1}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Success', response.data)

    def test_route_get_permission_denied(self):
        """즐겨찾기 경로 GET 권한 거부 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=0), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.side_effect = [
                {'uid': 9999}
            ]
            response = self.client.get(
                '/location/fav/route',
                headers={'Session-Token': 'test_token'},
                json={'startlocation_id': 10}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Permission Denied', response.data)

    def test_route_post_permission_denied(self):
        """즐겨찾기 경로 POST 권한 거부 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=0):
            response = self.client.post(
                '/location/fav/route',
                headers={'Session-Token': 'test_token'},
                json={
                    'route': 'LINESTRING(0 0,1 1)',
                    'startlocation_id': 10,
                    'endlocation_id': 20,
                    'status': 1
                }
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Permission Denied', response.data)

    def test_route_delete_permission_denied(self):
        """즐겨찾기 경로 DELETE 권한 거부 테스트"""
        with patch('main.auth_user', return_value=self.mock_session_uid), \
             patch('main.check_permission', return_value=0), \
             patch('main.cursor', self.mock_cursor):
            self.mock_cursor.fetchone.side_effect = [
                {'startlocation_id': 10},
                {'uid': 9999}
            ]
            response = self.client.delete(
                '/location/fav/route',
                headers={'Session-Token': 'test_token'},
                json={'route_id': 1}
            )
            self.assertEqual(response.status_code, 403)
            self.assertIn(b'Permission Denied', response.data)


if __name__ == '__main__':
    # 테스트 실행 설정
    unittest.main(verbosity=2)
