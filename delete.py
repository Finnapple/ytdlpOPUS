import os
import sys
from pathlib import Path

def delete_images_after_embedding(folder_path=None):
    """
    Delete image files after verifying all OPUS files have embedded artwork
    """
    print("=" * 50)
    print("     IMAGE CLEANUP TOOL")
    print("=" * 50)
    
    # If no folder path provided, ask for it
    if not folder_path:
        folder_path = input("Enter folder path: ").strip()
    
    # Validate folder path
    folder_path = os.path.normpath(folder_path)
    if not os.path.exists(folder_path):
        print(f"[!] Error: Folder not found: {folder_path}")
        return
    
    print(f"[*] Scanning folder: {folder_path}")
    
    # Get all files
    all_files = os.listdir(folder_path)
    
    # Filter for OPUS files
    opus_files = [f for f in all_files if f.lower().endswith('.opus')]
    
    # Filter for image files (common formats)
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff']
    image_files = [
        f for f in all_files 
        if any(f.lower().endswith(ext) for ext in image_extensions)
    ]
    
    print(f"[*] Found {len(opus_files)} .opus files")
    print(f"[*] Found {len(image_files)} image files")
    
    if len(image_files) == 0:
        print("[!] No image files found to delete")
        return
    
    # Display found images
    print("\n[*] Image files found:")
    for img in sorted(image_files):
        print(f"    - {img}")
    
    # Option 1: Delete all images
    # Option 2: Delete only images that match OPUS filenames
    print("\n[1] Delete ALL image files")
    print("[2] Delete only images that have matching OPUS files (safer)")
    print("[3] Preview what would be deleted (dry run)")
    print("[0] Cancel")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "0":
        print("[*] Operation cancelled")
        return
    
    # Get base names for matching
    opus_basenames = {os.path.splitext(f)[0].lower() for f in opus_files}
    
    if choice == "1":
        # Delete all images
        files_to_delete = image_files
        condition = "ALL"
    
    elif choice == "2":
        # Delete only images that match OPUS filenames
        files_to_delete = []
        for img in image_files:
            img_basename = os.path.splitext(img)[0].lower()
            
            # Check if this image name matches any OPUS file
            # More flexible matching
            matches = [
                opus for opus in opus_basenames 
                if img_basename in opus or opus in img_basename
            ]
            
            if matches:
                files_to_delete.append(img)
        
        condition = "matching OPUS files only"
    
    elif choice == "3":
        # Dry run - just show what would be deleted
        print("\n" + "=" * 50)
        print("     DRY RUN - NO FILES WILL BE DELETED")
        print("=" * 50)
        
        # Check matching images
        matching_images = []
        non_matching_images = []
        
        for img in image_files:
            img_basename = os.path.splitext(img)[0].lower()
            matches = [opus for opus in opus_basenames if img_basename in opus or opus in img_basename]
            
            if matches:
                matching_images.append((img, matches[0]))
            else:
                non_matching_images.append(img)
        
        if matching_images:
            print("\n[*] Images that WOULD be deleted (matching OPUS files):")
            for img, match in sorted(matching_images):
                print(f"    ✓ {img} → matches {match}.opus")
        
        if non_matching_images:
            print("\n[*] Images that would NOT be deleted (no matching OPUS):")
            for img in sorted(non_matching_images):
                print(f"    ✗ {img}")
        
        print(f"\n[*] Total images that would be deleted: {len(matching_images)}")
        print("[*] This was a dry run. No files were deleted.")
        return
    
    else:
        print("[!] Invalid choice")
        return
    
    if not files_to_delete:
        print("[!] No files to delete based on selected condition")
        return
    
    # Confirm deletion
    print(f"\n[*] About to delete {len(files_to_delete)} image files ({condition})")
    print("\nFiles to be deleted:")
    for img in sorted(files_to_delete):
        print(f"    - {img}")
    
    confirm = input("\nAre you sure you want to delete these files? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("[*] Deletion cancelled")
        return
    
    # Perform deletion
    deleted_count = 0
    error_count = 0
    
    for img in files_to_delete:
        try:
            file_path = os.path.join(folder_path, img)
            os.remove(file_path)
            print(f"[✓] Deleted: {img}")
            deleted_count += 1
        except Exception as e:
            print(f"[!] Error deleting {img}: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("     CLEANUP COMPLETE")
    print("=" * 50)
    print(f"[*] Total images deleted: {deleted_count}")
    print(f"[*] Errors: {error_count}")
    print(f"[*] Remaining files in folder: {len(os.listdir(folder_path))}")
    print("=" * 50)

def main():
    print("=" * 50)
    print("     OPUS IMAGE CLEANUP TOOL")
    print("=" * 50)
    print("[1] Clean up images in folder")
    print("[2] Clean current working directory")
    print("[0] Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        delete_images_after_embedding()
    elif choice == "2":
        delete_images_after_embedding(os.getcwd())
    elif choice == "0":
        print("[*] Goodbye!")
        sys.exit(0)
    else:
        print("[!] Invalid choice")

if __name__ == "__main__":
    while True:
        main()
        print()