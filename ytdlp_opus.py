#!/usr/bin/env python3
import os
import sys
import re
import json
import subprocess
from pathlib import Path
import argparse
from typing import List, Dict, Optional, Tuple
import time
import shutil
import unicodedata
import traceback
from datetime import datetime

class UniversalAudioDownloader:
    def __init__(self):
        # Set output directory to the same folder as the script
        script_dir = Path(__file__).parent.absolute()
        self.output_dir = script_dir / "Audio Downloads"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get the Python executable path (for virtual environment)
        self.python_exe = self.get_venv_python()
        
        # Initialize failed downloads log
        self.failed_downloads = []
        self.failed_downloads_file = script_dir / "failed_downloads.txt"
        
        # Check if yt-dlp is installed in venv
        if not self.check_ytdlp_installed():
            print("[*] yt-dlp is not installed. Installing now...")
            self.install_ytdlp()
        
        # Check if ffmpeg is available (either in PATH or in script folder)
        self.ffmpeg_path = self.find_ffmpeg()
        if not self.ffmpeg_path:
            print("[*] ffmpeg not found. Some features may not work properly.")
            print("[*] Please place ffmpeg.exe in the same folder as this script")
    
    def get_venv_python(self) -> str:
        """Get Python executable from virtual environment if it exists (silent)"""
        script_dir = Path(__file__).parent.absolute()
        
        # Check for venv in common locations
        venv_paths = [
            script_dir / "venv" / "Scripts" / "python.exe",  # Windows venv
            script_dir / "venv" / "bin" / "python",          # Linux/Mac venv
            script_dir / ".venv" / "Scripts" / "python.exe", # Alternative Windows
            script_dir / ".venv" / "bin" / "python",         # Alternative Linux/Mac
            script_dir / "ytdlp" / "Scripts" / "python.exe", # From previous setup
            script_dir / "ytdlp" / "bin" / "python",         # From previous setup
        ]
        
        for venv_python in venv_paths:
            if venv_python.exists():
                return str(venv_python)
        
        # If no venv found, use system Python
        return sys.executable
    
    def find_ffmpeg(self) -> Optional[str]:
        """Find ffmpeg in PATH or in script folder"""
        script_dir = Path(__file__).parent.absolute()
        
        # Check in script folder first
        ffmpeg_in_script = script_dir / "ffmpeg.exe"
        if ffmpeg_in_script.exists():
            return str(ffmpeg_in_script)
        
        # Check in PATH
        ffmpeg_in_path = shutil.which("ffmpeg")
        if ffmpeg_in_path:
            return ffmpeg_in_path
        
        # Check in venv folder
        venv_ffmpeg = script_dir / "venv" / "ffmpeg.exe"
        if venv_ffmpeg.exists():
            return str(venv_ffmpeg)
        
        return None
    
    def check_ytdlp_installed(self) -> bool:
        """Check if yt-dlp is installed as a Python module in venv"""
        try:
            subprocess.run(
                [self.python_exe, "-m", "yt_dlp", "--version"], 
                capture_output=True, 
                check=True, 
                text=True,
                timeout=10
            )
            return True
        except:
            return False
    
    def install_ytdlp(self):
        """Install yt-dlp using pip in venv"""
        try:
            print("[*] Installing yt-dlp...")
            subprocess.run(
                [self.python_exe, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                check=True,
                timeout=60
            )
            print("[+] yt-dlp installed successfully!")
        except Exception as e:
            print(f"[!] Failed to install yt-dlp: {e}")
            print("[*] Please install manually: python -m pip install yt-dlp")
            sys.exit(1)
    
    def clear_screen(self):
        """Clear the screen but keep the header"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_header()
    
    def show_header(self):
        """Display the header"""
        print(r"       _      _ _       ")
        print(r"      | |    | | |      ")
        print(r" _   _| |_ __| | |_ __  ")
        print(r"| | | | __/ _` | | '_ \ ")
        print(r"| |_| | || (_| | | |_) |")
        print(r" \__, |\__\__,_|_| .__/ ")
        print(r"  __/ |          | |    ")
        print(r" |___/           |_|    ")
        print("     Developed by: @Finnapple")
        print()
        print("[*] Universal Audio Downloader - Highest Quality (No Album Art)")
        print("[*] Download highest quality audio from:")
        print("[*] • SoundCloud")
        print("[*] • YouTube Music")
        print("[*] • YouTube")
        print("[*] • And more...")
        print("[*] Paste any audio URL. Type 'exit' to quit.")
        print(f"[*] Downloading to: {self.output_dir}")
        if self.ffmpeg_path:
            print(f"[*] FFmpeg: Found")
        print("-" * 50)
    
    def log_failed_download(self, url: str, title: str, artist: str, error: str):
        """Log failed download to memory and file"""
        failed_entry = {
            'url': url,
            'title': title,
            'artist': artist,
            'error': error,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.failed_downloads.append(failed_entry)
        
        # Also log to file
        try:
            with open(self.failed_downloads_file, 'a', encoding='utf-8') as f:
                f.write(f"Time: {failed_entry['timestamp']}\n")
                f.write(f"Title: {title}\n")
                f.write(f"Artist: {artist}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Error: {error}\n")
                f.write("-" * 50 + "\n\n")
        except Exception as e:
            print(f"[!] Failed to write to error log: {e}")
    
    def show_failed_downloads_summary(self, context: str = ""):
        """Show summary of failed downloads"""
        if not self.failed_downloads:
            return
        
        print("\n" + "="*60)
        print("[!] FAILED DOWNLOADS SUMMARY")
        if context:
            print(f"[!] Context: {context}")
        print("="*60)
        
        for i, failed in enumerate(self.failed_downloads, 1):
            print(f"\n[{i}] {failed['title']} - {failed['artist']}")
            print(f"    URL: {failed['url']}")
            print(f"    Error: {failed['error'][:200]}...")
            print(f"    Time: {failed['timestamp']}")
        
        print(f"\n[*] Total failed downloads: {len(self.failed_downloads)}")
        print(f"[*] Failed downloads log saved to: {self.failed_downloads_file}")
        print("="*60)
        
        # Ask user if they want to retry failed downloads
        if len(self.failed_downloads) > 0:
            retry = input("\n[*] Do you want to retry failed downloads? (y/n): ").strip().lower()
            if retry == 'y':
                self.retry_failed_downloads()
    
    def retry_failed_downloads(self):
        """Retry all failed downloads"""
        if not self.failed_downloads:
            print("[*] No failed downloads to retry.")
            return
        
        print(f"\n[*] Retrying {len(self.failed_downloads)} failed downloads...")
        
        # Create a copy of failed downloads to retry
        to_retry = self.failed_downloads.copy()
        self.failed_downloads.clear()  # Clear the list for new failures
        
        successful_retries = 0
        
        for failed in to_retry:
            print(f"\n[*] Retrying: {failed['title']} - {failed['artist']}")
            success = self.download_track(failed['url'], self.output_dir)
            
            if success:
                successful_retries += 1
                print(f"[+] Successfully retried: {failed['title']}")
            else:
                print(f"[!] Still failed: {failed['title']}")
        
        print(f"\n[*] Retry completed: {successful_retries}/{len(to_retry)} successful")
        
        # Show remaining failures
        if self.failed_downloads:
            self.show_failed_downloads_summary("After retry")
    
    def create_safe_filename(self, title: str, artist: str = "") -> str:
        """Create a safe filename using title and artist"""
        if not title or title == 'Unknown':
            return "unknown_track.mp3"
        
        # Combine artist and title if both exist
        if artist and artist != 'Unknown Artist' and artist != 'Unknown':
            filename = f"{artist} - {title}"
        else:
            filename = title
        
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove control characters
        filename = ''.join(char for char in filename if ord(char) >= 32)
        
        # Normalize unicode characters
        filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
        
        # Replace multiple spaces with single space
        filename = re.sub(r'\s+', ' ', filename)
        
        # Trim whitespace
        filename = filename.strip()
        
        # If filename is too long, truncate it
        if len(filename) > 150:
            filename = filename[:150] + "..."
        
        # Add extension
        filename = f"{filename}.mp3"
        
        return filename

    def create_safe_folder_name(self, name: str) -> str:
        """Create a safe folder name"""
        if not name or name == 'Unknown':
            return "Unknown Folder"
        
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Remove control characters
        name = ''.join(char for char in name if ord(char) >= 32)
        
        # Normalize unicode characters
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
        
        # Replace multiple spaces with single space
        name = re.sub(r'\s+', ' ', name)
        
        # Trim whitespace
        name = name.strip()
        
        # If name is too long, truncate it
        if len(name) > 150:
            name = name[:150] + "..."
        
        return name

    def detect_platform(self, url: str) -> str:
        """Detect which platform the URL is from"""
        url_lower = url.lower()
        
        if 'soundcloud.com' in url_lower:
            return 'soundcloud'
        elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            if 'music.youtube.com' in url_lower:
                return 'youtube_music'
            else:
                return 'youtube'
        elif 'spotify.com' in url_lower:
            return 'spotify'
        elif 'bandcamp.com' in url_lower:
            return 'bandcamp'
        elif 'vimeo.com' in url_lower:
            return 'vimeo'
        else:
            return 'unknown'

    def get_audio_info(self, url: str) -> Optional[Dict]:
        """Get audio info using python -m yt_dlp --dump-json"""
        try:
            cmd = [
                self.python_exe, "-m", "yt_dlp",
                "--dump-json",
                "--no-playlist",
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return None
                
        except subprocess.TimeoutExpired:
            error_msg = "Timeout while getting audio info"
            print(f"[!] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Error getting audio info: {str(e)}"
            print(f"[!] {error_msg}")
            return None

    def extract_metadata(self, info: Dict, platform: str, url: str) -> Dict:
        """Extract relevant metadata from yt-dlp info based on platform"""
        try:
            # Common fields
            title = info.get('title', 'Unknown Title')
            
            # Platform-specific artist extraction
            artist = 'Unknown Artist'
            if platform == 'soundcloud':
                # SoundCloud specific
                artist = info.get('uploader', info.get('artist', info.get('creator', 'Unknown Artist')))
                # Try to get from description or other fields
                if artist == 'Unknown Artist' and info.get('description'):
                    # Sometimes artist is in description
                    desc = info.get('description', '')
                    match = re.search(r'by\s+([^\n]+)', desc, re.IGNORECASE)
                    if match:
                        artist = match.group(1).strip()
            else:
                # YouTube and others
                artist = info.get('artist', info.get('uploader', info.get('creator', 'Unknown Artist')))
            
            # Clean up artist name (remove " - Topic" from YouTube music channels)
            if artist and ' - Topic' in artist:
                artist = artist.replace(' - Topic', '')
            
            # Album/Playlist info
            album = info.get('album', info.get('playlist', 'Unknown Album'))
            
            # Try to get better quality info
            quality = "Unknown"
            if info.get('abr'):  # Audio bitrate
                quality = f"{info.get('abr')}kbps"
            elif info.get('asr'):  # Audio sample rate
                quality = f"{info.get('asr')}Hz"
            
            metadata = {
                'title': title,
                'artist': artist,
                'album': album,
                'track_number': info.get('track_number', ''),
                'release_year': info.get('release_year', ''),
                'release_date': info.get('release_date', ''),
                'genre': info.get('genre', ''),
                'platform': platform,
                'quality': quality,
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', ''),
                'webpage_url': info.get('webpage_url', url),
                'extractor': info.get('extractor', platform)
            }
            
            # Clean up metadata values
            for key, value in metadata.items():
                if value is None:
                    metadata[key] = ''
                elif isinstance(value, (int, float)) and key not in ['duration']:
                    metadata[key] = str(value)
            
            return metadata
            
        except Exception as e:
            print(f"[!] Error extracting metadata: {e}")
            return {
                'title': 'Unknown Title',
                'artist': 'Unknown Artist',
                'album': 'Unknown Album',
                'track_number': '',
                'release_year': '',
                'release_date': '',
                'genre': '',
                'platform': platform,
                'quality': 'Unknown',
                'duration': 0,
                'uploader': '',
                'webpage_url': url,
                'extractor': platform
            }

    def get_best_audio_format(self, platform: str) -> str:
        """Get the best audio format string based on platform"""
        if platform == 'soundcloud':
            # SoundCloud: Prefer original format, then best audio
            return (
                "soundcloud:original+bestaudio/"
                "bestaudio[ext=m4a]/"
                "bestaudio[ext=mp3]/"
                "bestaudio"
            )
        elif platform == 'youtube_music':
            # YouTube Music: Prefer Opus, then best audio
            return (
                "bestaudio[ext=webm][acodec=opus]/"
                "bestaudio[ext=m4a]/"
                "bestaudio"
            )
        elif platform == 'spotify':
            # Spotify: Usually requires cookies, fallback to bestaudio
            return "bestaudio"
        else:
            # Generic: Best audio in any format
            return "bestaudio"

    def download_track(self, url: str, output_dir: Path) -> Tuple[bool, str]:
        """Download a single track using python -m yt_dlp (NO ALBUM ART)"""
        title = "Unknown Title"
        artist = "Unknown Artist"
        
        try:
            # Detect platform
            platform = self.detect_platform(url)
            print(f"[*] Detected platform: {platform.capitalize()}")
            
            # Get audio info
            print("[*] Getting audio information...")
            info = self.get_audio_info(url)
            if not info:
                error_msg = "Failed to get audio information"
                self.log_failed_download(url, title, artist, error_msg)
                return False, error_msg
            
            # Extract metadata with URL parameter
            metadata = self.extract_metadata(info, platform, url)
            title = metadata['title']
            artist = metadata['artist']
            
            # Get best format for platform
            format_spec = self.get_best_audio_format(platform)
            
            # Create filename using title and artist
            filename = self.create_safe_filename(title, artist)
            output_file = output_dir / filename
            
            # Check if file already exists
            if output_file.exists():
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"[*] File already exists: {filename} ({file_size:.1f} MB)")
                return True, "File already exists"
            
            print(f"[*] Downloading: {artist} - {title}")
            if metadata.get('quality'):
                print(f"[*] Quality: {metadata['quality']}")
            if metadata.get('duration'):
                minutes = int(metadata['duration']) // 60
                seconds = int(metadata['duration']) % 60
                print(f"[*] Duration: {minutes}:{seconds:02d}")
            
            # Build yt-dlp command for highest quality audio (NO ALBUM ART)
            cmd = [
                self.python_exe, "-m", "yt_dlp",
                "-f", format_spec,
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "0",  # Best quality
                "--no-playlist",
                "--embed-metadata",
                "--no-embed-thumbnail",  # NO ALBUM ART
                "--no-embed-chapters",
                "--no-embed-info-json",
                "--add-metadata",
                "--prefer-ffmpeg",
                "-o", str(output_file.with_suffix('')),  # Remove extension, yt-dlp will add proper one
                url
            ]
            
            # Add ffmpeg location if found
            if self.ffmpeg_path:
                cmd.extend(["--ffmpeg-location", self.ffmpeg_path])
            
            print(f"[*] Output file: {filename}")
            print("[*] Album art: Disabled")
            
            # Run download
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output
            for line in proc.stdout:
                line = line.strip()
                if line:
                    if '%' in line or '[download]' in line:
                        print(f"\r{line}", end='', flush=True)
                    elif '[ExtractAudio]' in line or '[ffmpeg]' in line or '[Metadata]' in line:
                        print(f"\n{line}")
                    elif '[soundcloud]' in line.lower():
                        print(f"\n{line}")
            
            proc.wait()
            
            # Check for downloaded file (might be .mp3 or .opus or .m4a)
            possible_files = list(output_dir.glob(f"{output_file.stem}.*"))
            downloaded_file = None
            for f in possible_files:
                if f.suffix.lower() in ['.mp3', '.opus', '.m4a', '.webm', '.ogg']:
                    downloaded_file = f
                    break
            
            if proc.returncode == 0 and downloaded_file and downloaded_file.exists():
                # If not already mp3, rename to mp3
                if downloaded_file.suffix.lower() != '.mp3':
                    mp3_file = output_file.with_suffix('.mp3')
                    shutil.move(str(downloaded_file), str(mp3_file))
                    file_size = mp3_file.stat().st_size / (1024 * 1024)
                else:
                    file_size = downloaded_file.stat().st_size / (1024 * 1024)
                
                print(f"\n[+] Download complete: {filename} ({file_size:.1f} MB)")
                return True, "Download successful"
            else:
                error_msg = f"Download failed with code {proc.returncode}"
                print(f"\n[!] {error_msg}")
                self.log_failed_download(url, title, artist, error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"\n[!] {error_msg}")
            print(f"[!] Traceback: {traceback.format_exc()}")
            self.log_failed_download(url, title, artist, error_msg)
            return False, error_msg

    def process_playlist(self, url: str):
        """Process playlist from any platform"""
        print(f"[*] Processing playlist: {url}")
        
        # Detect platform
        platform = self.detect_platform(url)
        print(f"[*] Detected platform: {platform.capitalize()}")
        
        try:
            # Get playlist info
            cmd = [
                self.python_exe, "-m", "yt_dlp",
                "--flat-playlist",
                "--dump-single-json",
                url
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                playlist_data = json.loads(result.stdout)
                playlist_title = playlist_data.get('title', 'Playlist')
                
                # For SoundCloud, entries might be in different format
                entries = []
                if 'entries' in playlist_data:
                    entries = playlist_data['entries']
                elif '_entries' in playlist_data:
                    entries = playlist_data['_entries']
                
                print(f"[*] Playlist: {playlist_title}")
                print(f"[*] Total tracks: {len(entries)}")
                
                # Create playlist directory
                safe_playlist_title = self.create_safe_folder_name(playlist_title)
                playlist_dir = self.output_dir / safe_playlist_title
                playlist_dir.mkdir(exist_ok=True)
                
                # Download each track
                successful = 0
                total = len(entries)
                
                for i, entry in enumerate(entries, 1):
                    if not entry:
                        print(f"[!] Skipping invalid entry {i}")
                        continue
                    
                    # Get track URL
                    if 'url' in entry:
                        track_url = entry['url']
                    elif 'webpage_url' in entry:
                        track_url = entry['webpage_url']
                    elif 'id' in entry:
                        # Construct URL based on platform
                        if platform == 'soundcloud':
                            track_url = f"https://soundcloud.com/{entry['id']}"
                        else:
                            track_url = f"https://youtube.com/watch?v={entry['id']}"
                    else:
                        print(f"[!] Skipping entry {i} - no URL found")
                        continue
                    
                    print(f"\n[*] Track {i}/{total}")
                    
                    success, _ = self.download_track(track_url, playlist_dir)
                    if success:
                        successful += 1
                    
                    # Small delay between downloads
                    if i < total:
                        time.sleep(1)
                
                print(f"\n[*] Playlist download completed!")
                print(f"[*] Successful: {successful}/{total} tracks")
                
                return successful > 0
            else:
                print("[!] Failed to get playlist info")
                return False
                
        except Exception as e:
            print(f"[!] Error processing playlist: {e}")
            return False

    def process_url(self, url: str) -> bool:
        """Process URL from any platform"""
        url_lower = url.lower()
        
        # Check if it's a valid URL
        if not (url.startswith('http://') or url.startswith('https://')):
            print("[*] Please provide a valid URL (starting with http:// or https://)")
            return False
        
        try:
            # Check if it's a playlist
            if any(x in url_lower for x in ['playlist', 'set/', 'album', 'list=']):
                print("[*] Detected playlist/set/album")
                return self.process_playlist(url)
            else:
                print("[*] Detected single track")
                success, _ = self.download_track(url, self.output_dir)
                return success
                
        except Exception as e:
            print(f"[!] Error processing URL: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Universal Audio Downloader - Highest Quality (No Album Art)')
    parser.add_argument('url', nargs='?', help='Audio URL (YouTube Music, SoundCloud, etc.)')
    parser.add_argument('--file', '-f', help='Text file containing multiple URLs')
    parser.add_argument('--retry', '-r', action='store_true', help='Retry failed downloads from log')
    
    args = parser.parse_args()
    
    downloader = UniversalAudioDownloader()
    
    # Check if there are existing failed downloads
    if downloader.failed_downloads_file.exists():
        try:
            with open(downloader.failed_downloads_file, 'r', encoding='utf-8') as f:
                if f.read().strip():
                    print(f"[*] Found existing failed downloads log: {downloader.failed_downloads_file}")
        except:
            pass
    
    if args.retry:
        # Retry failed downloads from file
        if downloader.failed_downloads_file.exists():
            try:
                with open(downloader.failed_downloads_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        print("[*] Loading failed downloads from log...")
                        # Parse URLs from log
                        urls = []
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if line.startswith('URL: '):
                                url = line[5:].strip()
                                if url and url not in urls:
                                    urls.append(url)
                        
                        if urls:
                            print(f"[*] Found {len(urls)} failed downloads to retry")
                            for url in urls:
                                print(f"\n{'='*50}")
                                downloader.process_url(url)
                                print(f"{'='*50}\n")
                        else:
                            print("[*] No failed downloads found in log")
                    else:
                        print("[*] Failed downloads log is empty")
            except Exception as e:
                print(f"[!] Error reading failed downloads log: {e}")
        else:
            print("[*] No failed downloads log found")
        return
    
    if args.file:
        # Process multiple URLs from a file
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"[*] Found {len(urls)} URLs in file")
            
            for i, url in enumerate(urls, 1):
                print(f"\n{'='*50}")
                print(f"[*] URL {i}/{len(urls)}")
                print(f"{'='*50}")
                downloader.process_url(url)
                
        except FileNotFoundError:
            print(f"[!] File not found: {args.file}")
        except Exception as e:
            print(f"[!] Error processing file: {e}")
    
    elif args.url:
        # Process a single URL
        downloader.process_url(args.url)
        
        # Show failed downloads summary
        if downloader.failed_downloads:
            downloader.show_failed_downloads_summary()
    
    else:
        # Interactive mode
        downloader.show_header()
        
        while True:
            try:
                url = input("\n[*] Enter Audio URL (YouTube Music/SoundCloud/etc): ").strip()
                
                if url.lower() in ['exit', 'quit', 'q']:
                    if downloader.failed_downloads:
                        downloader.show_failed_downloads_summary("Before exit")
                    print("[*] Goodbye!")
                    break
                
                if url.lower() in ['clear', 'cls']:
                    downloader.clear_screen()
                    continue
                
                if url.lower() == 'failed':
                    downloader.show_failed_downloads_summary()
                    continue
                
                if url.lower() == 'retry':
                    downloader.retry_failed_downloads()
                    continue
                
                if not url:
                    continue
                
                downloader.process_url(url)
                
            except KeyboardInterrupt:
                print("\n[*] Exiting...")
                break
            except Exception as e:
                print(f"[!] Error: {e}")

if __name__ == "__main__":
    main()
