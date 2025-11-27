import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../../core/constants/api_constants.dart';

class MusicRemoteDataSource {
  final Dio _dio;

  MusicRemoteDataSource(this._dio);

  Future<Map<String, dynamic>> recognizeSong(String audioFilePath) async {
    try {
      final file = File(audioFilePath);
      
      if (!await file.exists()) {
        throw Exception('Audio file not found: $audioFilePath');
      }

      // Log request
      debugPrint('🎵 [API] Starting recognition request');
      debugPrint('📁 [API] File path: $audioFilePath');
      debugPrint('📊 [API] File size: ${await file.length()} bytes');
      debugPrint('🌐 [API] URL: ${ApiConstants.baseUrl}${ApiConstants.recognizeEndpoint}');

      // Create FormData with file
      // Extract actual filename from path to preserve extension
      final fileName = audioFilePath.split('/').last;
      final formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(
          audioFilePath,
          filename: fileName.isNotEmpty ? fileName : 'recording.m4a',
        ),
      });

      // Make POST request
      final response = await _dio.post<Map<String, dynamic>>(
        ApiConstants.recognizeEndpoint,
        data: formData,
        options: Options(
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        ),
      );

      // Log response
      debugPrint('✅ [API] Response received');
      debugPrint('📥 [API] Status code: ${response.statusCode}');
      debugPrint('📦 [API] Response data: ${response.data}');

      if (response.data == null) {
        throw Exception('Empty response from server');
      }

      return response.data!;
    } on DioException catch (e) {
      // Log error details
      debugPrint('❌ [API] Error occurred');
      debugPrint('🔴 [API] Error type: ${e.type}');
      debugPrint('🔴 [API] Error message: ${e.message}');
      
      if (e.response != null) {
        debugPrint('🔴 [API] Response status: ${e.response?.statusCode}');
        debugPrint('🔴 [API] Response data: ${e.response?.data}');
        throw Exception(
          'Server error: ${e.response?.statusCode} - ${e.response?.data?['detail'] ?? e.message}',
        );
      } else if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw Exception('Connection timeout. Please check if the server is running.');
      } else if (e.type == DioExceptionType.connectionError) {
        throw Exception(
          'Cannot connect to server. Please check:\n'
          '1. Backend server is running (python backend/main.py)\n'
          '2. Server URL is correct: ${ApiConstants.baseUrl}\n'
          '3. For iOS Simulator: use http://127.0.0.1:8000\n'
          '4. For physical device: use your computer IP address',
        );
      } else {
        throw Exception('Network error: ${e.message}');
      }
    } catch (e) {
      debugPrint('❌ [API] Unexpected error: $e');
      rethrow;
    }
  }
}


