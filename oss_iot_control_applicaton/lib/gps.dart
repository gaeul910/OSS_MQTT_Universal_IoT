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
}