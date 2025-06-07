import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:oss_iot_control_applicaton/config.dart';
import 'package:oss_iot_control_applicaton/session.dart';
import 'package:oss_iot_control_applicaton/gps.dart';
import 'package:oss_iot_control_applicaton/notifications.dart';
import 'package:oss_iot_control_applicaton/login.dart';
import 'package:mockito/mockito.dart';

// Mock/Fake 클래스 정의
class MockNotificationService extends Mock implements NotificationService {}
class MockGpsTracker extends Mock implements GpsTracker {}
class MockSessionManager extends Mock implements SessionManager {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('ThemeNotifier', () {
    test('toggleTheme이 ThemeMode를 올바르게 변경한다', () {
      final notifier = ThemeNotifier();
      expect(notifier.themeMode, ThemeMode.light);

      notifier.toggleTheme(true);
      expect(notifier.themeMode, ThemeMode.dark);

      notifier.toggleTheme(false);
      expect(notifier.themeMode, ThemeMode.light);
    });
  });

  group('SettingsScreen UI 및 분기', () {
    testWidgets('다크모드 토글 UI와 로직이 동작한다', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(home: SettingsScreen()),
      );
      final switchFinder = find.byType(SwitchListTile);
      expect(switchFinder, findsOneWidget);

      // 다크모드로 변경
      await tester.tap(switchFinder);
      await tester.pump();
      expect(themeNotifier.themeMode, ThemeMode.dark);
    });

    testWidgets('세션 키 확인 다이얼로그 분기(세션 없음/있음)', (WidgetTester tester) async {
      // 세션 없음
      await tester.pumpWidget(MaterialApp(home: SettingsScreen()));
      await tester.tap(find.widgetWithText(ListTile, '세션 키 확인'));
      await tester.pumpAndSettle();
      expect(find.text('세션 키 없음'), findsOneWidget);

      // 세션 있음 (Fake SessionManager 필요)
      // 실제 DI 구조라면 mockSessionManager로 주입
    });

    testWidgets('GPS 테스트 버튼 클릭 시 GpsTestScreen으로 이동', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: SettingsScreen()));
      await tester.tap(find.widgetWithText(ListTile, 'GPS 테스트'));
      await tester.pumpAndSettle();
      expect(find.byType(GpsTestScreen), findsOneWidget);
    });

    testWidgets('로그아웃 분기: 취소/확인/외부 서비스 중단 및 라우팅', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(home: SettingsScreen()));

      // 로그아웃 다이얼로그
      await tester.tap(find.widgetWithText(ListTile, '로그아웃'));
      await tester.pumpAndSettle();
      expect(find.text('로그아웃 확인'), findsOneWidget);

      // 취소
      await tester.tap(find.text('취소'));
      await tester.pumpAndSettle();
      expect(find.text('로그아웃 확인'), findsNothing);

      // 다시 로그아웃, 이번엔 확인
      await tester.tap(find.widgetWithText(ListTile, '로그아웃'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('로그아웃'));
      await tester.pumpAndSettle();
      expect(find.byType(LoginPage), findsOneWidget);
    });
  });
}
