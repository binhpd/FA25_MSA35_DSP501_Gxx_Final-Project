abstract class AuthLocalDataSource {
  Future<void> saveUser(String username, String email);
  Future<void> clearUser();
  Future<bool> hasUser();
  Future<String?> getUsername();
  Future<String?> getEmail();
}

class AuthLocalDataSourceImpl implements AuthLocalDataSource {
  // Simulate local storage (in real app, use SharedPreferences or similar)
  // Note: This is in-memory storage for demo purposes only
  String? _storedUsername;
  String? _storedEmail;

  @override
  Future<void> saveUser(String username, String email) async {
    _storedUsername = username;
    _storedEmail = email;
  }

  @override
  Future<void> clearUser() async {
    _storedUsername = null;
    _storedEmail = null;
  }

  @override
  Future<bool> hasUser() async {
    return _storedUsername != null && _storedEmail != null;
  }

  @override
  Future<String?> getUsername() async {
    return _storedUsername;
  }

  @override
  Future<String?> getEmail() async {
    return _storedEmail;
  }
}
