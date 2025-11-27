class Song {
  final String id;
  final String title;
  final String artist;
  final String? album;
  final String? coverImageUrl;
  final String? spotifyUrl;
  final String? youtubeUrl;
  final DateTime? recognizedAt;

  const Song({
    required this.id,
    required this.title,
    required this.artist,
    this.album,
    this.coverImageUrl,
    this.spotifyUrl,
    this.youtubeUrl,
    this.recognizedAt,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Song &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          title == other.title &&
          artist == other.artist;

  @override
  int get hashCode => id.hashCode ^ title.hashCode ^ artist.hashCode;

  @override
  String toString() =>
      'Song(id: $id, title: $title, artist: $artist, album: $album)';
}





