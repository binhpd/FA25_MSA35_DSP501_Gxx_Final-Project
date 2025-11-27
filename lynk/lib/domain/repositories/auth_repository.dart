import '../entities/user.dart';

abstract class AuthRepository {
  Future<User> login(String username, String password);
  Future<void> logout();
  Future<bool> isLoggedIn();
  Future<User?> getCurrentUser();
}
