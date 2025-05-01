// lib/main.dart
import 'package:flutter/material.dart';
import 'login.dart'; // LoginPage가 정의된 파일 import

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false, // 디버그 배너 제거 (선택)
      home: LoginPage(), // 앱 시작 시 LoginPage를 첫 화면으로 지정
    );
  }
}