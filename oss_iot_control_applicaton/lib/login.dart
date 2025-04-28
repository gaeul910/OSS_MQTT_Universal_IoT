import 'package:flutter/material.dart';
import 'package:pinput/pinput.dart';

class LoginPage extends StatelessWidget {
  final String correctCode = '123456';

  LoginPage({super.key});

  void _onCodeEntered(BuildContext context, String code) {
    if (code == correctCode) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('로그인 성공')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('코드가 일치하지 않습니다.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('6자리 로그인')),
      body: Center(
        child: Pinput(
          length: 6,
          keyboardType: TextInputType.number,
          onCompleted: (code) => _onCodeEntered(context, code),
        ),
      ),
    );
  }
}