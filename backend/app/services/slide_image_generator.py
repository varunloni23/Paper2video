"""
Slide image generator - creates PNG images from slide content
"""

import os
from typing import Dict, List, Optional
from PIL import Image, ImageDraw, ImageFont
import textwrap


class SlideImageGenerator:
    """Generate slide images from slide data"""
    
    # Slide dimensions (16:9 aspect ratio, HD)
    SLIDE_WIDTH = 1920
    SLIDE_HEIGHT = 1080
    
    # Color schemes
    COLOR_SCHEMES = {
        "professional": {
            "background": "#1a1a2e",
            "title_bg": "#16213e",
            "title_text": "#ffffff",
            "body_text": "#e8e8e8",
            "bullet_color": "#4ecca3",
            "accent": "#4ecca3"
        },
        "academic": {
            "background": "#ffffff",
            "title_bg": "#2c3e50",
            "title_text": "#ffffff",
            "body_text": "#333333",
            "bullet_color": "#3498db",
            "accent": "#3498db"
        },
        "modern": {
            "background": "#0f0f0f",
            "title_bg": "#1f1f1f",
            "title_text": "#ffffff",
            "body_text": "#cccccc",
            "bullet_color": "#ff6b6b",
            "accent": "#ff6b6b"
        },
        "light": {
            "background": "#f5f5f5",
            "title_bg": "#2d3436",
            "title_text": "#ffffff",
            "body_text": "#2d3436",
            "bullet_color": "#6c5ce7",
            "accent": "#6c5ce7"
        }
    }
    
    def __init__(self, color_scheme: str = "professional"):
        self.colors = self.COLOR_SCHEMES.get(color_scheme, self.COLOR_SCHEMES["professional"])
        self.fonts = self._load_fonts()
    
    def _load_fonts(self) -> Dict:
        """Load fonts for slide text"""
        # Try to use system fonts, fall back to default
        fonts = {}
        
        # Common font paths on different systems
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "/System/Library/Fonts/SFNS.ttf",  # macOS SF Pro
        ]
        
        default_font_path = None
        for path in font_paths:
            if os.path.exists(path):
                default_font_path = path
                break
        
        try:
            if default_font_path:
                fonts["title"] = ImageFont.truetype(default_font_path, 72)
                fonts["subtitle"] = ImageFont.truetype(default_font_path, 48)
                fonts["body"] = ImageFont.truetype(default_font_path, 36)
                fonts["small"] = ImageFont.truetype(default_font_path, 28)
            else:
                # Use default font
                fonts["title"] = ImageFont.load_default()
                fonts["subtitle"] = ImageFont.load_default()
                fonts["body"] = ImageFont.load_default()
                fonts["small"] = ImageFont.load_default()
        except Exception:
            fonts["title"] = ImageFont.load_default()
            fonts["subtitle"] = ImageFont.load_default()
            fonts["body"] = ImageFont.load_default()
            fonts["small"] = ImageFont.load_default()
        
        return fonts
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def generate_title_slide(
        self,
        title: str,
        subtitle: str = "",
        author: str = "",
        output_path: str = None
    ) -> Image.Image:
        """Generate a title slide"""
        img = Image.new('RGB', (self.SLIDE_WIDTH, self.SLIDE_HEIGHT), 
                       self._hex_to_rgb(self.colors["background"]))
        draw = ImageDraw.Draw(img)
        
        # Add gradient-like effect with rectangles
        accent_color = self._hex_to_rgb(self.colors["accent"])
        draw.rectangle([0, 0, self.SLIDE_WIDTH, 8], fill=accent_color)
        draw.rectangle([0, self.SLIDE_HEIGHT - 8, self.SLIDE_WIDTH, self.SLIDE_HEIGHT], 
                      fill=accent_color)
        
        # Title
        title_wrapped = textwrap.fill(title, width=40)
        title_bbox = draw.textbbox((0, 0), title_wrapped, font=self.fonts["title"])
        title_height = title_bbox[3] - title_bbox[1]
        title_y = (self.SLIDE_HEIGHT - title_height) // 2 - 100
        
        draw.multiline_text(
            (self.SLIDE_WIDTH // 2, title_y),
            title_wrapped,
            font=self.fonts["title"],
            fill=self._hex_to_rgb(self.colors["title_text"]),
            anchor="mm",
            align="center"
        )
        
        # Subtitle
        if subtitle:
            draw.text(
                (self.SLIDE_WIDTH // 2, title_y + title_height + 60),
                subtitle,
                font=self.fonts["subtitle"],
                fill=self._hex_to_rgb(self.colors["body_text"]),
                anchor="mm"
            )
        
        # Author
        if author:
            draw.text(
                (self.SLIDE_WIDTH // 2, self.SLIDE_HEIGHT - 120),
                author,
                font=self.fonts["small"],
                fill=self._hex_to_rgb(self.colors["body_text"]),
                anchor="mm"
            )
        
        if output_path:
            img.save(output_path, 'PNG')
        
        return img
    
    def generate_content_slide(
        self,
        title: str,
        bullet_points: List[str],
        slide_number: int = 1,
        total_slides: int = 1,
        output_path: str = None
    ) -> Image.Image:
        """Generate a content slide with bullet points"""
        img = Image.new('RGB', (self.SLIDE_WIDTH, self.SLIDE_HEIGHT),
                       self._hex_to_rgb(self.colors["background"]))
        draw = ImageDraw.Draw(img)
        
        # Title bar
        title_bar_height = 140
        draw.rectangle(
            [0, 0, self.SLIDE_WIDTH, title_bar_height],
            fill=self._hex_to_rgb(self.colors["title_bg"])
        )
        
        # Accent line under title
        draw.rectangle(
            [0, title_bar_height, self.SLIDE_WIDTH, title_bar_height + 6],
            fill=self._hex_to_rgb(self.colors["accent"])
        )
        
        # Title text
        title_wrapped = textwrap.shorten(title, width=60, placeholder="...")
        draw.text(
            (80, title_bar_height // 2),
            title_wrapped,
            font=self.fonts["subtitle"],
            fill=self._hex_to_rgb(self.colors["title_text"]),
            anchor="lm"
        )
        
        # Bullet points
        bullet_start_y = title_bar_height + 80
        bullet_spacing = 90
        max_bullets = min(len(bullet_points), 7)  # Limit bullets per slide
        
        bullet_char = "●"
        
        for i, point in enumerate(bullet_points[:max_bullets]):
            y_pos = bullet_start_y + (i * bullet_spacing)
            
            # Bullet character
            draw.text(
                (80, y_pos),
                bullet_char,
                font=self.fonts["body"],
                fill=self._hex_to_rgb(self.colors["bullet_color"])
            )
            
            # Bullet text (wrap long lines)
            wrapped_text = textwrap.fill(point, width=65)
            draw.multiline_text(
                (130, y_pos),
                wrapped_text,
                font=self.fonts["body"],
                fill=self._hex_to_rgb(self.colors["body_text"])
            )
        
        # Slide number
        draw.text(
            (self.SLIDE_WIDTH - 80, self.SLIDE_HEIGHT - 50),
            f"{slide_number}/{total_slides}",
            font=self.fonts["small"],
            fill=self._hex_to_rgb(self.colors["body_text"]),
            anchor="rm"
        )
        
        if output_path:
            img.save(output_path, 'PNG')
        
        return img
    
    def generate_slides(
        self,
        slides: List[Dict],
        output_dir: str,
        presentation_title: str = "Research Presentation"
    ) -> List[str]:
        """Generate all slide images"""
        os.makedirs(output_dir, exist_ok=True)
        
        generated_paths = []
        total_slides = len(slides)
        
        for i, slide in enumerate(slides):
            slide_path = os.path.join(output_dir, f"slide_{i+1:02d}.png")
            
            slide_number = slide.get("slide_number", i + 1)
            title = slide.get("title", f"Slide {i + 1}")
            bullet_points = slide.get("bullet_points", [])
            
            # First slide is title slide
            if i == 0:
                self.generate_title_slide(
                    title=title,
                    subtitle=", ".join(bullet_points[:2]) if bullet_points else "",
                    output_path=slide_path
                )
            else:
                self.generate_content_slide(
                    title=title,
                    bullet_points=bullet_points,
                    slide_number=slide_number,
                    total_slides=total_slides,
                    output_path=slide_path
                )
            
            generated_paths.append(slide_path)
        
        return generated_paths


def generate_slide_images(
    slides: List[Dict],
    output_dir: str,
    color_scheme: str = "professional"
) -> List[str]:
    """Main function to generate slide images"""
    generator = SlideImageGenerator(color_scheme=color_scheme)
    return generator.generate_slides(slides, output_dir)
