import 'package:flutter/foundation.dart';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';

class AuthProvider extends ChangeNotifier {
  final AuthRepository authRepository;

  AuthProvider(this.authRepository);

  User? _user;
  bool _isLoading = false;
  bool _isAuthenticated = false;
  String? _error;

  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;

  Future<void> checkAuth() async {
    _isLoading = true;
    notifyListeners();

    try {
      _isAuthenticated = await authRepository.isLoggedIn();
      if (_isAuthenticated) {
        // Load user data when authenticated
        final user = await authRepository.getCurrentUser();
        if (user != null) {
          _user = user;
        }
      } else {
        _user = null;
      }
      _error = null;
    } catch (e) {
      _error = e.toString();
      _isAuthenticated = false;
      _user = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _user = await authRepository.login(username, password);
      _isAuthenticated = true;
      _error = null;
      return true;
    } catch (e) {
      _error = e.toString();
      _user = null;
      _isAuthenticated = false;
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await authRepository.logout();
      _user = null;
      _isAuthenticated = false;
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
