import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  // 싱글톤 패턴
  static final NotificationService _instance = NotificationService._internal();

  factory NotificationService() => _instance;

  NotificationService._internal();

  // 상태 변수
  bool _isPolling = false;
  Isolate? _pollingIsolate;
  ReceivePort? _receivePort;

  // 서버 연결 정보
  late String _ip;
  late String _port;
  late String _uid; // String으로 선언

  final FlutterLocalNotificationsPlugin _notificationsPlugin = FlutterLocalNotificationsPlugin();

  /// 알림 권한 요청 (앱 시작 시 호출)
  Future<void> requestNotificationPermission() async {
    await _notificationsPlugin
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();

    await _notificationsPlugin
        .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>()
        ?.requestPermissions(alert: true, badge: true, sound: true);
  }

  /// 서버 정보 세팅 (로그인 후 호출)
  void configure({required String ip, required String port, required dynamic uid}) {
    _ip = ip;
    _port = port;
    _uid = uid.toString();
  }

  /// 알림 플러그인 초기화
  Future<void> initialize() async {
    const AndroidInitializationSettings initializationSettingsAndroid =
    AndroidInitializationSettings('@mipmap/ic_launcher');
    const DarwinInitializationSettings initializationSettingsIOS =
    DarwinInitializationSettings();
    const InitializationSettings initializationSettings = InitializationSettings(
      android: initializationSettingsAndroid,
      iOS: initializationSettingsIOS,
    );
    await _notificationsPlugin.initialize(initializationSettings);
  }

  /// 롱 폴링 시작
  Future<void> startPolling() async {
    if (_isPolling) return;
    if (_ip.isEmpty || _port.isEmpty) {
      debugPrint('서버 정보가 설정되지 않았습니다.');
      return;
    }
    _isPolling = true;
    _receivePort = ReceivePort();

    _pollingIsolate = await Isolate.spawn(
      _pollingTask,
      {
        'sendPort': _receivePort!.sendPort,
        'ip': _ip,
        'port': _port,
        'uid': _uid, // 추가!
      },
    );

    _receivePort!.listen((dynamic message) {
      if (message is Map<String, dynamic>) {
        _handleNotification(message);
      }
    });

    debugPrint('백그라운드 알림 롱폴링이 시작되었습니다.');
  }

  /// 롱 폴링 중지
  void stopPolling() {
    if (!_isPolling) return;
    _pollingIsolate?.kill();
    _receivePort?.close();
    _pollingIsolate = null;
    _receivePort = null;
    _isPolling = false;
    debugPrint('백그라운드 알림 롱폴링이 중지되었습니다.');
  }

  /// 알림 표시 및 상태 업데이트
  Future<void> _handleNotification(Map<String, dynamic> notification) async {
    final int id = notification['id'] is int
        ? notification['id']
        : int.tryParse(notification['id'].toString()) ?? 0;
    final String content = notification['content']?.toString() ?? '새로운 알림이 있습니다.';

    await _showNotification(id, 'IoT 알림', content);
    //await _updateNotificationStatus(id); //나중에 추가할 것

    debugPrint('알림 수신 및 상태 업데이트: ID=$id, 내용=$content');
  }
}