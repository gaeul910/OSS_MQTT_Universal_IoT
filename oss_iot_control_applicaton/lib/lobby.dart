import 'package:flutter/material.dart';
import 'config.dart';
class LobbyScreen extends StatefulWidget {
  const LobbyScreen({Key? key}) : super(key: key);

  @override
  State<LobbyScreen> createState() => _LobbyScreenState();
}

class _LobbyScreenState extends State<LobbyScreen> {
  // Scaffold를 제어하기 위한 GlobalKey
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey, // Scaffold에 GlobalKey 할당
      appBar: AppBar(
        title: const Text('Lobby'), // 앱바 타이틀
        actions: [
          // 오른쪽 상단 햄버거(메뉴) 버튼
          IconButton(
            icon: const Icon(Icons.menu),
            onPressed: () {
              // 버튼 클릭 시 오른쪽에서 Drawer(메뉴) 열기
              _scaffoldKey.currentState?.openEndDrawer();
            },
          ),
        ],
      ),
      // 오른쪽에서 나타나는 Drawer(옵션 메뉴)
      endDrawer: Drawer(
        child: ListView(
          padding: EdgeInsets.zero, // 패딩 없음
          children: <Widget>[
            DrawerHeader(
              decoration: const BoxDecoration(
                color: Colors.blue, // 앱 위의 배경색
              ),
              child: const Text(
                'Options', // 앱 위의 텍스트
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                ),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.home), // 아이콘
              title: const Text('Home'), // 메뉴 이름
              onTap: () {
                Navigator.pop(context); // Drawer 닫기
                // 홈 화면 이동 추가(예정)
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings),
              title: const Text('Settings'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const SettingsScreen()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.info),
              title: const Text('About'),
              onTap: () {
                Navigator.pop(context); // Drawer 닫기
                // 앱 정보 화면 이동 추가(예정)
              },
            ),
          ],
        ),
      ),
    );
  }
}
