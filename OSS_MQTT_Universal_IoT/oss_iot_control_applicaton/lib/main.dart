import 'package:flutter/material.dart';
import 'login.dart'; // LoginPage가 정의된 파일 import
import 'config.dart';
import 'notifications.dart'; // 알림 서비스 import
import 'package:permission_handler/permission_handler.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Permission.location.request();
  await NotificationService().initialize(); // 알림 플러그인 초기화
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});
  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  void initState() {
    super.initState();
    themeNotifier.addListener(_onThemeChanged);
  }
  @override
  void dispose() {
    themeNotifier.removeListener(_onThemeChanged);
    super.dispose();
  }

  void _onThemeChanged() {
    setState(() {}); // 테마 변경 시 앱 전체 리빌드
  }
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // 디버그 배너 제거 (선택)
      theme: ThemeData.light(),
      darkTheme: ThemeData.dark(),
      themeMode: themeNotifier.themeMode,
      home: LoginPage(), // 앱 시작 시 LoginPage를 첫 화면으로 지정
    );
  }
}