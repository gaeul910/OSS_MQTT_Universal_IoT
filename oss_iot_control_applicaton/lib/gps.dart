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
}