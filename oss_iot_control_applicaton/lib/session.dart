import 'dart:async';
import 'package:http/http.dart' as http;

class SessionManager {
  // 싱글톤 패턴
  static final SessionManager _instance = SessionManager._internal();

  factory SessionManager() => _instance;

  SessionManager._internal();

  String? _sessionToken;
  String? _ip;
  String? _port;

  Timer? _renewTimer;

  /// 세션 키, 서버 정보 저장
  void configure({
    required String sessionToken,
    required String ip,
    required String port,
  }) {
    _sessionToken = sessionToken;
    _ip = ip;
    _port = port;
    _setupRenewTimer();
  }
}