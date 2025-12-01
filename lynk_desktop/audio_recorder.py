"""
Audio Recorder Module
Handles audio recording functionality
"""

import pyaudio
import wave
import os
import tempfile
from datetime import datetime
import config


class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.frames = []
        self.stream = None
        
        # Audio settings from config (matching Flutter app: 44100 Hz, 16-bit)
        self.sample_rate = config.SAMPLE_RATE
        self.channels = config.CHANNELS
        self.chunk = config.CHUNK_SIZE
        self.format = pyaudio.paInt16
        self.sample_width = 2  # 16-bit = 2 bytes
    
    def _get_default_input_device(self):
        """Get default input device index"""
        try:
            # Try to find default input device
            default_device = self.audio.get_default_input_device_info()
            return default_device['index']
        except:
            # Fallback: try to find any input device
            try:
                for i in range(self.audio.get_device_count()):
                    device_info = self.audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        return i
            except:
                pass
            return None
    
    def record(self, duration=10):
        """
        Record audio for specified duration
        
        Args:
            duration: Recording duration in seconds (default: 10)
            
        Returns:
            Path to saved audio file (WAV format)
        """
        try:
            # Create temporary file for recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = tempfile.gettempdir()
            output_file = os.path.join(temp_dir, f"lynk_recording_{timestamp}.wav")
            
            # Initialize recording
            self.is_recording = True
            self.frames = []
            
            # Get input device
            input_device = self._get_default_input_device()
            
            # Open audio stream with device selection
            stream_params = {
                'format': self.format,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'frames_per_buffer': self.chunk,
                'input_device_index': input_device,
            }
            
            # Try with device first, fallback to default
            try:
                self.stream = self.audio.open(**stream_params)
            except Exception as e1:
                print(f"⚠️ Warning: Could not open with specific device: {e1}")
                # Try without specifying device
                stream_params.pop('input_device_index', None)
                try:
                    self.stream = self.audio.open(**stream_params)
                except Exception as e2:
                    print(f"❌ Error: Could not open audio stream: {e2}")
                    raise Exception(f"Không thể mở microphone. Vui lòng kiểm tra quyền truy cập microphone và đảm bảo microphone đang hoạt động. Chi tiết: {str(e2)}")
            
            # Record audio
            print(f"🎤 Recording for {duration} seconds...")
            for _ in range(0, int(self.sample_rate / self.chunk * duration)):
                if not self.is_recording:
                    break
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            
            # Stop and close stream
            self.stop()
            
            # Save to WAV file
            self._save_wav(output_file)
            
            print(f"✅ Recording saved to: {output_file}")
            return output_file
            
        except OSError as e:
            error_code = e.errno if hasattr(e, 'errno') else None
            if error_code == -9986:
                # Internal PortAudio error - usually permission or device issue
                error_msg = "Lỗi truy cập microphone. Vui lòng:\n1. Kiểm tra quyền truy cập microphone trong System Settings\n2. Đảm bảo không có ứng dụng khác đang sử dụng microphone\n3. Thử khởi động lại ứng dụng"
            else:
                error_msg = f"Lỗi ghi âm: {str(e)}"
            print(f"❌ Error recording audio: {error_msg}")
            self.stop()
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Lỗi không xác định khi ghi âm: {str(e)}"
            print(f"❌ Error recording audio: {error_msg}")
            self.stop()
            raise Exception(error_msg)
    
    def stop(self):
        """Stop recording"""
        self.is_recording = False
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None
    
    def _save_wav(self, filename):
        """Save recorded frames to WAV file"""
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
        except Exception as e:
            print(f"❌ Error saving WAV file: {str(e)}")
            raise
    
    def __del__(self):
        """Cleanup on deletion"""
        self.stop()
        try:
            self.audio.terminate()
        except:
            pass

