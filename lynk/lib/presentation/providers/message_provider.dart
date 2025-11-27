import 'package:flutter/foundation.dart';
import '../../domain/entities/message.dart';
import '../../domain/repositories/message_repository.dart';

class MessageProvider extends ChangeNotifier {
  final MessageRepository messageRepository;

  MessageProvider(this.messageRepository);

  Message? _message;
  bool _isLoading = false;
  String? _error;

  Message? get message => _message;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadMessage() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Call the repository directly
      _message = await messageRepository.getHelloMessage();
      _error = null;
    } catch (e) {
      _error = e.toString();
      _message = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
