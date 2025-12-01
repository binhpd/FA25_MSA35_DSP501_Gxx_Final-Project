import '../utils/api_config.dart';

class ApiConstants {
  // Backend API base URL
  // Automatically detects platform and uses appropriate URL:
  // - iOS Simulator: http://127.0.0.1:8000
  // - Android Emulator: http://10.0.2.2:8000
  // - Physical Device: http://<your-computer-ip>:8000 (set in ApiConfig.physicalDeviceHost)
  // 
  // ⚠️ IMPORTANT: Switch between emulator and physical device:
  // - For Android Emulator: use ApiConfig.getBaseUrl()
  // - For Physical Device: use ApiConfig.getPhysicalDeviceUrl()
  // 
  // Current setting: Physical Device (192.168.1.216)
  // This getter calls ApiConfig.getPhysicalDeviceUrl() which returns http://192.168.1.216:8000
  static String get baseUrl => ApiConfig.getPhysicalDeviceUrl(); // ← Used for Android physical device
  
  // To use Android Emulator instead, change to:
  // static String get baseUrl => ApiConfig.getBaseUrl();
  
  // API Endpoints
  static const String recognizeEndpoint = '/recognize';
  static const String learnEndpoint = '/learn';
  static const String statsEndpoint = '/stats';
  static const String songsEndpoint = '/songs';
}


