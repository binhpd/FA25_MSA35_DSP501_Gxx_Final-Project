class Message {
  final String content;
  final DateTime timestamp;

  const Message({
    required this.content,
    required this.timestamp,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Message &&
          runtimeType == other.runtimeType &&
          content == other.content &&
          timestamp == other.timestamp;

  @override
  int get hashCode => content.hashCode ^ timestamp.hashCode;

  @override
  String toString() => 'Message(content: $content, timestamp: $timestamp)';
}
