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

class YouTubeMusicOpusDownloader:
    def __init__(self):
        # Set output directory to the same folder as the script
        script_dir = Path(__file__).parent.absolute()
        self.output_dir = script_dir / "YouTube Music Downloads"
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
                # REMOVED: print(f"[*] Using venv Python: {venv_python}")
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
        print("[*] YouTube Music Downloader - Pure Opus Edition")
        print("[*] Download original Opus audio from YouTube Music")
        print("[*] Supports: Single tracks, Playlists, and Albums")
        print("[*] Paste YouTube Music URLs. Type 'exit' to quit.")
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
    
    def create_safe_filename(self, title: str) -> str:
        """Create a safe filename using only the song title"""
        if not title or title == 'Unknown':
            return "unknown_track.opus"
        
        # Remove invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '_')
        
        # Remove control characters
        title = ''.join(char for char in title if ord(char) >= 32)
        
        # Normalize unicode characters
        title = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode('ascii')
        
        # Replace multiple spaces with single space
        title = re.sub(r'\s+', ' ', title)
        
        # Trim whitespace
        title = title.strip()
        
        # If title is too long, truncate it
        if len(title) > 100:
            title = title[:100] + "..."
        
        # Just the title, no track numbers
        filename = f"{title}.opus"
        
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

    def get_video_info(self, url: str) -> Optional[Dict]:
        """Get video info using python -m yt_dlp --dump-json"""
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
            error_msg = "Timeout while getting video info"
            print(f"[!] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Error getting video info: {str(e)}"
            print(f"[!] {error_msg}")
            return None

    def extract_metadata(self, info: Dict) -> Dict:
        """Extract relevant metadata from yt-dlp info"""
        try:
            # Try to get artist from multiple sources
            artist = info.get('artist')
            if not artist:
                artist = info.get('uploader', 'Unknown Artist')
            
            # Try to get album from multiple sources
            album = info.get('album')
            if not album:
                album = info.get('playlist', 'Unknown Album')
            
            metadata = {
                'title': info.get('title', 'Unknown Title'),
                'artist': artist,
                'album': album,
                'track_number': info.get('track_number'),
                'release_year': info.get('release_year'),
                'release_date': info.get('release_date'),
                'genre': info.get('genre'),
            }
            
            # Clean up metadata values
            for key, value in metadata.items():
                if value is None:
                    metadata[key] = ''
                elif isinstance(value, (int, float)):
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
            }

    def download_track(self, url: str, output_dir: Path) -> Tuple[bool, str]:
        """Download a single track using python -m yt_dlp"""
        title = "Unknown Title"
        artist = "Unknown Artist"
        
        try:
            # Get video info
            print("[*] Getting video information...")
            info = self.get_video_info(url)
            if not info:
                error_msg = "Failed to get video information"
                self.log_failed_download(url, title, artist, error_msg)
                return False, error_msg
            
            # Extract metadata
            metadata = self.extract_metadata(info)
            title = metadata['title']
            artist = metadata['artist']
            
            # Create filename using ONLY the title
            filename = self.create_safe_filename(title)
            output_file = output_dir / filename
            
            # Check if file already exists
            if output_file.exists():
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"[*] File already exists: {filename} ({file_size:.1f} MB)")
                return True, "File already exists"
            
            print(f"[*] Downloading: {artist} - {title}")
            
            # Build yt-dlp command using venv Python
            cmd = [
                self.python_exe, "-m", "yt_dlp",
                "-f", "bestaudio[ext=webm][acodec=opus]/bestaudio",
                "-x",
                "--audio-format", "opus",
                "--audio-quality", "0",
                "--no-playlist",
                "--no-embed-thumbnail",
                "--embed-metadata",
                "-o", str(output_file.with_suffix('')),
                url
            ]
            
            # Add ffmpeg location if found
            if self.ffmpeg_path:
                cmd.extend(["--ffmpeg-location", self.ffmpeg_path])
            
            print(f"[*] Output file: {filename}")
            
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
                    elif '[ExtractAudio]' in line or '[ffmpeg]' in line:
                        print(f"\n{line}")
            
            proc.wait()
            
            if proc.returncode == 0 and output_file.exists():
                file_size = output_file.stat().st_size / (1024 * 1024)
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
            self.log_failed_download(url, title, artist, error_msg)
            return False, error_msg

    def process_playlist(self, url: str):
        """Process YouTube Music playlist"""
        print(f"[*] Processing playlist: {url}")
        
        try:
            # Get playlist info using venv Python
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
                entries = playlist_data.get('entries', [])
                
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
                    if not entry or not entry.get('id'):
                        print(f"[!] Skipping invalid entry {i}")
                        continue
                    
                    print(f"\n[*] Track {i}/{total}")
                    
                    video_url = f"https://music.youtube.com/watch?v={entry['id']}"
                    
                    success, _ = self.download_track(video_url, playlist_dir)
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
        """Process a YouTube Music URL"""
        url_lower = url.lower()
        
        # Accept both music.youtube.com and youtube.com URLs
        if 'youtube.com' not in url_lower and 'youtu.be' not in url_lower:
            print("[*] Please provide a valid YouTube URL")
            return False
        
        try:
            if 'playlist' in url_lower or '&list=' in url_lower:
                return self.process_playlist(url)
            else:
                print(f"[*] Processing single track: {url}")
                success, _ = self.download_track(url, self.output_dir)
                return success
        except Exception as e:
            print(f"[!] Error processing URL: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='YouTube Music Downloader - Pure Opus Edition')
    parser.add_argument('url', nargs='?', help='YouTube Music URL')
    parser.add_argument('--file', '-f', help='Text file containing multiple URLs')
    parser.add_argument('--retry', '-r', action='store_true', help='Retry failed downloads from log')
    
    args = parser.parse_args()
    
    downloader = YouTubeMusicOpusDownloader()
    
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
                url = input("\n[*] Enter YouTube Music URL: ").strip()
                
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
