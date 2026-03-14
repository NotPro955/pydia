"""
Phase 5b: Generate lip-synced video using Wav2Lip.

Charlie Kirk spokesperson image + audio → MP4 with moving lips.

Wav2Lip: Free, open-source lip-sync AI.
Repo: https://github.com/Rudrabha/Wav2Lip

SETUP (first time only):
  1. Clone repo:
     git clone https://github.com/Rudrabha/Wav2Lip.git
     cd Wav2Lip
     pip install -r requirements.txt
  
  2. Download face detection model:
     https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth
     Save to: face_detection/detection/sfd/s3fd.pth
  
  3. Download Wav2Lip checkpoint from Google Drive:
     https://drive.google.com/drive/folders/1I-0dNLfFOSFwrfqjNa-SXuwaURHE5K4k?usp=sharing
     Download wav2lip_gan.pth, save to: checkpoints/wav2lip_gan.pth
  
  4. Download Charlie Kirk's image and save as charlie_kirk.jpg in your working directory
  
  5. Set environment variable:
     export WAV2LIP_PATH="/path/to/Wav2Lip"
     (or update WAV2LIP_PATH in this file)
"""

import os
import subprocess


# Path to Wav2Lip repo — update if installed elsewhere
WAV2LIP_PATH = os.getenv("WAV2LIP_PATH", "./Wav2Lip")


def _check_wav2lip() -> bool:
    """Check if Wav2Lip is installed and accessible."""
    if not os.path.isdir(WAV2LIP_PATH):
        return False
    required_files = ["inference.py", "checkpoints/wav2lip_gan.pth", "face_detection/detection/sfd/s3fd.pth"]
    return all(os.path.exists(os.path.join(WAV2LIP_PATH, f)) for f in required_files)


def _get_spokesperson_image(image_path: str = "charlie_kirk.jpg") -> str | None:
    """Get the Charlie Kirk spokesperson image from local file.
    
    Args:
        image_path: Path to the local image file (default: charlie_kirk.jpg in current dir)
    
    Returns:
        Path to image if it exists, None otherwise
    """
    if not os.path.isfile(image_path):
        print(f"[Video] Spokesperson image not found: {image_path}")
        print(f"[Video] Please save Charlie Kirk's image as '{image_path}' in your working directory")
        print(f"[Video] (download from Wikipedia and save as JPG/PNG)")
        return None
    
    print(f"[Video] Using spokesperson image: {image_path}")
    return image_path


def generate_video(
    person_name: str,
    pitch: str,
    audio_path: str,
    spokesperson_image: str = "charlie_kirk.jpg",
    output_dir: str = "output"
) -> str | None:
    """
    Create an MP4 with Charlie Kirk lip-synced video using Wav2Lip.
    
    Args:
        person_name: Name of person being pitched (for filename)
        pitch: The spoken pitch text (unused, just for reference)
        audio_path: Path to audio WAV/MP3 file
        spokesperson_image: Path to local Charlie Kirk image (default: charlie_kirk.jpg)
        output_dir: Where to save the final MP4
    
    Returns:
        Path to final MP4 or None if Wav2Lip unavailable
    """
    os.makedirs(output_dir, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in person_name)
    final_path = os.path.join(output_dir, f"{safe_name}_pitch.mp4")

    # Check Wav2Lip installation
    if not _check_wav2lip():
        print("[Video] Wav2Lip not fully set up — skipping video")
        print("[Video] SETUP STEPS:")
        print("[Video] 1. git clone https://github.com/Rudrabha/Wav2Lip.git")
        print("[Video] 2. cd Wav2Lip && pip install -r requirements.txt")
        print("[Video] 3. Download face detection model:")
        print("[Video]    https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth")
        print("[Video]    → face_detection/detection/sfd/s3fd.pth")
        print("[Video] 4. Download wav2lip_gan.pth from:")
        print("[Video]    https://drive.google.com/drive/folders/1I-0dNLfFOSFwrfqjNa-SXuwaURHE5K4k")
        print("[Video]    → checkpoints/wav2lip_gan.pth")
        print(f"[Video] 5. Set: export WAV2LIP_PATH=/path/to/Wav2Lip")
        return None

    # Get spokesperson image
    img_path = _get_spokesperson_image(spokesperson_image)
    if not img_path:
        return None

    # Validate audio path
    if not os.path.isfile(audio_path):
        print(f"[Video] Audio file not found: {audio_path}")
        return None

    # Build Wav2Lip inference command
    cmd = [
        "python",
        os.path.join(WAV2LIP_PATH, "inference.py"),
        "--checkpoint_path", os.path.join(WAV2LIP_PATH, "checkpoints", "wav2lip_gan.pth"),
        "--face", img_path,
        "--audio", audio_path,
        "--outfile", final_path,
    ]

    try:
        print(f"[Video] Running Wav2Lip... (this may take 30-60 seconds)")
        subprocess.run(cmd, check=True, cwd=WAV2LIP_PATH)
        
        if os.path.isfile(final_path):
            file_size = os.path.getsize(final_path) / (1024 * 1024)
            print(f"[Video] Lip-synced video saved → {final_path} ({file_size:.1f}MB)")
            return final_path
        else:
            print(f"[Video] Wav2Lip completed but output file not found")
            return None

    except subprocess.CalledProcessError as e:
        print(f"[Video] Wav2Lip inference failed: {e}")
        return None
    except Exception as e:
        print(f"[Video] Unexpected error: {e}")
        return None
