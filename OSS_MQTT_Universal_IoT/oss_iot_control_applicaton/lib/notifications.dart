import 'dart:async';
import 'dart:convert';
import 'dart:isolate';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'session.dart';

class NotificationService {
  static final NotificationService _instance = NotificationService._internal();

  factory NotificationService() => _instance;

  NotificationService._internal();

  final FlutterLocalNotificationsPlugin _notificationsPlugin = FlutterLocalNotificationsPlugin();
  // 상태 변수
  bool _isPolling = false;
  Isolate? _pollingIsolate;
  ReceivePort? _receivePort;

  // 서버 연결 정보
  late String _ip;
  late String _port;
  late String _uid; // String으로 선언
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
        'uid': _uid,
        'sessionToken': SessionManager().sessionToken ?? '',
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

    await _updateNotificationStatus(id);


    debugPrint('알림 수신 및 상태 업데이트: ID=$id, 내용=$content');
  }

  /// 직접 호출 가능한 알림 표시 (테스트용)
  Future<void> showNotification({
    int id = 0,
    String title = '테스트 알림',
    String body = '이것은 테스트 알림입니다.',
  }) async {
    await _showNotification(id, title, body);
  }

  /// 내부용 알림 표시
  Future<void> _showNotification(int id, String title, String body) async {
    const AndroidNotificationDetails androidPlatformChannelSpecifics =
    AndroidNotificationDetails(
      'iot_notification_channel',
      'IoT 알림',
      importance: Importance.high,
      priority: Priority.high,
    );
    const NotificationDetails platformChannelSpecifics =
    NotificationDetails(android: androidPlatformChannelSpecifics);

    await _notificationsPlugin.show(
      id,
      title,
      body,
      platformChannelSpecifics,
    );
  }

  //이미 받은 알림의 stat 값을 1로 초기화 하는 기능
  Future<bool> _updateNotificationStatus(int notificationId) async {
    try {
      final response = await http.post(
        Uri.parse('http://$_ip:$_port/notification/sync'),
        headers: {
          'content-type': 'application/json',
          'session-token': SessionManager().sessionToken ?? '',
        },
        body: json.encode({
          'notification_id': notificationId,
        }),
      );
      return response.statusCode == 200;
    } catch (e) {
      debugPrint('알림 상태 업데이트 실패: $e');
      return false;
    }
  }

  /// 롱 폴링 작업 (Isolate에서 실행)
  static Future<void> _pollingTask(Map<String, dynamic> params) async {
    final String sessionToken = params['sessionToken'] ?? '';
    final SendPort sendPort = params['sendPort'];
    final String ip = params['ip'];
    final String port = params['port'];
    final String uid = params['uid'];

    Future<List<Map<String, dynamic>>> _longPoll() async {
      try {
        final syncResponse = await http.get(
          Uri.parse('http://$ip:$port/notification/sync'),
          headers: {
            'uid': uid,
            'content-type': 'application/json',
            'session-token': sessionToken,
          },
        ).timeout(const Duration(seconds: 40));

        if (syncResponse.statusCode == 200) {
          final idList = json.decode(syncResponse.body);
          if (idList is List && idList.isNotEmpty) {
            List<Map<String, dynamic>> notifications = [];
            for (final item in idList) {
              final idValue = (item is Map && item.containsKey('id')) ? item['id'] : item;
              final notiResponse = await http.get(
                Uri.parse('http://$ip:$port/notification/getnoti'),
                headers: {
                  'id': idValue.toString(),
                  'session-token': sessionToken,
                },
              );
              if (notiResponse.statusCode == 200) {
                final notiData = json.decode(notiResponse.body);
                if (notiData is Map<String, dynamic> && notiData.isNotEmpty) {
                  notifications.add(notiData);
                } else if (notiData is List && notiData.isNotEmpty && notiData.first is Map<String, dynamic>) {
                  notifications.add(notiData.first); // 리스트의 첫 Map만 추가 (여러 개면 반복문 사용)
                }
              }
            }
            return notifications;
          }
        }
        return [];
      } catch (e) {
        print('롱 폴링 중 에러 발생: $e');
        await Future.delayed(const Duration(seconds: 5));
        return [];
      }
    }

    while (true) {
      final notifications = await _longPoll();
      for (final notification in notifications) {
        sendPort.send(notification);
      }
      await Future.delayed(const Duration(seconds: 1));
    }
  }
}
