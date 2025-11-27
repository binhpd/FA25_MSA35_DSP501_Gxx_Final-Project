import 'dart:async';
import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_local_datasource.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthLocalDataSource localDataSource;

  // No longer needs remote data source
  AuthRepositoryImpl(this.localDataSource);

  // Fixed credentials for demo
  static const String _validUsername = 'admin';
  static const String _validPassword = 'password123';

  @override
  Future<User> login(String username, String password) async {
    try {
      // Logic from remote data source is now here
      await Future.delayed(const Duration(milliseconds: 500));

      if (username == _validUsername && password == _validPassword) {
        final user = User(
          username: username,
          email: '$username@example.com',
        );

        // Save user to local storage
        await localDataSource.saveUser(user.username, user.email);

        return user;
      } else {
        throw Exception('Invalid username or password');
      }
    } catch (e) {
      throw Exception('Login failed: $e');
    }
  }

  @override
  Future<void> logout() async {
    await localDataSource.clearUser();
  }

  @override
  Future<bool> isLoggedIn() async {
    return await localDataSource.hasUser();
  }

  @override
  Future<User?> getCurrentUser() async {
    final username = await localDataSource.getUsername();
    final email = await localDataSource.getEmail();
    if (username != null && email != null) {
      return User(
        username: username,
        email: email,
      );
    }
    return null;
  }
}
