import 'package:flutter/material.dart';
import 'login.dart'; // 로그인 화면 import
import 'notifications.dart';
import 'gps.dart';
import 'session.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  @override
  Widget build(BuildContext context) {
    final bool isDarkMode = themeNotifier.themeMode == ThemeMode.dark;

    return Scaffold(
      appBar: AppBar(title: const Text('설정')),
      body: ListView(
        children: [
          // 1. 다크모드 토글
          SwitchListTile(
            secondary: const Icon(Icons.dark_mode),
            title: const Text('다크모드'),
            value: isDarkMode,
            onChanged: (value) {
              setState(() {
                themeNotifier.toggleTheme(value);
              });
            },
          ),

          // 2. 세션 키 확인 기능
          ListTile(
            leading: const Icon(Icons.vpn_key),
            title: const Text('세션 키 확인'),
            onTap: () {
              final sessionKey = SessionManager().sessionToken ?? '세션 키 없음';
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('현재 세션 키'),
                  content: SelectableText(sessionKey),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('닫기'),
                    ),
                  ],
                ),
              );
            },
          ),

          // gps 테스트
          ListTile(
            leading: const Icon(Icons.gps_fixed),
            title: const Text('GPS 테스트'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const GpsTestScreen()),
              );
            },
          ),
          // 3. 로그아웃 항목
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('로그아웃'),
            onTap: () async {
              final bool? shouldLogout = await showDialog<bool>(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    title: const Text('로그아웃 확인'),
                    content: const Text('정말 로그아웃하시겠습니까?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        child: const Text('취소'),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        child: const Text('로그아웃'),
                      ),
                    ],
                  );
                },
              );
              if (shouldLogout == true) {
                NotificationService().stopPolling();
                GpsTracker().stopTracking();
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginPage()),
                      (route) => false,
                );
              }
            },
          ),
        ],
      ),
    );
  }
}

class ThemeNotifier extends ChangeNotifier {
  ThemeMode _themeMode = ThemeMode.light;
  ThemeMode get themeMode => _themeMode;

  void toggleTheme(bool isDark) {
    _themeMode = isDark ? ThemeMode.dark : ThemeMode.light;
    notifyListeners();
  }
}
final ThemeNotifier themeNotifier = ThemeNotifier();