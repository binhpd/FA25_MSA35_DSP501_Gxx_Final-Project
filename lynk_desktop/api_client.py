"""
API Client Module
Handles communication with the backend server
"""

import requests
import os
import logging
from typing import Optional, Dict, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the backend server
        """
        self.base_url = base_url.rstrip('/')
        self.recognize_endpoint = f"{self.base_url}/recognize"
    
    def recognize_song(self, audio_file_path: str) -> Optional[Dict]:
        """
        Send audio file to server for recognition
        
        Args:
            audio_file_path: Path to the audio file (WAV format)
            
        Returns:
            Dictionary with recognition result or None if failed
            {
                'success': bool,
                'song': str,
                'confidence': float,
                'matches': int,
                'message': str
            }
        """
        try:
            # Check if file exists
            if not os.path.exists(audio_file_path):
                print(f"❌ Audio file not found: {audio_file_path}")
                return None
            
            file_size = os.path.getsize(audio_file_path)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"📤 Sending audio file to server: {audio_file_path}")
            logger.info(f"📊 File size: {file_size} bytes ({file_size_mb:.2f} MB)")
            logger.info(f"🌐 URL: {self.recognize_endpoint}")
            
            # Warn if file is very large
            if file_size > 10 * 1024 * 1024:  # > 10MB
                logger.warning(f"⚠️ Large file detected ({file_size_mb:.2f} MB). Upload may take longer.")
            
            # Calculate timeout based on file size
            # Estimate: ~1 second per MB for upload + processing time
            estimated_timeout = max(30, int(file_size_mb * 2) + 30)
            
            # Prepare file for upload
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'file': (
                        os.path.basename(audio_file_path),
                        audio_file,
                        'audio/wav'
                    )
                }
                
                # Make POST request with appropriate timeout based on file size
                logger.info(f"📤 Uploading file (timeout: {estimated_timeout}s)...")
                
                response = requests.post(
                    self.recognize_endpoint,
                    files=files,
                    timeout=estimated_timeout,
                    stream=False  # Don't stream, wait for full response
                )
            
            # Check response
            logger.info(f"📥 Response status: {response.status_code}")
            logger.info(f"📥 Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                # Parse JSON response safely
                try:
                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    if 'application/json' not in content_type:
                        logger.warning(f"⚠️ Unexpected content type: {content_type}")
                    
                    # Parse JSON with error handling
                    try:
                        result = response.json()
                        logger.info(f"✅ Recognition successful: {result}")
                        return result
                    except ValueError as json_error:
                        logger.error(f"❌ Failed to parse JSON response: {json_error}")
                        logger.error(f"Response text (first 500 chars): {response.text[:500]}")
                        return {
                            'success': False,
                            'error': True,
                            'status_code': 200,
                            'message': f"Lỗi parse response từ server: {str(json_error)}",
                            'detail': response.text[:200] if response.text else 'Empty response'
                        }
                except Exception as parse_error:
                    logger.error(f"❌ Error parsing response: {parse_error}")
                    return {
                        'success': False,
                        'error': True,
                        'status_code': 200,
                        'message': f"Lỗi xử lý response: {str(parse_error)}",
                        'detail': str(parse_error)
                    }
            else:
                # Handle different error status codes
                error_info = {
                    'success': False,
                    'error': True,
                    'status_code': response.status_code,
                    'message': '',
                    'detail': ''
                }
                
                try:
                    # Try to parse error response as JSON
                    error_data = response.json()
                    error_info['message'] = error_data.get('detail', error_data.get('message', 'Unknown error'))
                    error_info['detail'] = str(error_data)
                except:
                    # If not JSON, use raw text
                    error_info['message'] = response.text[:200] if response.text else f"Server error {response.status_code}"
                    error_info['detail'] = response.text
                
                # Add status-specific messages
                if response.status_code == 500:
                    error_info['message'] = f"Lỗi server (500): {error_info['message']}"
                    print(f"❌ Internal Server Error (500): {error_info['detail']}")
                elif response.status_code == 400:
                    error_info['message'] = f"Lỗi yêu cầu (400): {error_info['message']}"
                    print(f"❌ Bad Request (400): {error_info['detail']}")
                elif response.status_code == 404:
                    # 404 Not Found - endpoint doesn't exist
                    endpoint_name = self.recognize_endpoint.split('/')[-1] if '/' in self.recognize_endpoint else 'endpoint'
                    error_info['message'] = f"Không tìm thấy endpoint '/{endpoint_name}' trên server"
                    error_info['detail'] = f"Server trả về 404 Not Found. Endpoint '{self.recognize_endpoint}' không tồn tại."
                    logger.error(f"❌ Not Found (404): Endpoint '{self.recognize_endpoint}' không tồn tại")
                    logger.error(f"Response: {error_info['detail']}")
                    print(f"❌ Not Found (404): Endpoint '{self.recognize_endpoint}' không tồn tại")
                    print(f"💡 Kiểm tra xem backend server có đúng version không")
                else:
                    error_info['message'] = f"Lỗi server ({response.status_code}): {error_info['message']}"
                    print(f"❌ Server error ({response.status_code}): {error_info['detail']}")
                
                return error_info
                
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Không thể kết nối đến server: {self.base_url}"
            print(f"❌ Connection error: {error_msg}")
            print("💡 Make sure the backend server is running on port 8000")
            return {
                'success': False,
                'error': True,
                'status_code': 0,
                'message': error_msg,
                'detail': str(e)
            }
        except requests.exceptions.Timeout as e:
            # Try to get file size for better error message
            try:
                file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024) if os.path.exists(audio_file_path) else 0
                timeout_used = max(30, int(file_size_mb * 2) + 30) if file_size_mb > 0 else 60
            except:
                file_size_mb = 0
                timeout_used = 60
            
            error_msg = f"Server không phản hồi (timeout sau {timeout_used}s)"
            if file_size_mb > 5:
                error_msg += f"\n\nFile lớn ({file_size_mb:.2f} MB) có thể cần thời gian xử lý lâu hơn."
            logger.error(f"❌ Request timeout: {error_msg}")
            print(f"❌ Request timeout: {error_msg}")
            return {
                'success': False,
                'error': True,
                'status_code': 0,
                'message': error_msg,
                'detail': str(e)
            }
        except Exception as e:
            error_msg = f"Lỗi không xác định: {str(e)}"
            print(f"❌ Error during recognition: {error_msg}")
            return {
                'success': False,
                'error': True,
                'status_code': 0,
                'message': error_msg,
                'detail': str(e)
            }
    
    def test_connection(self) -> bool:
        """
        Test connection to the server
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Server connection test successful")
                return True
            elif response.status_code == 404:
                logger.warning(f"⚠️ Server responded with 404. Base URL might be wrong: {self.base_url}")
                return False
            else:
                logger.warning(f"⚠️ Server responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Cannot connect to server: {self.base_url}")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing connection: {str(e)}")
            return False
    
    def test_recognize_endpoint(self) -> Tuple[bool, str]:
        """
        Test if /recognize endpoint exists
        
        Returns:
            Tuple of (exists: bool, message: str)
        """
        try:
            # Try to access the endpoint (without file to get method not allowed or similar)
            # Or check if server root endpoint lists available endpoints
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                try:
                    data = response.json()
                    endpoints = data.get('endpoints', {})
                    if '/recognize' in str(endpoints):
                        return True, "Endpoint /recognize exists"
                    else:
                        return False, "Endpoint /recognize not found in server API"
                except:
                    return True, "Server is reachable (cannot verify endpoint)"
            elif response.status_code == 404:
                return False, f"Server base URL returns 404: {self.base_url}"
            else:
                return False, f"Server returned status {response.status_code}"
        except Exception as e:
            return False, f"Error checking endpoint: {str(e)}"

