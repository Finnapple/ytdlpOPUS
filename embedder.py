#!/usr/bin/env python3
import os
import re
from mutagen.oggopus import OggOpus
from mutagen.flac import Picture
from PIL import Image
from pathlib import Path

SUPPORTED_COVERS = (".jpg", ".jpeg", ".png")

def find_cover_for_song(song_file_path):
    """Find cover art with same base name as song file"""
    song_path = Path(song_file_path)
    base_name = song_path.stem  # Get filename without extension
    
    # Look for cover files with same base name
    folder = song_path.parent
    
    for ext in SUPPORTED_COVERS:
        cover_path = folder / f"{base_name}{ext}"
        if cover_path.exists():
            return str(cover_path)
    
    # Alternative: Look for common cover filenames
    common_covers = ["cover.jpg", "cover.jpeg", "cover.png", "album.jpg", "folder.jpg"]
    for cover_name in common_covers:
        cover_path = folder / cover_name
        if cover_path.exists():
            return str(cover_path)
    
    # Search for any image file in the folder
    for file in folder.iterdir():
        if file.suffix.lower() in SUPPORTED_COVERS:
            return str(file)
    
    return None

def embed_cover(opus_path, cover_path):
    """Embed cover art into Opus file"""
    try:
        audio = OggOpus(opus_path)
        
        # Read and process cover image
        with open(cover_path, "rb") as f:
            cover_data = f.read()
        
        # Determine MIME type from extension
        cover_ext = os.path.splitext(cover_path)[1].lower()
        if cover_ext == ".png":
            mime = "image/png"
        else:
            mime = "image/jpeg"
        
        # Get image dimensions
        with Image.open(cover_path) as img:
            img = img.convert("RGB")  # Convert to RGB for compatibility
            width, height = img.size
        
        # Create Picture metadata
        pic = Picture()
        pic.data = cover_data
        pic.type = 3  # Front cover
        pic.mime = mime
        pic.width = width
        pic.height = height
        pic.depth = 24
        
        # Embed the picture
        audio["metadata_block_picture"] = [pic.write().decode("latin1")]
        audio.save()
        
        print(f"[✓] Embedded cover → {os.path.basename(opus_path)}")
        return True
        
    except Exception as e:
        print(f"[✗] Failed to embed cover for {os.path.basename(opus_path)}: {e}")
        return False

def batch_process(folder_path):
    """Process all Opus files in folder"""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"[!] Folder not found: {folder_path}")
        return
    
    opus_files = list(folder.glob("*.opus"))
    
    if not opus_files:
        print(f"[!] No .opus files found in {folder_path}")
        return
    
    print(f"[*] Found {len(opus_files)} .opus files")
    print(f"[*] Searching for matching cover art...")
    
    processed = 0
    skipped = 0
    failed = 0
    
    for opus_file in opus_files:
        print(f"\n[*] Processing: {opus_file.name}")
        
        # Find matching cover art
        cover_path = find_cover_for_song(opus_file)
        
        if not cover_path:
            print(f"[!] No matching cover art found for: {opus_file.name}")
            print(f"    Expected: {opus_file.stem}.jpg/.png/.jpeg")
            skipped += 1
            continue
        
        print(f"[*] Found cover: {os.path.basename(cover_path)}")
        
        # Embed the cover art
        if embed_cover(str(opus_file), cover_path):
            processed += 1
        else:
            failed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print("[*] PROCESSING COMPLETE")
    print(f"[*] Total files: {len(opus_files)}")
    print(f"[*] Successfully processed: {processed}")
    print(f"[*] Skipped (no cover): {skipped}")
    print(f"[*] Failed: {failed}")
    print('='*50)
    
    # Show example of expected filenames
    if skipped > 0:
        print("\n[*] Expected filename format:")
        print("    Song:   'Song Title.opus'")
        print("    Cover:  'Song Title.jpg' (or .png/.jpeg)")
        print("")
        print("[*] Tips:")
        print("    1. Make sure cover art files are in the same folder")
        print("    2. Cover art should have same base name as the song")
        print("    3. Supported formats: .jpg, .jpeg, .png")

def interactive_mode():
    """Interactive mode with menu"""
    while True:
        print("\n" + "="*50)
        print("    OPUS COVER ART EMBEDDER")
        print("="*50)
        print("[1] Process folder")
        print("[2] Process single Opus file")
        print("[3] Show expected filename format")
        print("[0] Exit")
        print("-"*50)
        
        choice = input("\nEnter choice [0-3]: ").strip()
        
        if choice == "1":
            folder = input("\nEnter folder path: ").strip()
            if not folder:
                print("[!] No folder path provided")
                continue
            
            folder_path = Path(folder)
            if not folder_path.exists():
                print(f"[!] Folder not found: {folder}")
                continue
            
            batch_process(folder_path)
            
        elif choice == "2":
            opus_file = input("\nEnter Opus file path: ").strip()
            if not opus_file:
                print("[!] No file path provided")
                continue
            
            opus_path = Path(opus_file)
            if not opus_path.exists() or opus_path.suffix.lower() != ".opus":
                print(f"[!] Invalid Opus file: {opus_file}")
                continue
            
            print(f"\n[*] Processing single file: {opus_path.name}")
            cover_path = find_cover_for_song(opus_path)
            
            if not cover_path:
                print(f"[!] No matching cover art found for: {opus_path.name}")
                print(f"    Expected: {opus_path.stem}.jpg/.png/.jpeg")
                
                # Ask for custom cover path
                custom_cover = input("\nEnter custom cover art path (or press Enter to skip): ").strip()
                if custom_cover and Path(custom_cover).exists():
                    cover_path = custom_cover
                else:
                    continue
            
            print(f"[*] Found cover: {os.path.basename(cover_path)}")
            embed_cover(str(opus_path), cover_path)
            
        elif choice == "3":
            print("\n[*] EXPECTED FILENAME FORMAT:")
            print("="*30)
            print("FOLDER STRUCTURE:")
            print("/Music Folder/")
            print("├── Song One.opus")
            print("├── Song One.jpg    ← Same base name!")
            print("├── Song Two.opus")
            print("├── Song Two.png    ← Same base name!")
            print("├── Song Three.opus")
            print("└── Song Three.jpeg ← Same base name!")
            print()
            print("[*] The script will automatically match:")
            print("    'Song Title.opus' → 'Song Title.jpg'")
            print("    'Song Title.opus' → 'Song Title.png'")
            print("    'Song Title.opus' → 'Song Title.jpeg'")
            print()
            print("[*] If no exact match found, it will look for:")
            print("    - cover.jpg")
            print("    - cover.png")
            print("    - album.jpg")
            print("    - folder.jpg")
            print("    - Any other image file in the folder")
            
        elif choice == "0":
            print("\n[*] Goodbye!")
            break
        
        else:
            print("[!] Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2:
        # Command line mode: python script.py /path/to/folder
        folder_path = sys.argv[1]
        batch_process(folder_path)
    else:
        # Interactive mode
        interactive_mode()