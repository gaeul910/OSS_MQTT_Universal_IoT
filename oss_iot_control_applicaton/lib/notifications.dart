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

}