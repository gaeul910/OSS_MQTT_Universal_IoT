import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:pinput/pinput.dart';
import 'lobby.dart';
import 'notifications.dart';
import 'gps.dart';
import 'session.dart';
// 로그인 페이지 위젯 (StatefulWidget으로 입력값 관리)
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});
  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  // 올바른 인증코드를 미리 지정 (차후 API에서 랜덤 시드로 결정된 코드를 받아와야 한다.)
  final String correctCode = '123456';

  final TextEditingController _textController = TextEditingController(); // ip 입력 컨트롤러
  final TextEditingController _portController = TextEditingController(); // 포트 입력 컨트롤러
  final TextEditingController _uidController = TextEditingController();  // uid 입력 컨트롤러

  // 사용자가 입력한 인증코드 저장 변수
  String _enteredCode = '';

  // 세션 토큰 저장 변수
  String? _sessionToken;

  // 로그인 버튼 클릭 시 실행되는 함수
  Future<void> _onLogin(BuildContext context, String code) async {
    String inputText = _textController.text.trim(); // 문자열 입력값
    String portText = _portController.text.trim();
    String uidText = _uidController.text.trim();

    // 주소 입력이 비었는지 체크
    if (inputText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('주소를 입력해주세요.')),
      );
      return;
    }
    if (portText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('포트 번호를 입력해주세요.')),
      );
      return;
    }
    if (uidText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('uid를 입력해주세요.')),
      );
      return;
    }
    // uid는 숫자만 입력 가능
    int? userId = int.tryParse(uidText);
    if (userId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('uid는 숫자만 입력해야 합니다.')),
      );
      return;
    }

    // 서버로 uid와 인증코드 전송
    final url = Uri.parse('http://$inputText:$portText/connect');
    final headers = {'Content-Type': 'application/json'};
    final body = jsonEncode({
      'uid': userId,
      'auth_code': code,
    });

    try {
      final response = await http.post(url, headers: headers, body: body);

      final sessionToken = response.body.trim();

      if (response.statusCode == 200 && sessionToken.isNotEmpty) {
        setState(() {
          _sessionToken = sessionToken;
        });
        //세션 매니저에 세션 토큰과 서버 정보 등록 (자동 갱신 시작)
        SessionManager().configure(
          sessionToken: sessionToken,
          ip: inputText,
          port: portText,
        );

        // NotificationService, GpsTracker 등에 서버 정보 및 세션 토큰 전달
        NotificationService().configure(
          ip: inputText,
          port: portText,
          uid: userId,
        );
        NotificationService().startPolling();

        GpsTracker().configure(
          ip: inputText,
          port: portText,
          uid: userId,
        );
        GpsTracker().startTracking();

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const LobbyScreen()),
        );
        // 로그인 성공 시 추가 작업 가능
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('로그인 실패 또는 세션 토큰 없음: ${response.body}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('서버 연결 실패: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('통신정보 및 인증코드 입력')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 문자열 입력 필드
            TextField(
              controller: _textController, // 입력값을 컨트롤러로 관리
              decoration: const InputDecoration(
                labelText: '문자열 입력', // 힌트(라벨) 텍스트
                border: OutlineInputBorder(), // 테두리 스타일
              ),
            ),
            const SizedBox(height: 24), // 위젯 사이 간격

            // 포트 번호 입력 필드
            TextField(
              controller: _portController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: '포트 번호 입력',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),

            // uid 입력 필드
            TextField(
              controller: _uidController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                labelText: 'uid 입력 (숫자)',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 24),

            // 인증코드 입력 필드 (Pinput)
            Pinput(
              length: 6, // 6자리로 고정
              keyboardType: TextInputType.number, // 숫자 키패드 표시
              onCompleted: (code) {
                // 인증코드 입력이 끝나면 코드 저장
                setState(() {
                  _enteredCode = code;
                });
              },
            ),
            const SizedBox(height: 24), // 위젯 사이 간격

            // 로그인 버튼
            ElevatedButton(
              onPressed: () => _onLogin(context, _enteredCode),
              child: const Text('로그인'),
            ),
          ],
        ),
      ),
    );
  }
}