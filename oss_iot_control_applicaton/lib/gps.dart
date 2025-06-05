import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';

/// 위치 추적 및 서버 전송 싱글톤 서비스
class GpsTracker {
  static final GpsTracker _instance = GpsTracker._internal();

  factory GpsTracker() => _instance;

  GpsTracker._internal();

  // 서버 정보 및 사용자 정보
  late String _ip;
  late String _port;
  late String _uid;
  String _sessionToken = 'your_token_here'; // 필요시 setter로 변경

  // 위치 정보
  double? latitude;
  double? longitude;

  // 내부 상태
  bool _isTracking = false;
  StreamSubscription<Position>? _positionStream;
  Timer? _sendTimer;

  /// 서버 정보 및 uid 설정 (로그인 시 호출)
  void configure({required String ip, required String port, required dynamic uid, String? sessionToken}) {
    _ip = ip;
    _port = port;
    _uid = uid.toString();
    if (sessionToken != null) _sessionToken = sessionToken;
  }
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
