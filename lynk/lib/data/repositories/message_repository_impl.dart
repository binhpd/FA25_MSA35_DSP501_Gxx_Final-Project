import 'dart:async';

import '../../domain/entities/message.dart';
import '../../domain/repositories/message_repository.dart';

class MessageRepositoryImpl implements MessageRepository {
  // No longer needs a data source
  MessageRepositoryImpl();

  @override
  Future<Message> getHelloMessage() async {
    try {
      // Logic from datasource is now here
      // Simulate API call delay
      await Future.delayed(const Duration(milliseconds: 500));
      const messageContent = 'Hello World from Clean Architecture!';

      return Message(
        content: messageContent,
        timestamp: DateTime.now(),
      );
    } catch (e) {
      throw Exception('Failed to get hello message: $e');
    }
  }
}
