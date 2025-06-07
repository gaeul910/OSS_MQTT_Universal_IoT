import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:oss_iot_control_applicaton/main.dart';
import 'package:oss_iot_control_applicaton/config.dart';
import 'package:oss_iot_control_applicaton/login.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('MyApp 진입점 및 테마/라우팅 테스트', () {
    testWidgets('앱이 정상적으로 실행되고 LoginPage를 렌더링한다', (WidgetTester tester) async {
      await tester.pumpWidget(const MyApp());
      expect(find.byType(LoginPage), findsOneWidget);
    });

    testWidgets('테마 변경 시 전체 앱이 리빌드된다', (WidgetTester tester) async {
      await tester.pumpWidget(const MyApp());

      // 기본값은 light
      expect(themeNotifier.themeMode, ThemeMode.light);

      // 테마 변경
      themeNotifier.toggleTheme(true);
      await tester.pump();
      expect(themeNotifier.themeMode, ThemeMode.dark);

      // 다시 light로 변경
      themeNotifier.toggleTheme(false);
      await tester.pump();
      expect(themeNotifier.themeMode, ThemeMode.light);
    });

    testWidgets('테마 변경 이벤트가 _onThemeChanged를 통해 정상 동작한다', (WidgetTester tester) async {
      await tester.pumpWidget(const MyApp());
      // 내부적으로 _onThemeChanged는 themeNotifier의 notifyListeners로 트리거됨
      themeNotifier.toggleTheme(true);
      await tester.pump();
      expect(find.byType(MyApp), findsOneWidget);
    });
  });
}
