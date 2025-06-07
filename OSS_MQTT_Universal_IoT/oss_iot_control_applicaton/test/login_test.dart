import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:oss_iot_control_applicaton/login.dart';
import 'package:oss_iot_control_applicaton/lobby.dart';
import 'package:oss_iot_control_applicaton/session.dart';
import 'package:oss_iot_control_applicaton/notifications.dart';
import 'package:oss_iot_control_applicaton/gps.dart';
import 'package:mockito/mockito.dart';
import 'package:http/http.dart' as http;

// Mock 클래스
class MockHttpClient extends Mock implements http.Client {}
class MockSessionManager extends Mock implements SessionManager {}
class MockNotificationService extends Mock implements NotificationService {}
class MockGpsTracker extends Mock implements GpsTracker {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('LoginPage UI 및 입력 분기', () {
    testWidgets('입력값 검증: 주소/포트/uid 미입력, uid 타입 오류', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: LoginPage()));

      // 포트, uid, 코드 모두 비워둔 채 로그인
      await tester.tap(find.text('로그인'));
      await tester.pump();
      expect(find.text('주소를 입력해주세요.'), findsOneWidget);

      // 주소만 입력, 포트 미입력
      await tester.enterText(find.byType(TextField).at(0), '127.0.0.1');
      await tester.tap(find.text('로그인'));
      await tester.pump();
      expect(find.text('포트 번호를 입력해주세요.'), findsOneWidget);

      // 주소, 포트 입력, uid 미입력
      await tester.enterText(find.byType(TextField).at(1), '8080');
      await tester.tap(find.text('로그인'));
      await tester.pump();
      expect(find.text('uid를 입력해주세요.'), findsOneWidget);

      // uid 타입 오류
      await tester.enterText(find.byType(TextField).at(2), 'abc');
      await tester.tap(find.text('로그인'));
      await tester.pump();
      expect(find.text('uid는 숫자만 입력해야 합니다.'), findsOneWidget);
    });

    testWidgets('서버 응답: 로그인 성공 시 Lobby로 라우팅', (WidgetTester tester) async {
      // http.post mocking은 실제 구조에 따라 DI 필요
      await tester.pumpWidget(MaterialApp(home: LoginPage()));

      // 정상 입력
      await tester.enterText(find.byType(TextField).at(0), '127.0.0.1');
      await tester.enterText(find.byType(TextField).at(1), '8080');
      await tester.enterText(find.byType(TextField).at(2), '123');
      // Pinput 입력
      // 실제로는 Pinput 위젯에 대한 입력 시뮬레이션 필요 (구현에 따라 다름)

      // 로그인 버튼 클릭
      await tester.tap(find.text('로그인'));
      await tester.pumpAndSettle();

      // LobbyScreen으로 이동했는지 확인
      // (실제 http.post와 세션, 알림, GPS 등은 mock으로 DI 필요)
      // expect(find.byType(LobbyScreen), findsOneWidget);
    });

    testWidgets('서버 응답: 로그인 실패/예외 처리', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: LoginPage()));

      await tester.enterText(find.byType(TextField).at(0), '127.0.0.1');
      await tester.enterText(find.byType(TextField).at(1), '8080');
      await tester.enterText(find.byType(TextField).at(2), '123');
      // Pinput 입력 생략

      // 로그인 버튼 클릭 (실패 상황 가정)
      await tester.tap(find.text('로그인'));
      await tester.pump();

      // 실패 메시지 출력 확인 (실제 서버 응답 mocking 필요)
      // expect(find.textContaining('로그인 실패'), findsOneWidget);
    });
  });
}
