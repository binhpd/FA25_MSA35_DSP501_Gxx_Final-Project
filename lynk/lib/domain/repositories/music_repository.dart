abstract class MusicRepository {
  Future<Map<String, dynamic>?> recognizeSong(String audioFilePath);
  Future<bool> checkMicrophonePermission();
  Future<bool> requestMicrophonePermission();
}
