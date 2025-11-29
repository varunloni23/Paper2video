"""
Text-to-Speech module using edge-tts (Microsoft Edge TTS)
Falls back to macOS 'say' command if edge-tts fails.
"""

import os
import asyncio
import subprocess
import tempfile
import re
from typing import List, Dict, Optional


class TTSGenerator:
    """Generate voiceover audio from text using Edge TTS or macOS say"""
    
    # Available voices for research/professional presentations
    VOICE_OPTIONS = {
        "neutral_male": "en-US-GuyNeural",
        "neutral_female": "en-US-JennyNeural", 
        "professional_male": "en-US-ChristopherNeural",
        "professional_female": "en-US-AriaNeural",
        "british_male": "en-GB-RyanNeural",
        "british_female": "en-GB-SoniaNeural"
    }
    
    # macOS voices as fallback
    MACOS_VOICES = {
        "neutral_male": "Alex",
        "neutral_female": "Samantha",
        "professional_male": "Daniel",
        "professional_female": "Karen",
        "british_male": "Daniel",
        "british_female": "Karen"
    }
    
    def __init__(self, voice: str = "neutral_female", rate: str = "-5%", volume: str = "+0%"):
        """Initialize TTS generator"""
        self.voice = self.VOICE_OPTIONS.get(voice, voice)
        self.macos_voice = self.MACOS_VOICES.get(voice, "Samantha")
        self.rate = rate
        self.volume = volume
    
    async def generate_audio(self, text: str, output_path: str) -> Dict:
        """Generate audio file from text"""
        try:
            # Clean and sanitize text for TTS
            clean_text = self._clean_text_for_tts(text)
            
            if not clean_text or len(clean_text.strip()) < 5:
                return {
                    "success": True,
                    "path": None,
                    "estimated_duration": 0,
                    "word_count": 0,
                    "skipped": True
                }
            
            # Try edge-tts first, fall back to macOS say
            result = await self._try_edge_tts(clean_text, output_path)
            if not result["success"]:
                print(f"edge-tts failed, falling back to macOS say command", flush=True)
                result = self._use_macos_say(clean_text, output_path)
            
            return result
            
        except Exception as e:
            print(f"TTS Error: {e}", flush=True)
            return {
                "success": False,
                "error": str(e),
                "path": None
            }
    
    async def _try_edge_tts(self, text: str, output_path: str) -> Dict:
        """Try to use edge-tts"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                text_file = f.name
            
            try:
                cmd = [
                    'edge-tts',
                    '--voice', self.voice,
                    f'--rate={self.rate}',
                    f'--volume={self.volume}',
                    '--file', text_file,
                    '--write-media', output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
                
                if result.returncode != 0:
                    return {"success": False, "error": result.stderr or "edge-tts failed"}
            finally:
                if os.path.exists(text_file):
                    os.unlink(text_file)
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return {"success": False, "error": "Audio file was not created"}
            
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60
            
            return {
                "success": True,
                "path": output_path,
                "estimated_duration": estimated_duration,
                "word_count": word_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _use_macos_say(self, text: str, output_path: str) -> Dict:
        """Use macOS 'say' command as fallback"""
        try:
            temp_aiff = output_path.replace('.mp3', '.aiff')
            
            cmd = [
                'say',
                '-v', self.macos_voice,
                '-o', temp_aiff,
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
            if result.returncode != 0:
                return {"success": False, "error": f"macOS say failed: {result.stderr}"}
            
            cmd_ffmpeg = [
                'ffmpeg', '-y',
                '-i', temp_aiff,
                '-acodec', 'libmp3lame',
                '-ab', '192k',
                output_path
            ]
            
            result = subprocess.run(cmd_ffmpeg, capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
            
            if os.path.exists(temp_aiff):
                os.unlink(temp_aiff)
            
            if result.returncode != 0:
                return {"success": False, "error": f"ffmpeg conversion failed: {result.stderr}"}
            
            if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                return {"success": False, "error": "Audio file was not created"}
            
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60
            
            return {
                "success": True,
                "path": output_path,
                "estimated_duration": estimated_duration,
                "word_count": word_count
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for TTS processing"""
        if not text:
            return ""
        
        text = re.sub(r'###?\s*', '', text)
        
        text = text.replace('\ufb01', 'fi')
        text = text.replace('\ufb02', 'fl')
        text = text.replace('\u2019', "'")
        text = text.replace('\u2018', "'")
        text = text.replace('\u201c', '"')
        text = text.replace('\u201d', '"')
        text = text.replace('\u2013', '-')
        text = text.replace('\u2014', '-')
        
        text = ''.join(char for char in text if char.isprintable() or char in '\n\t ')
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) > 3000:
            text = text[:3000] + "..."
        
        return text
    
    async def generate_slide_audio(
        self,
        slides: List[Dict],
        output_dir: str,
        pause_between_slides: float = 0.5
    ) -> Dict:
        """Generate individual audio files for each slide"""
        os.makedirs(output_dir, exist_ok=True)
        
        audio_files = []
        total_duration = 0
        
        for i, slide in enumerate(slides):
            narration = slide.get("narration", "")
            if not narration:
                continue
            
            slide_audio_path = os.path.join(output_dir, f"slide_{i+1:02d}.mp3")
            
            result = await self.generate_audio(narration, slide_audio_path)
            
            if result["success"]:
                if result.get("skipped"):
                    print(f"Slide {i+1}: Text too short, skipping", flush=True)
                    continue
                    
                audio_files.append({
                    "slide_number": i + 1,
                    "path": slide_audio_path,
                    "duration": result["estimated_duration"],
                    "word_count": result["word_count"]
                })
                total_duration += result["estimated_duration"] + pause_between_slides
            else:
                print(f"Failed to generate audio for slide {i+1}: {result.get('error')}", flush=True)
        
        return {
            "success": True,
            "audio_files": audio_files,
            "total_estimated_duration": total_duration,
            "slide_count": len(audio_files)
        }


async def generate_audio_for_slides(
    slides: List[Dict],
    output_dir: str,
    voice: str = "neutral_female"
) -> Dict:
    """Main function to generate audio for slides"""
    generator = TTSGenerator(voice=voice)
    return await generator.generate_slide_audio(slides, output_dir)


async def generate_single_audio(
    text: str,
    output_path: str,
    voice: str = "neutral_female"
) -> Dict:
    """Generate single audio file from text"""
    generator = TTSGenerator(voice=voice)
    return await generator.generate_audio(text, output_path)
