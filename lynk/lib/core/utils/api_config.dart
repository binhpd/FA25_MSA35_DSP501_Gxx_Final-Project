import 'dart:io';
import 'package:flutter/foundation.dart';

/// Utility class to determine the correct API base URL based on the platform
class ApiConfig {
  // Default port for backend
  static const int defaultPort = 8000;

  // For Android Emulator, use 10.0.2.2 to access host machine's localhost
  static const String androidEmulatorHost = '10.0.2.2';

  // For iOS Simulator, use 127.0.0.1
  static const String iosSimulatorHost = '127.0.0.1';

  // For physical devices, you need to set your computer's IP address
  // Get your IP: 
  // - macOS/Linux: ipconfig getifaddr en0
  // - Windows: ipconfig
  // Current IP: 192.168.1.216 (updated for Android physical device)
  static const String physicalDeviceHost = '192.168.1.216';

  /// Get the base URL based on the current platform
  static String getBaseUrl({int? port, String? customHost}) {
    final int apiPort = port ?? defaultPort;
    
    // If custom host is provided, use it
    if (customHost != null && customHost.isNotEmpty) {
      return 'http://$customHost:$apiPort';
    }

    // Auto-detect based on platform
    if (kIsWeb) {
      // Web platform
      return 'http://localhost:$apiPort';
    } else if (Platform.isAndroid) {
      // Android Emulator uses 10.0.2.2 to access host machine
      return 'http://$androidEmulatorHost:$apiPort';
    } else if (Platform.isIOS) {
      // iOS Simulator
      return 'http://$iosSimulatorHost:$apiPort';
    } else {
      // Desktop platforms (macOS, Windows, Linux)
      return 'http://localhost:$apiPort';
    }
  }

  /// Get base URL for physical Android device
  /// Call this method if you're running on a physical Android device
  /// 
  /// This method is used by ApiConstants.baseUrl when building for physical devices
  /// See: lib/core/constants/api_constants.dart line 15
  static String getPhysicalDeviceUrl({int? port}) {
    final int apiPort = port ?? defaultPort;
    return 'http://$physicalDeviceHost:$apiPort';
  }

  /// Check if running on emulator/simulator
  static bool isEmulator() {
    if (kIsWeb) return false;
    if (Platform.isAndroid) {
      // Android emulator typically uses 10.0.2.2
      // Physical devices will need the actual IP
      return true; // Assume emulator by default
    }
    if (Platform.isIOS) {
      // iOS Simulator
      return true;
    }
    return false;
  }
}

