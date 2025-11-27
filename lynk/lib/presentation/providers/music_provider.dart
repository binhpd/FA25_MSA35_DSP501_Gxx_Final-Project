import 'package:flutter/foundation.dart';
import '../../domain/entities/song.dart';
import '../../domain/repositories/music_repository.dart';

enum RecordingState {
  idle,
  recording,
  processing,
  completed,
  error,
}

class MusicProvider extends ChangeNotifier {
  final MusicRepository musicRepository;

  MusicProvider(this.musicRepository);

  RecordingState _recordingState = RecordingState.idle;
  Song? _recognizedSong;
  String? _error;
  String? _audioFilePath;
  int _recordingDuration = 0;
  double _confidence = 0.0;
  int _matches = 0;

  RecordingState get recordingState => _recordingState;
  Song? get recognizedSong => _recognizedSong;
  String? get error => _error;
  String? get audioFilePath => _audioFilePath;
  int get recordingDuration => _recordingDuration;
  double get confidence => _confidence;
  int get matches => _matches;

  bool get isRecording => _recordingState == RecordingState.recording;
  bool get isProcessing => _recordingState == RecordingState.processing;
  bool get isCompleted => _recordingState == RecordingState.completed;

  Future<void> startRecording(String filePath) async {
    _recordingState = RecordingState.recording;
    _audioFilePath = filePath;
    _error = null;
    _recordingDuration = 0;
    notifyListeners();
  }

  void updateRecordingDuration(int seconds) {
    _recordingDuration = seconds;
    notifyListeners();
  }

  Future<void> stopRecording() async {
    if (_recordingState != RecordingState.recording) return;

    _recordingState = RecordingState.processing;
    _error = null;
    notifyListeners();

    try {
      if (_audioFilePath != null) {
        final result = await musicRepository.recognizeSong(_audioFilePath!);
        if (result != null) {
          _recognizedSong = result['song'] as Song?;
          _confidence = result['confidence'] as double? ?? 0.0;
          _matches = result['matches'] as int? ?? 0;
          if (_recognizedSong != null) {
            _recordingState = RecordingState.completed;
          } else {
            _recordingState = RecordingState.idle;
            _error = 'Không nhận diện được bài hát';
          }
        } else {
          _recordingState = RecordingState.idle;
          _error = 'Không nhận diện được bài hát';
        }
      } else {
        _recordingState = RecordingState.error;
        _error = 'Không tìm thấy file ghi âm';
      }
    } catch (e) {
      _recordingState = RecordingState.error;
      _error = e.toString();
    } finally {
      notifyListeners();
    }
  }

  void reset() {
    _recordingState = RecordingState.idle;
    _recognizedSong = null;
    _error = null;
    _audioFilePath = null;
    _recordingDuration = 0;
    _confidence = 0.0;
    _matches = 0;
    notifyListeners();
  }
}





