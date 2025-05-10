import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';
import 'lobby.dart';
// 로그인 페이지 위젯 (StatefulWidget으로 입력값 관리)
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  // 올바른 인증코드를 미리 지정 (차후 API에서 랜덤 시드로 결정된 코드를 받아와야 한다.)
  final String correctCode = '123456';

  // 문자열 입력을 위한 컨트롤러
  final TextEditingController _textController = TextEditingController();

  // 사용자가 입력한 인증코드 저장 변수
  String _enteredCode = '';

  // 로그인 버튼 클릭 시 실행되는 함수
  void _onLogin(BuildContext context, String code) {
    String inputText = _textController.text.trim(); // 문자열 입력값

    // 주소 입력이 비었는지 체크
    if (inputText.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('주소를 입력해주세요.')),
      );
      return;
    }

    // 인증코드가 일치하는지 체크
    if (code == correctCode) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const LobbyScreen()),
      );
      // 로그인 성공 시 추가 작업 가능
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('코드가 일치하지 않습니다.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('주소 + 6자리 코드 입력')),
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
