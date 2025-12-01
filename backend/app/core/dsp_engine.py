"""
DSP Engine for Audio Fingerprinting
Implements Avery Wang's Algorithm for Shazam-like music recognition
"""

import numpy as np
import soundfile as sf
from scipy.ndimage import maximum_filter
from scipy.signal import resample
import logging

# Setup logging
logger = logging.getLogger(__name__)


class AudioFingerprinter:
    """
    Audio Fingerprinting Engine using Spectrogram Peaks and Combinatorial Hashing
    """
    
    def __init__(self, 
                 sample_rate: int = 22050,
                 n_fft: int = 4096,
                 hop_length: int = 1024,
                 peak_neighborhood_size: int = 20,
                 target_zone_t_min: int = 1,
                 target_zone_t_max: int = 5):
        """
        Initialize the Audio Fingerprinter
        
        Args:
            sample_rate: Target sample rate (22050 Hz for optimal balance)
            n_fft: FFT window size (4096 for ~5Hz frequency resolution)
            hop_length: Hop length for STFT (1024 = 75% overlap)
            peak_neighborhood_size: Size of neighborhood for peak detection (20x20)
            target_zone_t_min: Minimum time offset for target zone (seconds)
            target_zone_t_max: Maximum time offset for target zone (seconds)
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.peak_neighborhood_size = peak_neighborhood_size
        self.target_zone_t_min = target_zone_t_min
        self.target_zone_t_max = target_zone_t_max
        
        # Convert time window to bins
        self.target_zone_bin_min = int(self.target_zone_t_min * self.sample_rate / self.hop_length)
        self.target_zone_bin_max = int(self.target_zone_t_max * self.sample_rate / self.hop_length)
    
    def load_audio(self, file_path: str) -> np.ndarray:
        """
        Load audio file and preprocess
        
        Args:
            file_path: Path to audio file (WAV/MP3/M4A/FLAC)
            
        Returns:
            Mono audio signal at target sample rate
        """
        import os
        
        logger.info(f"🎵 [DSP] Loading audio file: {file_path}")
        
        # Determine file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"📄 [DSP] File extension: {file_ext}")
        
        # Use librosa for formats that soundfile doesn't support well (m4a, mp3, aac)
        # Use soundfile for formats it handles well (wav, flac)
        if file_ext in ['.m4a', '.mp3', '.aac', '.mpeg']:
            # Use librosa for compressed formats
            logger.info(f"📚 [DSP] Using librosa for compressed format: {file_ext}")
            try:
                import librosa
                logger.info(f"✅ [DSP] librosa imported successfully")
                # librosa.load automatically converts to mono and handles resampling
                logger.info(f"🔄 [DSP] Loading with librosa (target sr={self.sample_rate}, mono=True)...")
                audio, sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
                logger.info(f"✅ [DSP] Audio loaded: shape={audio.shape}, sample_rate={sr}, duration={len(audio)/sr:.2f}s")
                return audio
            except ImportError as ie:
                logger.error(f"❌ [DSP] librosa not available: {str(ie)}")
                raise ImportError("librosa is required for .m4a/.mp3 files. Install with: pip install librosa")
            except Exception as e:
                logger.error(f"❌ [DSP] librosa load failed: {str(e)}", exc_info=True)
                error_msg = str(e)
                # Check if it's an ffmpeg-related error
                if 'ffmpeg' in error_msg.lower() or 'no suitable backend' in error_msg.lower():
                    raise Exception(
                        f"Failed to load audio file: {error_msg}. "
                        f"For .m4a files, librosa requires ffmpeg. "
                        f"Install with: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)"
                    )
                raise Exception(f"Failed to load audio file with librosa: {error_msg}")
        else:
            # Use soundfile for uncompressed formats (wav, flac, ogg)
            logger.info(f"🔊 [DSP] Using soundfile for uncompressed format: {file_ext}")
            try:
                logger.info(f"🔄 [DSP] Loading with soundfile...")
                audio, sr = sf.read(file_path)
                logger.info(f"✅ [DSP] Audio loaded with soundfile: shape={audio.shape}, sample_rate={sr}")
            except Exception as e:
                logger.warning(f"⚠️ [DSP] soundfile failed: {str(e)}, trying librosa fallback...")
                # Fallback: try librosa if soundfile fails
                try:
                    import librosa
                    logger.info(f"🔄 [DSP] Loading with librosa fallback...")
                    audio, sr = librosa.load(file_path, sr=None, mono=False)
                    logger.info(f"✅ [DSP] Audio loaded with librosa fallback: shape={audio.shape}, sample_rate={sr}")
                except ImportError:
                    logger.error(f"❌ [DSP] librosa not available for fallback")
                    raise ImportError(f"Cannot load audio: soundfile failed ({str(e)}) and librosa not available")
                except Exception as e2:
                    logger.error(f"❌ [DSP] librosa fallback also failed: {str(e2)}")
                    raise Exception(f"Failed to load audio file: soundfile error ({str(e)}), librosa error ({str(e2)})")
        
        # Convert to mono if stereo
        if len(audio.shape) > 1:
            logger.info(f"🔄 [DSP] Converting stereo to mono (shape: {audio.shape})")
            # Average channels to mono
            audio = np.mean(audio, axis=1)
            logger.info(f"✅ [DSP] Converted to mono: shape={audio.shape}")
        
        # Resample to target sample rate
        if sr != self.sample_rate:
            logger.info(f"🔄 [DSP] Resampling from {sr}Hz to {self.sample_rate}Hz")
            # Calculate number of samples for target sample rate
            num_samples = int(len(audio) * self.sample_rate / sr)
            audio = resample(audio, num_samples)
            logger.info(f"✅ [DSP] Resampled: {len(audio)} samples at {self.sample_rate}Hz")
        else:
            logger.info(f"✅ [DSP] No resampling needed (already at {sr}Hz)")
        
        logger.info(f"✅ [DSP] Audio preprocessing complete: shape={audio.shape}, duration={len(audio)/self.sample_rate:.2f}s")
        return audio
    
    def _compute_spectrogram(self, audio: np.ndarray) -> tuple:
        """
        Compute Short-Time Fourier Transform (STFT) spectrogram
        
        Args:
            audio: Mono audio signal
            
        Returns:
            Tuple of (magnitude spectrogram, time bins, frequency bins)
        """
        # Compute STFT using scipy.signal.stft
        from scipy.signal import stft
        
        # Create Hanning window
        window = np.hanning(self.n_fft)
        
        # Compute STFT
        frequencies, times, stft_result = stft(
            audio,
            fs=self.sample_rate,
            window=window,
            nperseg=self.n_fft,
            noverlap=self.n_fft - self.hop_length,
            nfft=self.n_fft,
            return_onesided=True
        )
        
        # Get magnitude spectrogram
        magnitude = np.abs(stft_result)
        
        # scipy.stft returns:
        # - frequencies: array of frequency values (Hz)
        # - times: array of time values (seconds)
        # - stft_result: (frequencies, times) shape
        
        # Note: magnitude shape is (frequencies, times)
        # We need to transpose to match librosa format (frequencies x times)
        # But scipy already returns (freq, time) which is what we want
        
        return magnitude, times, frequencies
    
    def _find_peaks(self, spectrogram: np.ndarray, threshold: float = None) -> list:
        """
        Find local peaks in spectrogram using 2D maximum filter
        
        Args:
            spectrogram: Magnitude spectrogram (2D array)
            threshold: Minimum magnitude threshold (auto if None)
            
        Returns:
            List of (time_idx, freq_idx) tuples for peaks
        """
        # Apply maximum filter
        neighborhood = np.ones((self.peak_neighborhood_size, self.peak_neighborhood_size))
        local_max = maximum_filter(spectrogram, footprint=neighborhood, mode='constant')
        
        # Find points where original equals local max (peaks)
        peaks_mask = (spectrogram == local_max) & (spectrogram > 0)
        
        # Apply threshold (use percentile to filter noise more effectively)
        if threshold is None:
            if peaks_mask.any():
                # Use 75th percentile to filter out weaker peaks (noise)
                threshold = np.percentile(spectrogram[peaks_mask], 75)
            else:
                threshold = 0
        
        peaks_mask = peaks_mask & (spectrogram >= threshold)
        
        # Get peak coordinates
        # np.where returns (row_indices, col_indices)
        # For spectrogram from scipy.stft: shape is (freq, time)
        # So row = freq_idx, col = time_idx
        # But we want (time_idx, freq_idx) to match our usage
        freq_indices, time_indices = np.where(peaks_mask)
        
        peaks = list(zip(time_indices, freq_indices))
        
        return peaks
    
    def generate_fingerprints(self, audio: np.ndarray) -> list:
        """
        Generate audio fingerprints using combinatorial hashing
        
        Args:
            audio: Mono audio signal
            
        Returns:
            List of fingerprints: ((f1, f2, dt), t_absolute)
            where f1, f2 are frequencies, dt is time delta, t_absolute is anchor time
        """
        # Compute spectrogram
        spectrogram, times, frequencies = self._compute_spectrogram(audio)
        
        peaks = self._find_peaks(spectrogram)
        
        fingerprints = []
        
        # For each anchor point
        # peaks are (time_idx, freq_idx) from np.where on spectrogram
        # spectrogram shape from scipy.stft is (freq_bins, time_bins)
        for anchor_time_idx, anchor_freq_idx in peaks:
            # Check bounds
            if anchor_time_idx >= len(times) or anchor_freq_idx >= len(frequencies):
                continue
                
            anchor_time = times[anchor_time_idx]
            anchor_freq = frequencies[anchor_freq_idx]
            

            time_min = anchor_time_idx + self.target_zone_bin_min
            time_max = min(anchor_time_idx + self.target_zone_bin_max, len(times))
            
            # Filter peaks that are in the target zone (more efficient)
            target_peaks = [
                (t_idx, f_idx) for t_idx, f_idx in peaks
                if time_min <= t_idx < time_max 
                and t_idx < len(times) 
                and f_idx < len(frequencies)
            ]
            
            # For each target peak in the zone
            for target_time_idx, target_freq_idx in target_peaks:
                if target_time_idx >= len(times) or target_freq_idx >= len(frequencies):
                    continue
                    
                target_freq = frequencies[target_freq_idx]
                
                # Calculate time delta (in bins)
                dt = target_time_idx - anchor_time_idx
                
                # Create hash: (f1, f2, dt) where dt is time delta in bins
                hash_token = (int(anchor_freq), int(target_freq), int(dt))
                
                # Store: (hash, absolute_time_of_anchor)
                fingerprints.append((hash_token, anchor_time))
        
        return fingerprints
    
    def process_file(self, file_path: str) -> list:
        """
        Process audio file and generate fingerprints
        
        Args:
            file_path: Path to audio file
            
        Returns:
            List of fingerprints
        """
        try:
            audio = self.load_audio(file_path)
            fingerprints = self.generate_fingerprints(audio)
            logger.info(f"[DSP] Generated {len(fingerprints)} fingerprints")
            return fingerprints
        except Exception as e:
            logger.error(f"[DSP] Error processing file {file_path}: {str(e)}", exc_info=True)
            raise

