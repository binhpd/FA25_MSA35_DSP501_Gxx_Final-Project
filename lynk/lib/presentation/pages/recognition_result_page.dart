import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../domain/entities/song.dart';

class RecognitionResultPage extends StatelessWidget {
  final Song song;
  final double confidence;
  final int matches;

  const RecognitionResultPage({
    super.key,
    required this.song,
    required this.confidence,
    required this.matches,
  });

  Future<void> _openSpotify() async {
    if (song.spotifyUrl != null && song.spotifyUrl!.isNotEmpty) {
      final uri = Uri.parse(song.spotifyUrl!);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    }
  }

  Future<void> _openYouTube() async {
    if (song.youtubeUrl != null && song.youtubeUrl!.isNotEmpty) {
      final uri = Uri.parse(song.youtubeUrl!);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        // Fallback: Search on YouTube
        final searchUri = Uri.parse(
          'https://www.youtube.com/results?search_query=${Uri.encodeComponent('${song.title} ${song.artist}')}',
        );
        if (await canLaunchUrl(searchUri)) {
          await launchUrl(searchUri, mode: LaunchMode.externalApplication);
        }
      }
    } else {
      // Search on YouTube if no URL
      final searchUri = Uri.parse(
        'https://www.youtube.com/results?search_query=${Uri.encodeComponent('${song.title} ${song.artist}')}',
      );
      if (await canLaunchUrl(searchUri)) {
        await launchUrl(searchUri, mode: LaunchMode.externalApplication);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Kết quả nhận diện'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const SizedBox(height: 32),
            // Success Icon với animation
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0.0, end: 1.0),
              duration: const Duration(milliseconds: 800),
              curve: Curves.easeOut,
              builder: (context, value, child) {
                return Transform.scale(
                  scale: value,
                  child: Opacity(
                    opacity: value,
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.green.withOpacity(0.1),
                      ),
                      child: const Icon(
                        Icons.check_circle,
                        size: 80,
                        color: Colors.green,
                      ),
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 32),
            // Song Title
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0.0, end: 1.0),
              duration: const Duration(milliseconds: 600),
              curve: Curves.easeOut,
              builder: (context, value, child) {
                return Opacity(
                  opacity: value,
                  child: Transform.translate(
                    offset: Offset(0, 20 * (1 - value)),
                    child: Text(
                      song.title,
                      style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.deepPurple,
                          ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 16),
            // Artist
            TweenAnimationBuilder<double>(
              tween: Tween(begin: 0.0, end: 1.0),
              duration: const Duration(milliseconds: 800),
              curve: Curves.easeOut,
              builder: (context, value, child) {
                return Opacity(
                  opacity: value,
                  child: Transform.translate(
                    offset: Offset(0, 20 * (1 - value)),
                    child: Text(
                      song.artist,
                      style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            color: Colors.grey[600],
                          ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              },
            ),
            if (song.album != null) ...[
              const SizedBox(height: 8),
              Text(
                song.album!,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.grey[500],
                    ),
                textAlign: TextAlign.center,
              ),
            ],
            const SizedBox(height: 32),
            // Confidence Card
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  children: [
                      Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.analytics,
                          color: Colors.deepPurple,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'Độ chính xác',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Text(
                      '${confidence.toStringAsFixed(1)}%',
                      style: Theme.of(context).textTheme.displayMedium?.copyWith(
                            color: Colors.deepPurple,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '$matches matches',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: Colors.grey[600],
                          ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            // Action Buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: _openSpotify,
                  icon: const Icon(Icons.music_note),
                  label: const Text('Spotify'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 16,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                ElevatedButton.icon(
                  onPressed: _openYouTube,
                  icon: const Icon(Icons.play_circle),
                  label: const Text('YouTube'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 16,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 32),
            // Recognition Time
            if (song.recognizedAt != null)
              Text(
                'Nhận diện lúc: ${_formatDateTime(song.recognizedAt!)}',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: Colors.grey[500],
                    ),
              ),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:'
        '${dateTime.minute.toString().padLeft(2, '0')}:'
        '${dateTime.second.toString().padLeft(2, '0')} '
        '${dateTime.day}/${dateTime.month}/${dateTime.year}';
  }
}

