import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:http/http.dart' as http;
import 'package:oss_iot_control_applicaton/notifications.dart';
import 'package:oss_iot_control_applicaton/session.dart';
import 'notifications_test.mocks.dart';


@GenerateMocks([
  FlutterLocalNotificationsPlugin,
  SessionManager,
  http.Client,
  AndroidFlutterLocalNotificationsPlugin,
  IOSFlutterLocalNotificationsPlugin,
])
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() {
    registerFallbackValue(Uri.parse('http://dummy'));
  });

  late NotificationService service;
  late MockFlutterLocalNotificationsPlugin mockNotificationsPlugin;
  late MockSessionManager mockSessionManager;
  late MockClient mockHttpClient;

  const testSettings = InitializationSettings(
    android: AndroidInitializationSettings('@mipmap/ic_launcher'),
    iOS: DarwinInitializationSettings(),
  );

  setUp(() {
    mockNotificationsPlugin = MockFlutterLocalNotificationsPlugin();
    mockSessionManager = MockSessionManager();
    mockHttpClient = MockClient();

    service = NotificationService(
      plugin: mockNotificationsPlugin,
      httpClient: mockHttpClient,
    )..notificationsPlugin = mockNotificationsPlugin;

    when(mockSessionManager.sessionToken).thenReturn('valid_token');
  });

  tearDown(() {
    service.stopPolling();
  });

  group('Public 메서드 테스트', () {
    test('[configure] 서버 정보 저장 및 기본 상태 확인', () {
      service.configure(ip: '127.0.0.1', port: '8080', uid: 'user123');
      expect(service.isPolling, isFalse);
      expect(service.pollingIsolate, isNull);
    });

    test('[initialize] 플러그인 초기화 성공', () async {
      when(mockNotificationsPlugin.initialize(any)).thenAnswer((_) async => true);

      await service.initialize();

      verify(mockNotificationsPlugin.initialize(testSettings)).called(1);
    });

    test('[requestNotificationPermission] 플랫폼별 권한 요청', () async {
      final androidPlugin = MockAndroidFlutterLocalNotificationsPlugin();
      final iosPlugin = MockIOSFlutterLocalNotificationsPlugin();

      when(mockNotificationsPlugin.resolvePlatformSpecificImplementation<
          AndroidFlutterLocalNotificationsPlugin>()).thenReturn(androidPlugin);
      when(mockNotificationsPlugin.resolvePlatformSpecificImplementation<
          IOSFlutterLocalNotificationsPlugin>()).thenReturn(iosPlugin);

      await service.requestNotificationPermission();

      verify(androidPlugin.requestNotificationsPermission()).called(1);
      verify(iosPlugin.requestPermissions(alert: true, badge: true, sound: true)).called(1);
    });

    test('[startPolling] 서버 정보 없을 때 폴링 시작 차단', () async {
      service.configure(ip: '', port: '', uid: '');
      await service.startPolling();
      expect(service.isPolling, isFalse);
    });

    test('[stopPolling] 폴링 리소스 정리 확인', () {
      service.configure(ip: '127.0.0.1', port: '8080', uid: 'user123');
      service.startPolling();
      service.stopPolling();

      expect(service.isPolling, isFalse);
      expect(service.pollingIsolate, isNull);
      expect(service.receivePort, isNull);
    });

    test('[showNotification] 기본 알림 표시 성공', () async {
      when(mockNotificationsPlugin.show(any, any, any, any)).thenAnswer((_) async => true);

      await service.showNotification(id: 1, title: 'Test', body: 'Body');

      verify(mockNotificationsPlugin.show(
        1,
        'Test',
        'Body',
        argThat(isA<NotificationDetails>()),
      )).called(1);
    });
  });

  group('분기 커버리지 테스트', () {
    test('_handleNotification: 유효하지 않은 ID 처리', () async {
      service.configure(ip: '127.0.0.1', port: '8080', uid: 'user123');
      when(mockNotificationsPlugin.show(any, any, any, any)).thenAnswer((_) async => true);
      when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
          .thenAnswer((_) async => http.Response('', 200));

      // Isolate 메시지 시뮬레이션
      service.startPolling();
      service.receivePort!.sendPort.send({'id': 'invalid_id', 'content': 'test'});

      await pumpEventQueue();

      verify(mockNotificationsPlugin.show(0, 'IoT 알림', 'test', any)).called(1);
    });

    test('_updateNotificationStatus: 세션 토큰 갱신 필요', () async {
      service.configure(ip: '127.0.0.1', port: '8080', uid: 'user123');
      when(mockHttpClient.post(any, headers: anyNamed('headers'), body: anyNamed('body')))
          .thenAnswer((_) async => http.Response('', 401))
          .thenAnswer((_) async => http.Response('', 200));
      when(mockSessionManager.renewSession()).thenAnswer((_) async => true);

      final result = await service.updateNotificationStatus(1);

      expect(result, isTrue);
      verify(mockSessionManager.renewSession()).called(1);
    });
  });

  group('에러 시나리오 테스트', () {
    test('롱 폴링 중 네트워크 에러 복구', () async {
      service.configure(ip: '127.0.0.1', port: '8080', uid: 'user123');
      when(mockHttpClient.get(any<Uri>(), headers: anyNamed('headers')))
          .thenThrow(Exception('Connection failed'))
          .thenAnswer((_) async => http.Response('[]', 200));

      service.startPolling();
      await Future.delayed(const Duration(seconds: 6));
      await pumpEventQueue();

      verify(mockHttpClient.get(any, headers: anyNamed('headers'))).called(greaterThan(1));
    });
  });
}
