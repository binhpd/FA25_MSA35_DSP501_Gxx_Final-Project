import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';

class PermissionProvider extends ChangeNotifier {
  bool _microphonePermissionGranted = false;
  bool _isChecking = false;

  bool get microphonePermissionGranted => _microphonePermissionGranted;
  bool get isChecking => _isChecking;

  Future<void> checkMicrophonePermission() async {
    _isChecking = true;
    notifyListeners();

    try {
      final status = await Permission.microphone.status;
      _microphonePermissionGranted = status.isGranted;
    } catch (e) {
      _microphonePermissionGranted = false;
    } finally {
      _isChecking = false;
      notifyListeners();
    }
  }

  Future<bool> requestMicrophonePermission() async {
    _isChecking = true;
    notifyListeners();

    try {
      final status = await Permission.microphone.request();
      _microphonePermissionGranted = status.isGranted;
      return _microphonePermissionGranted;
    } catch (e) {
      _microphonePermissionGranted = false;
      return false;
    } finally {
      _isChecking = false;
      notifyListeners();
    }
  }
}





