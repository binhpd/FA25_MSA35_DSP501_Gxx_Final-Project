"""
Lynk Desktop - Music Recognition Desktop Application
Python desktop app for recording audio and recognizing songs
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
from datetime import datetime
from audio_recorder import AudioRecorder
from api_client import APIClient
import config


class MusicRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lynk - Nhận diện bài hát")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Configure style
        self.setup_style()
        
        # Initialize components
        self.recorder = AudioRecorder()
        self.api_client = APIClient(base_url=config.BASE_URL)
        
        # State variables
        self.is_recording = False
        self.recording_duration = 0
        self.recording_timer = None
        self.current_result = None
        
        # Create UI
        self.create_ui()
        
        # Center window
        self.center_window()
    
    def setup_style(self):
        """Setup modern UI style"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors from config
        self.bg_color = config.BG_COLOR
        self.primary_color = config.PRIMARY_COLOR
        self.success_color = config.SUCCESS_COLOR
        self.error_color = config.ERROR_COLOR
        self.accent_color = config.ACCENT_COLOR
        
        self.root.configure(bg=self.bg_color)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_ui(self):
        """Create the user interface"""
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🎵 Lynk - Nhận diện bài hát",
            font=("Arial", 24, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Recording section
        self.create_recording_section(content_frame)
        
        # Result section (initially hidden)
        self.create_result_section(content_frame)
        
        # Status bar
        self.create_status_bar()
    
    def create_recording_section(self, parent):
        """Create recording controls section"""
        recording_frame = tk.Frame(parent, bg=self.bg_color)
        recording_frame.pack(fill=tk.X, pady=20)
        
        # Instructions
        instruction_label = tk.Label(
            recording_frame,
            text="Nhấn nút bên dưới để bắt đầu ghi âm (10 giây)",
            font=("Arial", 12),
            bg=self.bg_color,
            fg="#666"
        )
        instruction_label.pack(pady=10)
        
        # Recording button (circular)
        button_frame = tk.Frame(recording_frame, bg=self.bg_color)
        button_frame.pack(pady=30)
        
        self.record_button = tk.Button(
            button_frame,
            text="🎤\nGhi âm",
            font=("Arial", 16, "bold"),
            bg=self.primary_color,
            fg="black",
            width=15,
            height=4,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.toggle_recording
        )
        self.record_button.pack()
        
        # Duration label
        self.duration_label = tk.Label(
            recording_frame,
            text="00:00",
            font=("Arial", 32, "bold"),
            bg=self.bg_color,
            fg=self.primary_color
        )
        self.duration_label.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(
            recording_frame,
            text="Sẵn sàng",
            font=("Arial", 14),
            bg=self.bg_color,
            fg="#666"
        )
        self.status_label.pack(pady=10)
    
    def create_result_section(self, parent):
        """Create result display section"""
        self.result_frame = tk.Frame(parent, bg="white", relief=tk.RAISED, bd=2)
        self.result_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        self.result_frame.pack_forget()  # Initially hidden
        
        # Result content
        result_content = tk.Frame(self.result_frame, bg="white")
        result_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Success icon (placeholder)
        self.result_icon = tk.Label(
            result_content,
            text="✓",
            font=("Arial", 60, "bold"),
            bg="white",
            fg=self.success_color
        )
        self.result_icon.pack(pady=10)
        
        # Song name
        self.song_name_label = tk.Label(
            result_content,
            text="",
            font=("Arial", 20, "bold"),
            bg="white",
            fg=self.primary_color,
            wraplength=500
        )
        self.song_name_label.pack(pady=10)
        
        # Confidence card
        confidence_frame = tk.Frame(result_content, bg="#f0f0f0", relief=tk.RAISED, bd=1)
        confidence_frame.pack(fill=tk.X, pady=20, padx=20)
        
        confidence_title = tk.Label(
            confidence_frame,
            text="Độ chính xác",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#666"
        )
        confidence_title.pack(pady=10)
        
        self.confidence_label = tk.Label(
            confidence_frame,
            text="0%",
            font=("Arial", 32, "bold"),
            bg="#f0f0f0",
            fg=self.primary_color
        )
        self.confidence_label.pack()
        
        self.matches_label = tk.Label(
            confidence_frame,
            text="0 matches",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666"
        )
        self.matches_label.pack(pady=5, padx=10)
        
        # Action buttons
        button_frame = tk.Frame(result_content, bg="white")
        button_frame.pack(pady=20)
        
        self.record_again_button = tk.Button(
            button_frame,
            text="Ghi âm lại",
            font=("Arial", 12, "bold"),
            bg=self.primary_color,
            fg="white",
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.reset_ui
        )
        self.record_again_button.pack(side=tk.LEFT, padx=10)
    
    def create_status_bar(self):
        """Create status bar at bottom"""
        status_frame = tk.Frame(self.root, bg="#e0e0e0", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        self.status_bar_label = tk.Label(
            status_frame,
            text=f"Kết nối: {config.BASE_URL}",
            font=("Arial", 9),
            bg="#e0e0e0",
            fg="#666",
            anchor=tk.W
        )
        self.status_bar_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    def toggle_recording(self):
        """Start or stop recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Start audio recording"""
        try:
            self.is_recording = True
            self.recording_duration = 0
            self.recording_timer = 0
            
            # Update UI
            self.record_button.config(
                text="⏹\nDừng",
                bg=self.error_color,
                state=tk.NORMAL
            )
            self.status_label.config(text="Đang ghi âm...", fg=self.error_color)
            self.duration_label.config(text="00:00")
            
            # Hide result if visible
            self.result_frame.pack_forget()
            
            # Start recording in a separate thread
            recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            recording_thread.start()
            
            # Start timer
            self.update_timer()
            
        except Exception as e:
            error_msg = str(e)
            detailed_msg = f"Không thể bắt đầu ghi âm: {error_msg}\n\n"
            detailed_msg += "💡 Hướng dẫn:\n"
            detailed_msg += "1. Kiểm tra quyền truy cập microphone trong System Settings > Privacy & Security > Microphone\n"
            detailed_msg += "2. Đảm bảo không có ứng dụng khác đang sử dụng microphone\n"
            detailed_msg += "3. Thử khởi động lại ứng dụng"
            messagebox.showerror("Lỗi", detailed_msg)
            self.is_recording = False
    
    def _record_audio(self):
        """Record audio in background thread"""
        try:
            # Record for configured duration
            output_file = self.recorder.record(duration=config.RECORDING_DURATION)
            
            if output_file and os.path.exists(output_file):
                # Auto-stop after recording
                self.root.after(0, lambda: self.stop_recording_and_recognize(output_file))
            else:
                error_msg = "Không thể ghi âm. Vui lòng kiểm tra microphone.\n\n"
                error_msg += "💡 Hướng dẫn:\n"
                error_msg += "1. Kiểm tra quyền truy cập microphone trong System Settings\n"
                error_msg += "2. Đảm bảo microphone đang hoạt động\n"
                error_msg += "3. Thử khởi động lại ứng dụng"
                self.root.after(0, lambda: messagebox.showerror("Lỗi", error_msg))
                self.root.after(0, self.reset_recording_state)
                
        except Exception as e:
            error_msg = str(e)  # Capture error message
            self.root.after(0, lambda msg=error_msg: messagebox.showerror(
                "Lỗi", f"Lỗi khi ghi âm: {msg}"
            ))
            self.root.after(0, self.reset_recording_state)
    
    def update_timer(self):
        """Update recording duration timer"""
        if self.is_recording:
            minutes = self.recording_timer // 60
            seconds = self.recording_timer % 60
            self.duration_label.config(
                text=f"{minutes:02d}:{seconds:02d}"
            )
            
            # Stop at configured duration
            if self.recording_timer >= config.RECORDING_DURATION:
                return
            
            self.recording_timer += 1
            
            # Schedule next update
            self.root.after(1000, self.update_timer)
    
    def stop_recording(self):
        """Stop recording manually"""
        if self.is_recording:
            self.recorder.stop()
            self.is_recording = False
    
    def stop_recording_and_recognize(self, audio_file):
        """Stop recording and start recognition"""
        self.is_recording = False
        
        # Update UI - show final duration
        minutes = config.RECORDING_DURATION // 60
        seconds = config.RECORDING_DURATION % 60
        self.duration_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Update UI - disable button and show processing state
        self.record_button.config(
            text="🎤\nGhi âm",
            bg=self.primary_color,
            state=tk.DISABLED
        )
        self.status_label.config(text="Đang xử lý...", fg=self.accent_color)
        
        # Force UI update
        self.root.update_idletasks()
        
        # Start recognition in background thread
        recognition_thread = threading.Thread(
            target=self._recognize_song,
            args=(audio_file,),
            daemon=True
        )
        recognition_thread.start()
        
        # Start progress indicator
        self._show_progress_indicator()
    
    def _show_progress_indicator(self):
        """Show animated progress indicator"""
        if hasattr(self, '_progress_dots'):
            self._progress_dots = 0
        else:
            self._progress_dots = 0
        
        def update_progress():
            if hasattr(self, 'is_processing') and self.is_processing:
                dots = "." * (self._progress_dots % 4)
                try:
                    self.status_label.config(text=f"Đang xử lý{dots}", fg=self.accent_color)
                    self._progress_dots += 1
                    self.root.after(500, update_progress)
                except:
                    pass  # UI might be destroyed
        
        self.is_processing = True
        update_progress()
    
    def _stop_progress_indicator(self):
        """Stop progress indicator"""
        self.is_processing = False
    
    def _recognize_song(self, audio_file):
        """Recognize song in background thread"""
        try:
            # Update status in UI thread
            self.root.after(0, lambda: self.status_label.config(
                text="Đang upload file...", 
                fg=self.accent_color
            ))
            
            result = self.api_client.recognize_song(audio_file)
            
            # Stop progress indicator
            self.root.after(0, self._stop_progress_indicator)
            
            if result is None:
                # Connection or other critical error
                error_msg = "Không thể kết nối đến server.\n\n"
                error_msg += "💡 Hướng dẫn:\n"
                error_msg += "1. Kiểm tra backend server có đang chạy không\n"
                error_msg += "2. Kiểm tra kết nối mạng\n"
                error_msg += "3. Thử khởi động lại server"
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Lỗi kết nối", msg))
                self.root.after(0, self.reset_recording_state)
                return
            elif result.get('error', False):
                # Server returned an error (500, 400, etc.)
                status_code = result.get('status_code', 0)
                error_message = result.get('message', 'Lỗi không xác định')
                detail = result.get('detail', '')
                
                # Build detailed error message
                error_msg = f"{error_message}\n\n"
                
                if status_code == 500:
                    error_msg += "⚠️ Lỗi server (500 Internal Server Error)\n\n"
                    error_msg += "💡 Có thể do:\n"
                    error_msg += "1. File audio không hợp lệ hoặc bị hỏng\n"
                    error_msg += "2. Server đang gặp sự cố\n"
                    error_msg += "3. Database có vấn đề\n\n"
                    error_msg += "Vui lòng thử lại sau hoặc kiểm tra logs server."
                elif status_code == 400:
                    error_msg += "⚠️ Lỗi yêu cầu (400 Bad Request)\n\n"
                    error_msg += "File audio có thể không đúng định dạng hoặc quá lớn."
                elif status_code == 404:
                    error_msg += "⚠️ Không tìm thấy endpoint (404 Not Found)\n\n"
                    error_msg += "💡 Có thể do:\n"
                    error_msg += "1. Backend server không có endpoint '/recognize'\n"
                    error_msg += "2. URL server không đúng trong config.py\n"
                    error_msg += "3. Backend server đang chạy version cũ\n\n"
                    error_msg += "Vui lòng kiểm tra:\n"
                    error_msg += f"- Server URL: {config.BASE_URL}\n"
                    error_msg += "- Endpoint: {config.BASE_URL}/recognize\n"
                    error_msg += "- Backend server logs"
                else:
                    error_msg += f"⚠️ Lỗi server (Status: {status_code})\n\n"
                    error_msg += "Vui lòng thử lại sau."
                
                # Show error dialog
                self.root.after(0, lambda msg=error_msg: messagebox.showerror("Lỗi nhận diện", msg))
                self.root.after(0, self.reset_recording_state)
            elif result.get('success', False):
                # Success - display result
                self.current_result = result
                # Use lambda with captured variable to avoid closure issues
                def show_result(res=result):
                    try:
                        self.display_result(res)
                    except Exception as e:
                        print(f"Error displaying result: {e}")
                        messagebox.showerror("Lỗi", f"Lỗi hiển thị kết quả: {str(e)}")
                        self.reset_recording_state()
                self.root.after(0, show_result)
            else:
                # No match found (success=False but no error)
                self.root.after(0, lambda: messagebox.showwarning(
                    "Không tìm thấy",
                    "Không thể nhận diện bài hát.\n\n"
                    "💡 Có thể do:\n"
                    "1. Bài hát chưa có trong database\n"
                    "2. Chất lượng ghi âm không đủ tốt\n"
                    "3. Thời gian ghi âm quá ngắn\n\n"
                    "Vui lòng thử lại với âm thanh rõ hơn."
                ))
                self.root.after(0, self.reset_recording_state)
                
        except Exception as e:
            # Stop progress indicator
            self.root.after(0, self._stop_progress_indicator)
            
            error_msg = f"Lỗi không xác định khi nhận diện: {str(e)}\n\n"
            error_msg += "Vui lòng thử lại hoặc kiểm tra logs."
            import traceback
            print(f"❌ Exception in _recognize_song: {traceback.format_exc()}")
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("Lỗi", msg))
            self.root.after(0, self.reset_recording_state)
    
    def display_result(self, result):
        """Display recognition result"""
        try:
            # Stop progress indicator
            self._stop_progress_indicator()
            
            # Safely extract data from result
            song_name = result.get('song', 'Không xác định') if result else 'Không xác định'
            confidence = result.get('confidence', 0.0) if result else 0.0
            matches = result.get('matches', 0) if result else 0
            
            # Update result labels safely
            try:
                self.song_name_label.config(text=str(song_name))
                self.confidence_label.config(text=f"{float(confidence):.1f}%")
                self.matches_label.config(text=f"{int(matches)} matches")
            except Exception as label_error:
                print(f"⚠️ Error updating labels: {label_error}")
                # Set default values
                self.song_name_label.config(text="Không xác định")
                self.confidence_label.config(text="0.0%")
                self.matches_label.config(text="0 matches")
            
            # Show result frame
            try:
                self.result_frame.pack(fill=tk.BOTH, expand=True, pady=20)
            except Exception as frame_error:
                print(f"⚠️ Error showing result frame: {frame_error}")
            
            # Update status
            try:
                self.status_label.config(
                    text=f"Đã nhận diện: {song_name}",
                    fg=self.success_color
                )
            except Exception as status_error:
                print(f"⚠️ Error updating status: {status_error}")
            
            # Re-enable record button
            try:
                self.record_button.config(state=tk.NORMAL)
            except Exception as button_error:
                print(f"⚠️ Error enabling button: {button_error}")
            
            # Force UI update to ensure everything is displayed
            self.root.update_idletasks()
            
        except Exception as e:
            print(f"❌ Error in display_result: {e}")
            import traceback
            print(traceback.format_exc())
            # Show error and reset
            messagebox.showerror("Lỗi", f"Lỗi hiển thị kết quả: {str(e)}")
            self.reset_recording_state()
    
    def reset_recording_state(self):
        """Reset recording state"""
        self.is_recording = False
        self.recording_timer = 0
        self._stop_progress_indicator()
        try:
            self.record_button.config(
                text="🎤\nGhi âm",
                bg=self.primary_color,
                state=tk.NORMAL
            )
            self.status_label.config(text="Sẵn sàng", fg="#666")
            self.duration_label.config(text="00:00")
            # Force UI update
            self.root.update_idletasks()
        except Exception as e:
            # Handle case where UI might be destroyed
            print(f"⚠️ Warning: Could not update UI state: {e}")
    
    def reset_ui(self):
        """Reset UI to initial state"""
        self.result_frame.pack_forget()
        self.reset_recording_state()
        self.current_result = None


def main():
    """Main entry point"""
    root = tk.Tk()
    app = MusicRecognitionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

