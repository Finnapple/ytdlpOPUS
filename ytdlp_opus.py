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
        
        # Initialize failed downloads log
        self.failed_downloads = []
        self.failed_downloads_file = script_dir / "failed_downloads.txt"
        
        # Check if yt-dlp is installed
        if not self.check_ytdlp_installed():
            print("[*] yt-dlp is not installed. Please install it with: pip install yt-dlp")
            sys.exit(1)
        
        # Check if ffmpeg is installed
        if not self.check_ffmpeg_installed():
            print("[*] ffmpeg is not installed. Please install ffmpeg:")
            print("[*] Windows: https://ffmpeg.org/download.html")
            print("[*] Linux: sudo apt install ffmpeg")
            print("[*] macOS: brew install ffmpeg")
            sys.exit(1)
    
    def check_ytdlp_installed(self) -> bool:
        """Check if yt-dlp is installed and available"""
        try:
            subprocess.run(["yt-dlp", "--version"], 
                          capture_output=True, check=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_ffmpeg_installed(self) -> bool:
        """Check if ffmpeg is installed"""
        try:
            subprocess.run(["ffmpeg", "-version"], 
                          capture_output=True, check=True, text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
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
        """Get video info using yt-dlp --dump-json"""
        try:
            cmd = [
                "yt-dlp",
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

    def download_with_ytdlp_simple(self, url: str, output_file: Path, metadata: Dict) -> bool:
        """Download using simplified yt-dlp command with title only filename"""
        try:
            print(f"[*] Downloading with simplified command...")
            
            # Create a simple output template using only the title
            output_template = f"%(title)s.%(ext)s"
            
            # Build the yt-dlp command
            cmd = [
                "yt-dlp",
                "-f", "bestaudio[ext=webm][acodec=opus]/bestaudio",
                "--no-playlist",
                "--no-embed-thumbnail",
                "--restrict-filenames",
                "-o", output_template,
                url
            ]
            
            # Change to output directory
            original_cwd = os.getcwd()
            output_dir = output_file.parent
            output_dir.mkdir(parents=True, exist_ok=True)
            os.chdir(output_dir)
            
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )
                
                # Stream output
                output_lines = []
                for line in proc.stdout:
                    line = line.strip()
                    output_lines.append(line)
                    if line and ('%' in line or '[download]' in line or '[info]' in line):
                        print(f"[*] {line}")
                
                proc.wait()
                
                if proc.returncode == 0:
                    # Find the downloaded file
                    downloaded_files = list(output_dir.glob("*.webm")) + list(output_dir.glob("*.opus"))
                    
                    for downloaded_file in downloaded_files:
                        if downloaded_file.exists():
                            # Check if this is the file we want
                            expected_filename = self.create_safe_filename(metadata['title'])
                            if downloaded_file.name.lower() == expected_filename.lower():
                                # File already has correct name
                                file_size = downloaded_file.stat().st_size / (1024 * 1024)
                                print(f"[+] Download complete: {file_size:.1f} MB")
                                return True
                            else:
                                # Rename to our target filename
                                shutil.move(str(downloaded_file), str(output_file))
                                file_size = output_file.stat().st_size / (1024 * 1024)
                                print(f"[+] Download complete: {file_size:.1f} MB")
                                return True
                
                # If we get here, download failed
                error_output = "\n".join(output_lines[-5:])  # Last 5 lines of output
                print(f"[!] Download failed. Output: {error_output}")
                return False
                
            except subprocess.TimeoutExpired:
                print("[!] Download timeout expired")
                return False
            finally:
                os.chdir(original_cwd)
            
        except Exception as e:
            error_msg = f"Error in yt-dlp download: {str(e)}"
            print(f"[!] {error_msg}")
            return False

    def download_direct_opus(self, url: str, output_file: Path, metadata: Dict) -> bool:
        """Download using direct Opus format with simple filename"""
        try:
            # First get the exact format
            cmd_info = [
                "yt-dlp",
                "-f", "bestaudio[ext=webm][acodec=opus]",
                "--get-url",
                "--no-playlist",
                url
            ]
            
            result = subprocess.run(
                cmd_info,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = "Could not get direct Opus URL"
                if result.stderr:
                    error_msg += f": {result.stderr[:100]}"
                print(f"[!] {error_msg}")
                return False
            
            direct_url = result.stdout.strip()
            if not direct_url:
                print("[!] Empty direct URL received")
                return False
            
            print(f"[*] Downloading direct Opus stream...")
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Download using ffmpeg directly
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", direct_url,
                "-c", "copy",
                "-vn",
                "-y",
                str(output_file)
            ]
            
            proc = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if proc.returncode == 0 and output_file.exists():
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"[+] Direct Opus download complete: {file_size:.1f} MB")
                return True
            else:
                error_msg = "Direct download failed"
                if proc.stderr:
                    error_msg += f": {proc.stderr[:200]}"
                print(f"[!] {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[!] Direct download timeout expired")
            return False
        except Exception as e:
            error_msg = f"Direct Opus download error: {str(e)}"
            print(f"[!] {error_msg}")
            return False

    def download_and_convert(self, url: str, output_file: Path, metadata: Dict) -> bool:
        """Download using yt-dlp and convert to Opus with simple filename"""
        try:
            print(f"[*] Downloading and converting to Opus...")
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Use temporary filename
            temp_filename = f"temp_{int(time.time())}"
            temp_output = output_file.parent / temp_filename
            
            cmd = [
                "yt-dlp",
                "-f", "bestaudio[ext=webm][acodec=opus]/bestaudio",
                "-x",
                "--audio-format", "opus",
                "--audio-quality", "0",
                "--no-playlist",
                "--no-overwrites",
                "--no-embed-thumbnail",
                "--no-embed-metadata",
                "--restrict-filenames",
                "--output", str(temp_output),
                url
            ]
            
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Stream output
            output_lines = []
            for line in proc.stdout:
                line = line.strip()
                output_lines.append(line)
                if line and ('%' in line or '[download]' in line or '[info]' in line):
                    print(f"[*] {line}")
            
            proc.wait()
            
            if proc.returncode != 0:
                error_output = "\n".join(output_lines[-5:])
                print(f"[!] Download failed with code {proc.returncode}. Output: {error_output}")
                return False
            
            # Check for downloaded file
            for ext in ['.opus', '.webm']:
                possible_file = temp_output.with_suffix(ext)
                if possible_file.exists():
                    shutil.move(str(possible_file), str(output_file))
                    file_size = output_file.stat().st_size / (1024 * 1024)
                    print(f"[+] Download complete: {file_size:.1f} MB")
                    return True
            
            print("[!] Downloaded file not found after conversion")
            return False
            
        except subprocess.TimeoutExpired:
            print("[!] Conversion download timeout expired")
            return False
        except Exception as e:
            error_msg = f"Conversion download error: {str(e)}"
            print(f"[!] {error_msg}")
            return False

    def add_metadata_to_opus(self, opus_file: Path, metadata: Dict) -> bool:
        """Add metadata to Opus file using ffmpeg"""
        try:
            if not opus_file.exists():
                print("[!] Cannot add metadata: file does not exist")
                return False
            
            temp_file = opus_file.with_suffix('.temp.opus')
            
            # Build metadata arguments
            metadata_args = []
            
            # Add artist metadata
            if metadata.get('artist'):
                metadata_args.extend(['-metadata', f'artist={metadata["artist"]}'])
            
            # Add title metadata
            if metadata.get('title'):
                metadata_args.extend(['-metadata', f'title={metadata["title"]}'])
            
            # Add album metadata
            if metadata.get('album'):
                metadata_args.extend(['-metadata', f'album={metadata["album"]}'])
            
            # Add track number
            if metadata.get('track_number'):
                metadata_args.extend(['-metadata', f'track={metadata["track_number"]}'])
            
            # Add date
            if metadata.get('release_year'):
                metadata_args.extend(['-metadata', f'date={metadata["release_year"]}'])
            elif metadata.get('release_date'):
                metadata_args.extend(['-metadata', f'date={metadata["release_date"]}'])
            
            # Add genre
            if metadata.get('genre'):
                metadata_args.extend(['-metadata', f'genre={metadata["genre"]}'])
            
            if not metadata_args:
                print("[*] No metadata to add")
                return True
            
            # Build ffmpeg command
            ffmpeg_cmd = [
                "ffmpeg",
                "-i", str(opus_file),
                "-c", "copy",
                "-map_metadata", "0",
            ]
            ffmpeg_cmd.extend(metadata_args)
            ffmpeg_cmd.extend([
                "-y",
                str(temp_file)
            ])
            
            # Run ffmpeg
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and temp_file.exists():
                # Replace original with metadata-enhanced file
                opus_file.unlink()
                temp_file.rename(opus_file)
                print("[+] Metadata added successfully")
                return True
            else:
                error_msg = "Failed to add metadata"
                if result.stderr:
                    error_msg += f": {result.stderr[:200]}"
                print(f"[!] {error_msg}")
                if temp_file.exists():
                    temp_file.unlink()
                return False
                
        except Exception as e:
            error_msg = f"Error adding metadata: {str(e)}"
            print(f"[!] {error_msg}")
            return False

    def download_track(self, url: str, output_dir: Path) -> Tuple[bool, str]:
        """Main function to download a single track"""
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
            
            # Create filename using ONLY the title (no track numbers)
            filename = self.create_safe_filename(title)
            output_file = output_dir / filename
            
            # Check if file already exists
            if output_file.exists():
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"[*] File already exists: {filename} ({file_size:.1f} MB)")
                return True, "File already exists"
            
            print(f"[*] Downloading: {artist} - {title}")
            print(f"[*] Output filename: {filename}")
            
            # Try different download methods
            success = False
            error_messages = []
            
            # Try simplified yt-dlp command first
            if not success:
                success = self.download_with_ytdlp_simple(url, output_file, metadata)
                if not success:
                    error_messages.append("Method 1 (yt-dlp simple) failed")
            
            # If that fails, try direct Opus download
            if not success:
                success = self.download_direct_opus(url, output_file, metadata)
                if not success:
                    error_messages.append("Method 2 (direct Opus) failed")
            
            # If that also fails, try conversion method
            if not success:
                success = self.download_and_convert(url, output_file, metadata)
                if not success:
                    error_messages.append("Method 3 (conversion) failed")
            
            if success and output_file.exists():
                # Add metadata (non-critical, continue even if it fails)
                try:
                    self.add_metadata_to_opus(output_file, metadata)
                except Exception as e:
                    print(f"[*] Warning: Could not add metadata: {e}")
                
                # Final verification
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"[+] Successfully downloaded: {filename} ({file_size:.1f} MB)")
                return True, "Download successful"
            else:
                error_msg = f"All download methods failed. Errors: {', '.join(error_messages)}"
                print(f"[!] Failed to download: {title}")
                self.log_failed_download(url, title, artist, error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Unexpected error in download_track: {str(e)}"
            print(f"[!] {error_msg}")
            print(f"[!] Traceback: {traceback.format_exc()[:500]}")
            self.log_failed_download(url, title, artist, error_msg)
            return False, error_msg

    def process_playlist(self, url: str):
        """Process YouTube Music playlist"""
        print(f"[*] Processing playlist: {url}")
        
        # Clear previous failed downloads for this playlist
        original_failed_count = len(self.failed_downloads)
        
        try:
            # Get playlist info
            cmd = [
                "yt-dlp",
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
                    else:
                        print(f"[!] Failed to download track {i}")
                    
                    # Small delay between downloads
                    if i < total:
                        time.sleep(1)
                
                print(f"\n[*] Playlist download completed!")
                print(f"[*] Successful: {successful}/{total} tracks")
                
                # Show failed downloads for this playlist
                new_failed_count = len(self.failed_downloads) - original_failed_count
                if new_failed_count > 0:
                    self.show_failed_downloads_summary(f"Playlist: {playlist_title}")
                
                return successful > 0
            else:
                error_msg = "Failed to get playlist info"
                print(f"[!] {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "Timeout while getting playlist info"
            print(f"[!] {error_msg}")
            return False
        except Exception as e:
            error_msg = f"Error processing playlist: {str(e)}"
            print(f"[!] {error_msg}")
            return False

    def process_album(self, url: str):
        """Process YouTube Music album"""
        print(f"[*] Processing album: {url}")
        
        # Use playlist processing for albums
        return self.process_playlist(url)

    def process_single_track(self, url: str) -> bool:
        """Process a single YouTube Music track"""
        print(f"[*] Processing single track: {url}")
        success, error_msg = self.download_track(url, self.output_dir)
        
        if not success:
            self.show_failed_downloads_summary("Single track")
        
        return success

    def process_url(self, url: str) -> bool:
        """Process a YouTube Music URL"""
        url_lower = url.lower()
        
        # Accept both music.youtube.com and youtube.com URLs
        if 'youtube.com' not in url_lower:
            print("[*] Please provide a valid YouTube URL")
            return False
        
        try:
            if 'playlist' in url_lower:
                return self.process_playlist(url)
            elif 'album' in url_lower or 'release' in url_lower:
                return self.process_album(url)
            else:
                return self.process_single_track(url)
        except Exception as e:
            error_msg = f"Error processing URL: {str(e)}"
            print(f"[!] {error_msg}")
            self.log_failed_download(url, "Unknown", "Unknown", error_msg)
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
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            for url in urls:
                print(f"\n{'='*50}")
                downloader.process_url(url)
                print(f"{'='*50}\n")
                
        except FileNotFoundError:
            print(f"[*] File not found: {args.file}")
        except Exception as e:
            print(f"[*] Error processing file: {e}")
    
    elif args.url:
        # Process a single URL
        downloader.process_url(args.url)
        
        # Show final summary
        downloader.show_failed_downloads_summary("Final summary")
    
    else:
        # Interactive mode
        downloader.show_header()
        
        while True:
            try:
                url = input("\n[*] Enter YouTube Music URL: ").strip()
                
                if url.lower() in ['exit', 'quit', 'q']:
                    # Show final summary before exiting
                    if downloader.failed_downloads:
                        downloader.show_failed_downloads_summary("Before exit")
                    break
                
                if url.lower() in ['clear', 'cls']:
                    downloader.clear_screen()
                    continue
                
                if url.lower() == 'failed':
                    # Show failed downloads
                    downloader.show_failed_downloads_summary()
                    continue
                
                if url.lower() == 'retry':
                    # Retry failed downloads
                    downloader.retry_failed_downloads()
                    continue
                
                if not url:
                    continue
                
                downloader.process_url(url)
                
            except KeyboardInterrupt:
                print("\n[*] Exiting...")
                # Show final summary
                if downloader.failed_downloads:
                    downloader.show_failed_downloads_summary("Interrupted")
                break
            except Exception as e:
                print(f"[*] Error: {e}")

if __name__ == "__main__":
    main()