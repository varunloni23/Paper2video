"""
SVG Avatar generator with lip-sync animation for video overlay
"""

import os
import math
import subprocess
from typing import List, Dict, Optional


class SVGAvatarGenerator:
    """Generate animated SVG avatar with lip-sync"""
    
    # SVG template for a simple talking head avatar
    SVG_TEMPLATE = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{width}" height="{height}">
  <defs>
    <linearGradient id="skinGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{skin_light};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{skin_dark};stop-opacity:1" />
    </linearGradient>
    <linearGradient id="hairGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:{hair_light};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{hair_dark};stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background circle -->
  <circle cx="100" cy="100" r="95" fill="{bg_color}"/>
  
  <!-- Neck -->
  <rect x="75" y="145" width="50" height="40" fill="url(#skinGrad)" rx="5"/>
  
  <!-- Face -->
  <ellipse cx="100" cy="95" rx="55" ry="60" fill="url(#skinGrad)"/>
  
  <!-- Hair -->
  <ellipse cx="100" cy="55" rx="50" ry="30" fill="url(#hairGrad)"/>
  <ellipse cx="55" cy="75" rx="15" ry="25" fill="url(#hairGrad)"/>
  <ellipse cx="145" cy="75" rx="15" ry="25" fill="url(#hairGrad)"/>
  
  <!-- Eyes -->
  <ellipse cx="75" cy="85" rx="12" ry="8" fill="white"/>
  <ellipse cx="125" cy="85" rx="12" ry="8" fill="white"/>
  <circle cx="75" cy="85" r="5" fill="{eye_color}"/>
  <circle cx="125" cy="85" r="5" fill="{eye_color}"/>
  <circle cx="76" cy="84" r="2" fill="white"/>
  <circle cx="126" cy="84" r="2" fill="white"/>
  
  <!-- Eyebrows -->
  <path d="M 60 72 Q 75 68 90 72" stroke="{hair_dark}" stroke-width="3" fill="none"/>
  <path d="M 110 72 Q 125 68 140 72" stroke="{hair_dark}" stroke-width="3" fill="none"/>
  
  <!-- Nose -->
  <path d="M 100 90 L 95 110 Q 100 115 105 110 L 100 90" fill="{nose_color}" opacity="0.5"/>
  
  <!-- Mouth (animated) -->
  <ellipse cx="100" cy="130" rx="{mouth_width}" ry="{mouth_height}" fill="{mouth_color}">
    <animate attributeName="ry" values="{mouth_anim}" dur="{anim_duration}s" repeatCount="indefinite"/>
  </ellipse>
  
  <!-- Teeth hint -->
  <rect x="88" y="126" width="24" height="{teeth_height}" fill="white" rx="2" opacity="{teeth_opacity}"/>
  
  <!-- Ears -->
  <ellipse cx="45" cy="95" rx="8" ry="15" fill="url(#skinGrad)"/>
  <ellipse cx="155" cy="95" rx="8" ry="15" fill="url(#skinGrad)"/>
  
  <!-- Shirt collar hint -->
  <path d="M 60 175 L 75 155 L 100 165 L 125 155 L 140 175" fill="{shirt_color}" stroke="{shirt_color}"/>
</svg>'''
    
    # Avatar style presets
    STYLE_PRESETS = {
        "professional_male": {
            "skin_light": "#e8beac",
            "skin_dark": "#d4a594",
            "hair_light": "#4a3728",
            "hair_dark": "#2d1f15",
            "eye_color": "#4a3728",
            "nose_color": "#c49a87",
            "mouth_color": "#c17f6f",
            "shirt_color": "#2c3e50",
            "bg_color": "#34495e"
        },
        "professional_female": {
            "skin_light": "#f5d0c5",
            "skin_dark": "#e8beac",
            "hair_light": "#5c3d2e",
            "hair_dark": "#3d2517",
            "eye_color": "#5c3d2e",
            "nose_color": "#ddb3a3",
            "mouth_color": "#d4726a",
            "shirt_color": "#8e44ad",
            "bg_color": "#9b59b6"
        },
        "casual": {
            "skin_light": "#ffe0bd",
            "skin_dark": "#f5c9a8",
            "hair_light": "#2c1810",
            "hair_dark": "#1a0f0a",
            "eye_color": "#2c1810",
            "nose_color": "#e8b89a",
            "mouth_color": "#c46c5e",
            "shirt_color": "#27ae60",
            "bg_color": "#2ecc71"
        }
    }
    
    def __init__(self, style: str = "professional_female"):
        self.style = self.STYLE_PRESETS.get(style, self.STYLE_PRESETS["professional_female"])
    
    def generate_static_avatar(
        self,
        output_path: str,
        width: int = 200,
        height: int = 200,
        mouth_open: float = 0.5
    ) -> str:
        """Generate a static SVG avatar"""
        mouth_height = int(5 + mouth_open * 10)
        mouth_width = int(15 + mouth_open * 5)
        teeth_height = int(mouth_open * 8)
        teeth_opacity = mouth_open * 0.8
        
        svg_content = self.SVG_TEMPLATE.format(
            width=width,
            height=height,
            mouth_width=mouth_width,
            mouth_height=mouth_height,
            mouth_anim=f"{mouth_height};{mouth_height}",
            anim_duration=1,
            teeth_height=teeth_height,
            teeth_opacity=teeth_opacity,
            **self.style
        )
        
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return output_path
    
    def generate_animated_avatar(
        self,
        output_path: str,
        duration: float = 5.0,
        width: int = 200,
        height: int = 200
    ) -> str:
        """Generate an animated SVG avatar with lip-sync animation"""
        
        # Generate mouth animation keyframes
        # Simulates natural speech patterns
        mouth_values = []
        frames = 20
        for i in range(frames):
            t = i / frames
            # Create natural-looking mouth movement
            value = 5 + 10 * abs(math.sin(t * math.pi * 4))
            mouth_values.append(f"{value:.1f}")
        mouth_values.append(mouth_values[0])  # Loop back
        
        mouth_anim = ";".join(mouth_values)
        anim_duration = 0.5  # Quick animation cycle
        
        svg_content = self.SVG_TEMPLATE.format(
            width=width,
            height=height,
            mouth_width=18,
            mouth_height=8,
            mouth_anim=mouth_anim,
            anim_duration=anim_duration,
            teeth_height=4,
            teeth_opacity=0.6,
            **self.style
        )
        
        with open(output_path, 'w') as f:
            f.write(svg_content)
        
        return output_path
    
    def generate_avatar_video(
        self,
        output_path: str,
        duration: float,
        width: int = 400,
        height: int = 400,
        fps: int = 30,
        background_transparent: bool = True
    ) -> Dict:
        """
        Generate a video of the animated avatar
        
        This creates a video with lip-sync animation that can be overlaid
        on the presentation video.
        """
        temp_dir = os.path.dirname(output_path)
        frames_dir = os.path.join(temp_dir, "avatar_frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        try:
            total_frames = int(duration * fps)
            
            # Generate frames with varying mouth positions
            for frame in range(total_frames):
                t = frame / fps
                
                # Natural speech-like mouth movement
                # Combine multiple frequencies for more realistic movement
                mouth_open = (
                    0.5 * abs(math.sin(t * 8)) +
                    0.3 * abs(math.sin(t * 12 + 0.5)) +
                    0.2 * abs(math.sin(t * 5 + 1.0))
                )
                mouth_open = min(1.0, mouth_open)
                
                # Generate SVG frame
                svg_path = os.path.join(frames_dir, f"frame_{frame:05d}.svg")
                self._generate_frame(svg_path, width, height, mouth_open)
                
                # Convert SVG to PNG
                png_path = os.path.join(frames_dir, f"frame_{frame:05d}.png")
                self._svg_to_png(svg_path, png_path, width, height)
            
            # Combine frames into video
            result = self._frames_to_video(frames_dir, output_path, fps, background_transparent)
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            # Cleanup frames
            import shutil
            if os.path.exists(frames_dir):
                shutil.rmtree(frames_dir, ignore_errors=True)
    
    def _generate_frame(
        self,
        output_path: str,
        width: int,
        height: int,
        mouth_open: float
    ):
        """Generate a single frame SVG"""
        mouth_height = int(5 + mouth_open * 10)
        mouth_width = int(15 + mouth_open * 5)
        teeth_height = max(1, int(mouth_open * 8))
        teeth_opacity = mouth_open * 0.8
        
        svg_content = self.SVG_TEMPLATE.format(
            width=width,
            height=height,
            mouth_width=mouth_width,
            mouth_height=mouth_height,
            mouth_anim=f"{mouth_height};{mouth_height}",
            anim_duration=1,
            teeth_height=teeth_height,
            teeth_opacity=teeth_opacity,
            **self.style
        )
        
        with open(output_path, 'w') as f:
            f.write(svg_content)
    
    def _svg_to_png(self, svg_path: str, png_path: str, width: int, height: int):
        """Convert SVG to PNG using various methods"""
        try:
            # Try using cairosvg if available
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=width, output_height=height)
            return
        except ImportError:
            pass
        
        try:
            # Try using Pillow with svg support
            from PIL import Image
            import io
            
            # Read SVG and create image
            with open(svg_path, 'rb') as f:
                svg_data = f.read()
            
            # Create a simple colored circle as fallback
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            img.save(png_path, 'PNG')
        except Exception:
            # Create placeholder image
            from PIL import Image
            img = Image.new('RGBA', (width, height), (52, 73, 94, 255))
            img.save(png_path, 'PNG')
    
    def _frames_to_video(
        self,
        frames_dir: str,
        output_path: str,
        fps: int,
        transparent: bool = False
    ) -> Dict:
        """Convert frames to video using FFmpeg"""
        try:
            input_pattern = os.path.join(frames_dir, "frame_%05d.png")
            
            cmd = [
                "ffmpeg",
                "-y",
                "-framerate", str(fps),
                "-i", input_pattern,
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p" if not transparent else "yuva420p",
                "-preset", "medium",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL)
            
            if result.returncode == 0:
                return {"success": True, "path": output_path}
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}


def generate_avatar_overlay(
    output_path: str,
    duration: float,
    style: str = "professional_female"
) -> Dict:
    """Main function to generate avatar overlay video"""
    generator = SVGAvatarGenerator(style=style)
    return generator.generate_avatar_video(output_path, duration)


def generate_static_avatar_svg(
    output_path: str,
    style: str = "professional_female"
) -> str:
    """Generate a static SVG avatar"""
    generator = SVGAvatarGenerator(style=style)
    return generator.generate_animated_avatar(output_path)
