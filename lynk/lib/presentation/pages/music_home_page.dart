import 'dart:async';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import '../providers/music_provider.dart';
import 'recognition_result_page.dart';

class MusicHomePage extends StatefulWidget {
  const MusicHomePage({super.key});

  @override
  State<MusicHomePage> createState() => _MusicHomePageState();
}

class _MusicHomePageState extends State<MusicHomePage>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;
  final AudioRecorder _audioRecorder = AudioRecorder();
  Timer? _recordingTimer;
  String? _recordingPath;

  @override
  void initState() {
    super.initState();
    _setupAnimation();
  }

  void _setupAnimation() {
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1000),
    );

    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 1.2,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));

    _animationController.repeat(reverse: true);
  }

  Future<String> _getRecordingPath() async {
    final directory = await getApplicationDocumentsDirectory();
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return '${directory.path}/recording_$timestamp.m4a';
  }

  Future<void> _startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final path = await _getRecordingPath();
        await _audioRecorder.start(
          const RecordConfig(
            encoder: AudioEncoder.aacLc,
            bitRate: 128000,
            sampleRate: 44100,
          ),
          path: path,
        );

        if (!mounted) return;

        _recordingPath = path;
        final musicProvider = context.read<MusicProvider>();
        musicProvider.startRecording(path);

        // Start timer to update duration
        _recordingTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
          if (mounted) {
            musicProvider.updateRecordingDuration(timer.tick);
          }
        });

        // Auto stop after 10 seconds
        Timer(const Duration(seconds: 10), () {
          if (mounted) {
            _stopRecording();
          }
        });
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Cần quyền truy cập microphone để ghi âm'),
            ),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Lỗi khi ghi âm: $e')),
        );
      }
    }
  }

  Future<void> _stopRecording() async {
    try {
      await _audioRecorder.stop();
      _recordingTimer?.cancel();
      _recordingTimer = null;

      if (_recordingPath != null && mounted) {
        final musicProvider = context.read<MusicProvider>();
        await musicProvider.stopRecording();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Lỗi khi dừng ghi âm: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    _recordingTimer?.cancel();
    _audioRecorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nhận diện bài hát'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: Consumer<MusicProvider>(
        builder: (context, musicProvider, child) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Recording status text
                if (musicProvider.isRecording)
                  Column(
                    children: [
                      Text(
                        'Đang ghi âm...',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '${musicProvider.recordingDuration}s / 10s',
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 32),
                    ],
                  )
                else if (musicProvider.isProcessing)
                  Column(
                    children: [
                      const CircularProgressIndicator(),
                      const SizedBox(height: 16),
                      Text(
                        'Đang phân tích...',
                        style: Theme.of(context).textTheme.headlineSmall,
                      ),
                      const SizedBox(height: 32),
                    ],
                  )
                else if (musicProvider.error != null)
                  Column(
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 48,
                        color: Colors.red,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        musicProvider.error!,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 32),
                    ],
                  )
                else if (musicProvider.isCompleted &&
                    musicProvider.recognizedSong != null)
                  Column(
                    children: [
                      const Icon(
                        Icons.check_circle,
                        size: 48,
                        color: Colors.green,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'Đã nhận diện thành công!',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => RecognitionResultPage(
                                song: musicProvider.recognizedSong!,
                                confidence: musicProvider.confidence,
                                matches: musicProvider.matches,
                              ),
                            ),
                          );
                        },
                        icon: const Icon(Icons.visibility),
                        label: const Text('Xem chi tiết'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurple,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 16,
                          ),
                        ),
                      ),
                      const SizedBox(height: 32),
                    ],
                  ),

                // Record button with animation
                GestureDetector(
                  onTap: musicProvider.isRecording
                      ? _stopRecording
                      : musicProvider.isProcessing
                          ? null
                          : _startRecording,
                  child: AnimatedBuilder(
                    animation: _scaleAnimation,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: musicProvider.isRecording
                            ? _scaleAnimation.value
                            : 1.0,
                        child: Container(
                          width: 200,
                          height: 200,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: musicProvider.isRecording
                                ? Colors.red
                                : Colors.deepPurple,
                            boxShadow: [
                              BoxShadow(
                                color: (musicProvider.isRecording
                                        ? Colors.red
                                        : Colors.deepPurple)
                                    .withOpacity(0.5),
                                blurRadius: musicProvider.isRecording ? 30 : 20,
                                spreadRadius:
                                    musicProvider.isRecording ? 10 : 5,
                              ),
                            ],
                          ),
                          child: Icon(
                            musicProvider.isRecording ? Icons.stop : Icons.mic,
                            size: 80,
                            color: Colors.white,
                          ),
                        ),
                      );
                    },
                  ),
                ),

                const SizedBox(height: 32),

                // Waveform visualization (simplified)
                if (musicProvider.isRecording) _buildWaveformVisualizer(),

                const SizedBox(height: 32),

                // Reset button
                if (musicProvider.isCompleted || musicProvider.error != null)
                  ElevatedButton.icon(
                    onPressed: () {
                      musicProvider.reset();
                    },
                    icon: const Icon(Icons.refresh),
                    label: const Text('Thử lại'),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildWaveformVisualizer() {
    return SizedBox(
      height: 100,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: List.generate(
          20,
          (index) => AnimatedBuilder(
            animation: _animationController,
            builder: (context, child) {
              final delay = index * 0.1;
              final animationValue = (_animationController.value + delay) % 1.0;
              final height = 20 + (animationValue * 60);
              return Container(
                width: 4,
                height: height,
                margin: const EdgeInsets.symmetric(horizontal: 2),
                decoration: BoxDecoration(
                  color: Colors.deepPurple,
                  borderRadius: BorderRadius.circular(2),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}
