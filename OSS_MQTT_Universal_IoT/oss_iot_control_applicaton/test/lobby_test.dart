import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:oss_iot_control_applicaton/lobby.dart';
import 'package:oss_iot_control_applicaton/config.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('LobbyScreen UI & Drawer', () {
    testWidgets('로비 화면이 정상적으로 렌더링된다', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(home: LobbyScreen()),
      );
      expect(find.text('Lobby'), findsOneWidget);
      expect(find.byIcon(Icons.menu), findsOneWidget);
    });

    testWidgets('햄버거 메뉴 클릭 시 Drawer가 열린다', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(home: LobbyScreen()),
      );
      await tester.tap(find.byIcon(Icons.menu));
      await tester.pumpAndSettle();
      expect(find.text('Options'), findsOneWidget);
      expect(find.text('Settings'), findsOneWidget);
      expect(find.text('About'), findsOneWidget);
    });

    testWidgets('Drawer에서 Settings 클릭 시 SettingsScreen으로 이동', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(home: LobbyScreen()),
      );
      await tester.tap(find.byIcon(Icons.menu));
      await tester.pumpAndSettle();

      await tester.tap(find.widgetWithText(ListTile, 'Settings'));
      await tester.pumpAndSettle();

      // SettingsScreen이 정상적으로 표시되는지 확인
      expect(find.byType(SettingsScreen), findsOneWidget);
    });

    testWidgets('Drawer에서 Home, About 클릭 시 Drawer만 닫힘', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(home: LobbyScreen()),
      );
      await tester.tap(find.byIcon(Icons.menu));
      await tester.pumpAndSettle();

      await tester.tap(find.widgetWithText(ListTile, 'Home'));
      await tester.pumpAndSettle();
      expect(find.text('Options'), findsNothing);

      await tester.tap(find.byIcon(Icons.menu));
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(ListTile, 'About'));
      await tester.pumpAndSettle();
      expect(find.text('Options'), findsNothing);
    });
  });
}
