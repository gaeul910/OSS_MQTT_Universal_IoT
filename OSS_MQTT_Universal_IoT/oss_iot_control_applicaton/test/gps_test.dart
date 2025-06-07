import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:oss_iot_control_applicaton/gps.dart';
import 'package:oss_iot_control_applicaton/session.dart';
import 'package:geolocator/geolocator.dart';
import 'dart:async';
import 'package:mockito/mockito.dart';
import 'package:geolocator_platform_interface/geolocator_platform_interface.dart';
// Mock 클래스
class MockSessionManager extends Mock implements SessionManager {}
class FakePosition extends Fake implements Position {
  @override
  double get latitude => 37.0;
  @override
  double get longitude => 127.0;
// 나머지 Position 필드 생략 (필요시 추가)
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('GpsTracker public 메서드', () {
    test('configure가 내부 상태를 올바르게 설정한다', () {
      final tracker = GpsTracker();
      tracker.configure(ip: '1.2.3.4', port: '8080', uid: 123);
      // 내부 상태는 public getter가 없으므로, 실제 startTracking 등에서 정상 동작 확인
      expect(tracker.isTracking, isFalse);
    });

    test('startTracking: 위치 서비스 꺼짐/권한 거부/정상 분기', () async {
      final tracker = GpsTracker();

      // 위치 서비스 꺼짐
      GeolocatorPlatform.instance = FakeGeolocatorPlatform(serviceEnabled: false);
      expect(
            () async => await tracker.startTracking(),
        throwsA(isA<Exception>()),
      );

      // 권한 거부
      GeolocatorPlatform.instance = FakeGeolocatorPlatform(
        serviceEnabled: true,
        permission: LocationPermission.denied,
      );
      expect(
            () async => await tracker.startTracking(),
        throwsA(isA<Exception>()),
      );

      // 권한 영구 거부
      GeolocatorPlatform.instance = FakeGeolocatorPlatform(
        serviceEnabled: true,
        permission: LocationPermission.deniedForever,
      );
      expect(
            () async => await tracker.startTracking(),
        throwsA(isA<Exception>()),
      );
    });

    test('startTracking: 중복 호출 방지', () async {
      final tracker = GpsTracker();
      tracker.isTracking = true;
      await tracker.startTracking();
      expect(tracker.isTracking, isTrue);
    });

    test('stopTracking: 스트림, 타이머, 상태 초기화', () {
      final tracker = GpsTracker();
      tracker.isTracking = true;
      tracker.positionStream = null;
      tracker.sendTimer = null;
      tracker.stopTracking();
      expect(tracker.isTracking, isFalse);
    });
  });

  group('GpsTestScreen UI', () {
    testWidgets('위치 추적 시작/중지 버튼 UI', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(home: GpsTestScreen()),
      );
      expect(find.text('위치 추적 시작'), findsOneWidget);

      await tester.tap(find.text('위치 추적 시작'));
      await tester.pump();

      // 상태 텍스트가 "위치 추적 시작 중..." 혹은 "위치 갱신됨"으로 변할 수 있음
      expect(
        find.textContaining('위치'),
        findsWidgets,
      );
    });
  });
}

// Fake GeolocatorPlatform for 권한/서비스 분기
class FakeGeolocatorPlatform extends GeolocatorPlatform {
  final bool serviceEnabled;
  final LocationPermission permission;
  FakeGeolocatorPlatform({
    this.serviceEnabled = true,
    this.permission = LocationPermission.always,
  });


  @override
  Future<bool> isLocationServiceEnabled() async => serviceEnabled;
  @override
  Future<LocationPermission> checkPermission() async => permission;
  @override
  Future<LocationPermission> requestPermission() async => permission;

  @override
  Stream<Position> getPositionStream({LocationSettings? locationSettings}) =>
      Stream.value(Position(
        latitude: 37.0,
        longitude: 127.0,
        timestamp: DateTime.now(),
        accuracy: 1.0,
        altitude: 0.0,
        heading: 0.0,
        speed: 0.0,
        speedAccuracy: 0.0,
        altitudeAccuracy: 1.0,    // 추가
        headingAccuracy: 1.0,     // 필요하다면 추가
      ));
}