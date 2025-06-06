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
  /// 세션 키 반환 (앱 전체에서 사용)
  String? get sessionToken => _sessionToken;

  /// 서버 정보 반환 (필요시)
  String? get ip => _ip;
  String? get port => _port;

  /// 매일 자정마다 세션 갱신 타이머 설정
  void _setupRenewTimer() {
    _renewTimer?.cancel();

    final now = DateTime.now();
    final nextMidnight = DateTime(now.year, now.month, now.day + 1);
    final duration = nextMidnight.difference(now);

    // 자정까지 기다렸다가, 이후 매 24시간마다 갱신
    _renewTimer = Timer(duration, () {
      _renewSession();
      _renewTimer = Timer.periodic(const Duration(days: 1), (_) => _renewSession());
    });
  }
}