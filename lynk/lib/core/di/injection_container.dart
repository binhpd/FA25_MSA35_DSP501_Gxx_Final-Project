import 'package:provider/provider.dart';
import '../../data/repositories/message_repository_impl.dart';
import '../../domain/repositories/message_repository.dart';
import '../../presentation/providers/message_provider.dart';
import '../../data/datasources/auth_local_datasource.dart';
import '../../data/repositories/auth_repository_impl.dart';
import '../../domain/repositories/auth_repository.dart';
import '../../presentation/providers/auth_provider.dart';
import 'package:dio/dio.dart';
import '../../core/constants/api_constants.dart';
import '../../data/datasources/music_remote_datasource.dart';
import '../../data/repositories/music_repository_impl.dart';
import '../../domain/repositories/music_repository.dart';
import '../../presentation/providers/music_provider.dart';
import '../../presentation/providers/permission_provider.dart';

class InjectionContainer {
  static get providers => [
        // Message
        Provider<MessageRepository>(
          create: (_) => MessageRepositoryImpl(),
        ),
        ChangeNotifierProvider<MessageProvider>(
          create: (context) => MessageProvider(
            context.read<MessageRepository>(),
          ),
        ),

        // Auth Data Sources
        Provider<AuthLocalDataSource>(
          create: (_) => AuthLocalDataSourceImpl(),
        ),

        // Auth Repositories
        Provider<AuthRepository>(
          create: (context) => AuthRepositoryImpl(
            context.read<AuthLocalDataSource>(),
          ),
        ),

        // Auth Providers
        ChangeNotifierProvider<AuthProvider>(
          create: (context) => AuthProvider(
            context.read<AuthRepository>(),
          ),
        ),

        // Music Data Sources
        Provider<Dio>(
          create: (_) => Dio(
            BaseOptions(
              baseUrl: ApiConstants.baseUrl,
              connectTimeout: const Duration(seconds: 30),
              receiveTimeout: const Duration(seconds: 30),
              headers: {
                'Accept': 'application/json',
              },
            ),
          ),
        ),
        Provider<MusicRemoteDataSource>(
          create: (context) => MusicRemoteDataSource(
            context.read<Dio>(),
          ),
        ),

        // Music Repositories
        Provider<MusicRepository>(
          create: (context) => MusicRepositoryImpl(
            context.read<MusicRemoteDataSource>(),
          ),
        ),

        // Music Providers
        ChangeNotifierProvider<MusicProvider>(
          create: (context) => MusicProvider(
            context.read<MusicRepository>(),
          ),
        ),
        ChangeNotifierProvider<PermissionProvider>(
          create: (_) => PermissionProvider(),
        ),
      ];
}
