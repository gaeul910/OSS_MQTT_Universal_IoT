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

  Timer? get renewTimer => _renewTimer;
  Future<void> renewSession() => _renewSession();
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

  /// 세션 갱신 요청
  Future<void> _renewSession() async {
    if (_sessionToken == null || _ip == null || _port == null) return;

    final url = Uri.parse('http://$_ip:$_port/renew_session');
    try {
      final response = await http.post(
        url,
        headers: {'session-token': _sessionToken!},
      );
      if (response.statusCode == 200) {
        // 새 세션 키가 plain text로 온다고 가정
        final newToken = response.body.trim();
        if (newToken.isNotEmpty) {
          _sessionToken = newToken;
          print('[SessionManager] 세션 키 갱신 성공: $newToken');
        } else {
          print('[SessionManager] 세션 키 갱신 실패: 응답이 비어 있음');
        }
      } else {
        print('[SessionManager] 세션 키 갱신 실패: ${response.statusCode} ${response.body}');
      }
    } catch (e) {
      print('[SessionManager] 세션 키 갱신 오류: $e');
    }
  }

  /// 앱 종료 등에서 타이머 해제
  void dispose() {
    _renewTimer?.cancel();
  }
}