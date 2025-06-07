import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'session.dart';
/// 위치 추적 및 서버 전송 싱글톤 서비스
class GpsTracker {
  static final GpsTracker _instance = GpsTracker._internal();
  factory GpsTracker() => _instance;
  GpsTracker._internal();

  bool get isTracking => _isTracking;
  set isTracking(bool value) => _isTracking = value;

  StreamSubscription<Position>? get positionStream => _positionStream;
  set positionStream(StreamSubscription<Position>? value) => _positionStream = value;

  Timer? get sendTimer => _sendTimer;
  set sendTimer(Timer? value) => _sendTimer = value;

  @visibleForTesting
  Future<void> sendLocationToServerForTest() => _sendLocationToServer();

  // 서버 정보 및 사용자 정보
  late String _ip;
  late String _port;
  late String _uid;

  // 위치 정보
  double? latitude;
  double? longitude;

  // 내부 상태
  bool _isTracking = false;
  StreamSubscription<Position>? _positionStream;
  Timer? _sendTimer;

  /// 서버 정보 및 uid 설정 (로그인 시 호출)
  void configure({required String ip, required String port, required dynamic uid}) {
    _ip = ip;
    _port = port;
    _uid = uid.toString();
  }

  /// 위치 추적 시작 및 주기적 서버 전송
  Future<void> startTracking({void Function(Position)? onUpdate}) async {
    // 권한 및 서비스 체크
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('위치 서비스가 꺼져 있습니다.');
    }
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('위치 권한이 거부되었습니다.');
      }
    }
    if (permission == LocationPermission.deniedForever) {
      throw Exception('위치 권한이 영구적으로 거부되었습니다.');
    }

    if (_isTracking) return; // 중복 방지
    _isTracking = true;

    // 실시간 위치 스트림 구독
    _positionStream = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
      ),
    ).listen((Position position) {
      latitude = position.latitude;
      longitude = position.longitude;
      if (onUpdate != null) onUpdate(position);
      debugPrint('실시간 위치: $latitude, $longitude');
    });

    // 1분마다 서버 전송 타이머 시작
    _sendTimer = Timer.periodic(const Duration(minutes: 1), (timer) {
      if (latitude != null && longitude != null) {
        _sendLocationToServer();
      }
    });
  }

  /// 위치 추적 및 전송 중지
  void stopTracking() {
    _positionStream?.cancel();
    _sendTimer?.cancel();
    _isTracking = false;
  }

  /// 서버로 위치 전송
  Future<void> _sendLocationToServer() async {
    if (_ip.isEmpty || _port.isEmpty || _uid.isEmpty || latitude == null || longitude == null) return;

    try {
      final format = DateFormat('yyyy-MM-dd HH:mm:ss');
      final timeString = format.format(DateTime.now());

      final body = jsonEncode({
        'uid': _uid,
        'time': timeString,
        'coordinate': 'POINT($latitude $longitude)',
      });

      final response = await http.post(
        Uri.parse('http://$_ip:$_port/location/logs'),
        headers: {
          'content-type': 'application/json',
          'session-token': SessionManager().sessionToken ?? '',
        },
        body: body,
      );

      if (response.statusCode == 200) {
        debugPrint('위치 전송 성공');
      } else {
        debugPrint('위치 전송 실패: ${response.body}');
      }
    } catch (e) {
      debugPrint('위치 전송 오류: $e');
    }
  }
}

/// 예시: 실시간 위치 표시 및 추적 컨트롤 위젯
class GpsTestScreen extends StatefulWidget {
  const GpsTestScreen({super.key});

  @override
  State<GpsTestScreen> createState() => _GpsTestScreenState();
}

class _GpsTestScreenState extends State<GpsTestScreen> {
  String status = "위치 정보 없음";
  bool _isTracking = false;

  @override
  void dispose() {
    GpsTracker().stopTracking();
    super.dispose();
  }

  Future<void> _startTracking() async {
    setState(() {
      status = "위치 추적 시작 중...";
      _isTracking = true;
    });
    try {
      await GpsTracker().startTracking(onUpdate: (pos) {
        setState(() {
          status = "위치 갱신됨";
        });
      });
    } catch (e) {
      setState(() {
        status = "에러: $e";
        _isTracking = false;
      });
    }
  }

  void _stopTracking() {
    GpsTracker().stopTracking();
    setState(() {
      _isTracking = false;
      status = "위치 추적 중지됨";
    });
  }

  @override
  Widget build(BuildContext context) {
    final latitude = GpsTracker().latitude;
    final longitude = GpsTracker().longitude;

    return Scaffold(
      appBar: AppBar(
        title: const Text('GPS 실시간 추적'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('위도: ${latitude?.toStringAsFixed(6) ?? "알 수 없음"}'),
            Text('경도: ${longitude?.toStringAsFixed(6) ?? "알 수 없음"}'),
            Text('상태: $status'),
            const SizedBox(height: 20),
            _isTracking
                ? ElevatedButton(
              onPressed: _stopTracking,
              child: const Text('위치 추적 중지'),
            )
                : ElevatedButton(
              onPressed: _startTracking,
              child: const Text('위치 추적 시작'),
            ),
          ],
        ),
      ),
    );
  }
}