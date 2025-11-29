"""
Video composer - combines slides, audio, and avatar into final video using FFmpeg
"""

import os
import subprocess
import json
from typing import Dict, List, Optional
import shutil


class VideoComposer:
    """Compose final video from slides, audio, and optional avatar overlay"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        
        # Check if FFmpeg is available
        if not self._check_ffmpeg():
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
    
    def _check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        try:
            result = subprocess.run([
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "json",
                audio_path
            ], capture_output=True, text=True)
            
            data = json.loads(result.stdout)
            return float(data["format"]["duration"])
        except Exception:
            return 30.0  # Default duration
    
    def create_slide_video(
        self,
        slide_image: str,
        audio_file: str,
        output_path: str,
        transition_duration: float = 0.5
    ) -> bool:
        """Create a video segment for a single slide"""
        import sys
        try:
            # Verify files exist
            print(f"[VideoComposer] Checking slide: {slide_image}", flush=True)
            if not os.path.exists(slide_image):
                print(f"[VideoComposer] ERROR: Slide image not found: {slide_image}", flush=True)
                return False
            print(f"[VideoComposer] Checking audio: {audio_file}", flush=True)
            if not os.path.exists(audio_file):
                print(f"[VideoComposer] ERROR: Audio file not found: {audio_file}", flush=True)
                return False
            audio_size = os.path.getsize(audio_file)
            if audio_size == 0:
                print(f"[VideoComposer] ERROR: Audio file is empty: {audio_file}", flush=True)
                return False
            print(f"[VideoComposer] Audio size: {audio_size} bytes", flush=True)
                
            # Get audio duration
            duration = self._get_audio_duration(audio_file)
            print(f"[VideoComposer] Creating slide video: image={os.path.basename(slide_image)}, audio={os.path.basename(audio_file)}, duration={duration}s", flush=True)
            
            # Create video from image with audio
            cmd = [
                self.ffmpeg_path,
                "-y",  # Overwrite output
                "-loop", "1",
                "-i", slide_image,
                "-i", audio_file,
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-c:a", "aac",
                "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-t", str(duration + 0.5),  # Add small buffer
                output_path
            ]
            
            print(f"[VideoComposer] Running FFmpeg: {' '.join(cmd)}", flush=True)
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=120,
                stdin=subprocess.DEVNULL  # Prevent FFmpeg from reading stdin
            )
            print(f"[VideoComposer] FFmpeg returncode: {result.returncode}", flush=True)
            if result.returncode != 0:
                print(f"[VideoComposer] FFmpeg stderr: {result.stderr}", flush=True)
                return False
            
            # Verify output was created
            if os.path.exists(output_path):
                output_size = os.path.getsize(output_path)
                print(f"[VideoComposer] Created slide video: {os.path.basename(output_path)} ({output_size} bytes)", flush=True)
            else:
                print(f"[VideoComposer] ERROR: Output not created: {output_path}", flush=True)
                return False
            return True
            
        except Exception as e:
            print(f"Error creating slide video: {e}")
            return False
    
    def create_slideshow_video(
        self,
        slide_images: List[str],
        audio_files: List[Dict],
        output_path: str,
        transition_type: str = "fade",
        transition_duration: float = 0.5
    ) -> Dict:
        """
        Create a complete video from slides and audio files
        
        Args:
            slide_images: List of slide image paths
            audio_files: List of dicts with 'path', 'duration', and 'slide_number' keys
            output_path: Output video path
            transition_type: Type of transition (fade, dissolve, wipe)
            transition_duration: Duration of transitions in seconds
            
        Returns:
            Dict with result info
        """
        temp_dir = os.path.join(os.path.dirname(output_path), "temp_videos")
        os.makedirs(temp_dir, exist_ok=True)
        
        print(f"[VideoComposer] create_slideshow_video called", flush=True)
        print(f"[VideoComposer] slide_images: {slide_images}", flush=True)
        print(f"[VideoComposer] audio_files: {audio_files}", flush=True)
        print(f"[VideoComposer] output_path: {output_path}", flush=True)
        print(f"[VideoComposer] temp_dir: {temp_dir}", flush=True)
        
        try:
            # Create a mapping of slide_number to audio info
            audio_map = {}
            for audio_info in audio_files:
                slide_num = audio_info.get("slide_number", 0)
                audio_map[slide_num] = audio_info
            
            print(f"[VideoComposer] audio_map: {audio_map}", flush=True)
            
            # Create individual slide videos
            slide_videos = []
            
            for i, slide_img in enumerate(slide_images):
                slide_num = i + 1  # 1-indexed
                slide_video_path = os.path.join(temp_dir, f"slide_{i:02d}.mp4")
                
                print(f"[VideoComposer] Processing slide {slide_num}: {slide_img}", flush=True)
                
                # Find matching audio
                audio_info = audio_map.get(slide_num)
                print(f"[VideoComposer] Audio info for slide {slide_num}: {audio_info}", flush=True)
                if audio_info and audio_info.get("path"):
                    audio_path = audio_info["path"]
                    print(f"[VideoComposer] Audio path: {audio_path}, exists: {os.path.exists(audio_path)}", flush=True)
                    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                        print(f"[VideoComposer] Creating slide video with audio", flush=True)
                        if self.create_slide_video(slide_img, audio_path, slide_video_path):
                            slide_videos.append(slide_video_path)
                            print(f"[VideoComposer] Slide video created successfully", flush=True)
                            continue
                        else:
                            print(f"[VideoComposer] create_slide_video returned False", flush=True)
                
                # No audio for this slide - create video with default duration
                print(f"[VideoComposer] Creating slide video without audio (default duration)", flush=True)
                if self.create_slide_video_no_audio(slide_img, slide_video_path, duration=5.0):
                    slide_videos.append(slide_video_path)
                    print(f"[VideoComposer] Slide video (no audio) created successfully", flush=True)
            
            print(f"[VideoComposer] Total slide_videos created: {len(slide_videos)}", flush=True)
            
            if not slide_videos:
                print(f"[VideoComposer] ERROR: No slide videos created!", flush=True)
                return {"success": False, "error": "No slide videos created"}
            
            # Concatenate all slide videos
            print(f"[VideoComposer] Concatenating {len(slide_videos)} videos...", flush=True)
            concat_result = self._concatenate_videos(slide_videos, output_path, transition_type, transition_duration)
            print(f"[VideoComposer] Concatenation result: {concat_result}", flush=True)
            
            return concat_result
            
        finally:
            # Cleanup temp files
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def create_slide_video_no_audio(
        self,
        slide_image: str,
        output_path: str,
        duration: float = 5.0
    ) -> bool:
        """Create a video segment for a slide without audio"""
        try:
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-loop", "1",
                "-i", slide_image,
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                "-an",  # No audio
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error creating slide video (no audio): {e}")
            return False
    
    def _concatenate_videos(
        self,
        video_files: List[str],
        output_path: str,
        transition_type: str = "fade",
        transition_duration: float = 0.5
    ) -> Dict:
        """Concatenate multiple video files with transitions"""
        try:
            # Create concat file list with absolute paths
            concat_file = output_path + ".txt"
            with open(concat_file, 'w') as f:
                for video in video_files:
                    # Use absolute paths to avoid path resolution issues
                    abs_video = os.path.abspath(video)
                    f.write(f"file '{abs_video}'\n")
            
            # Simple concatenation (faster, no transitions)
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-movflags", "+faststart",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            
            # Cleanup concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            if result.returncode == 0:
                # Get final video duration
                duration = self._get_audio_duration(output_path)
                return {
                    "success": True,
                    "path": output_path,
                    "duration": duration,
                    "slide_count": len(video_files)
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_avatar_overlay(
        self,
        video_path: str,
        avatar_video_path: str,
        output_path: str,
        position: str = "bottom-right",
        scale: float = 0.25
    ) -> Dict:
        """
        Add avatar overlay to video
        
        Args:
            video_path: Main video path
            avatar_video_path: Avatar video path
            output_path: Output path
            position: Position of avatar (bottom-right, bottom-left, etc.)
            scale: Scale of avatar (0.0-1.0)
        """
        try:
            # Calculate position
            positions = {
                "bottom-right": f"main_w-overlay_w-20:main_h-overlay_h-20",
                "bottom-left": f"20:main_h-overlay_h-20",
                "top-right": f"main_w-overlay_w-20:20",
                "top-left": f"20:20"
            }
            
            pos = positions.get(position, positions["bottom-right"])
            
            cmd = [
                self.ffmpeg_path,
                "-y",
                "-i", video_path,
                "-i", avatar_video_path,
                "-filter_complex",
                f"[1:v]scale=iw*{scale}:ih*{scale}[avatar];[0:v][avatar]overlay={pos}",
                "-c:a", "copy",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            
            if result.returncode == 0:
                return {"success": True, "path": output_path}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_video_from_images_and_audio(
        self,
        slide_images: List[str],
        combined_audio: str,
        output_path: str,
        fps: int = 1
    ) -> Dict:
        """
        Create video from slide images with combined audio track
        Each slide duration is calculated based on audio length / number of slides
        """
        try:
            if not slide_images:
                return {"success": False, "error": "No slide images provided"}
            
            # Get total audio duration
            total_duration = self._get_audio_duration(combined_audio)
            slide_duration = total_duration / len(slide_images)
            
            # Create a temporary directory for the process
            temp_dir = os.path.join(os.path.dirname(output_path), "temp_process")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Create input file listing slides with duration
                input_file = os.path.join(temp_dir, "input.txt")
                with open(input_file, 'w') as f:
                    for img in slide_images:
                        f.write(f"file '{img}'\n")
                        f.write(f"duration {slide_duration}\n")
                    # Add last image again (FFmpeg concat requirement)
                    f.write(f"file '{slide_images[-1]}'\n")
                
                # Create video using concat demuxer
                cmd = [
                    self.ffmpeg_path,
                    "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", input_file,
                    "-i", combined_audio,
                    "-c:v", "libx264",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    "-movflags", "+faststart",
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "path": output_path,
                        "duration": total_duration,
                        "slide_count": len(slide_images)
                    }
                else:
                    return {"success": False, "error": result.stderr}
                    
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            return {"success": False, "error": str(e)}


def compose_video(
    slide_images: List[str],
    audio_files: List[Dict],
    output_path: str,
    avatar_path: Optional[str] = None
) -> Dict:
    """Main function to compose video"""
    composer = VideoComposer()
    
    # Create main video
    result = composer.create_slideshow_video(slide_images, audio_files, output_path)
    
    # Add avatar overlay if provided
    if result["success"] and avatar_path:
        avatar_output = output_path.replace(".mp4", "_with_avatar.mp4")
        avatar_result = composer.add_avatar_overlay(
            output_path, 
            avatar_path, 
            avatar_output
        )
        if avatar_result["success"]:
            # Replace original with avatar version
            os.replace(avatar_output, output_path)
    
    return result
