import 'dart:io';
import 'package:flutter/foundation.dart';
import '../../domain/entities/song.dart';
import '../../domain/repositories/music_repository.dart';
import '../datasources/music_remote_datasource.dart';

class MusicRepositoryImpl implements MusicRepository {
  final MusicRemoteDataSource remoteDataSource;

  MusicRepositoryImpl(this.remoteDataSource);

  @override
  Future<Map<String, dynamic>?> recognizeSong(String audioFilePath) async {
    try {
      debugPrint('🎵 [Repository] Starting song recognition');
      debugPrint('📁 [Repository] Audio file: $audioFilePath');

      // Validate file exists
      final audioFile = File(audioFilePath);
      if (!await audioFile.exists()) {
        throw Exception('Audio file not found: $audioFilePath');
      }

      // Call API
      final response = await remoteDataSource.recognizeSong(audioFilePath);

      debugPrint('✅ [Repository] API call successful');
      debugPrint('📦 [Repository] Response: $response');

      // Parse response
      final success = response['success'] as bool? ?? false;
      
      if (!success) {
        final message = response['message'] as String? ?? 'Song not recognized';
        debugPrint('⚠️ [Repository] Recognition failed: $message');
        return null;
      }

      final songName = response['song'] as String?;
      final confidence = response['confidence'] as num? ?? 0.0;
      final matches = response['matches'] as int? ?? 0;

      if (songName == null || songName.isEmpty) {
        debugPrint('⚠️ [Repository] No song name in response');
        return null;
      }

      debugPrint('🎉 [Repository] Song recognized: $songName');
      debugPrint('📊 [Repository] Confidence: $confidence%');
      debugPrint('🔢 [Repository] Matches: $matches');

      // Create Song entity
      final song = Song(
        id: songName.toLowerCase().replaceAll(' ', '_'),
        title: songName,
        artist: 'Unknown Artist', // Backend doesn't provide artist yet
        album: null,
        coverImageUrl: null,
        recognizedAt: DateTime.now(),
      );

      // Return map with song, confidence, and matches
      return {
        'song': song,
        'confidence': confidence.toDouble(),
        'matches': matches,
      };
    } catch (e) {
      debugPrint('❌ [Repository] Error: $e');
      throw Exception('Failed to recognize song: $e');
    }
  }

  @override
  Future<bool> checkMicrophonePermission() async {
    // This will be implemented with permission_handler
    // For now, return true for demo
    return true;
  }

  @override
  Future<bool> requestMicrophonePermission() async {
    // This will be implemented with permission_handler
    // For now, return true for demo
    return true;
  }
}
