import 'package:flutter/material.dart';
import 'login.dart'; // 로그인 화면 import

/// 설정 화면 전체를 보여주는 위젯 (기존에 만드신 화면이 있다면 그걸 사용하세요)
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('설정')),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('로그아웃'),
            onTap: () async {
              // 로그아웃 확인 다이얼로그 띄우기
              final bool? shouldLogout = await showDialog<bool>(
                context: context,
                builder: (context) {
                  return AlertDialog(
                    title: const Text('로그아웃 확인'),
                    content: const Text('정말 로그아웃하시겠습니까?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.of(context).pop(false), // 취소
                        child: const Text('취소'),
                      ),
                      ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(true), // 확인
                        child: const Text('로그아웃'),
                      ),
                    ],
                  );
                },
              );

              if (shouldLogout == true) {
                // 확인 시 로그인 화면으로 이동 (모든 화면 제거)
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

