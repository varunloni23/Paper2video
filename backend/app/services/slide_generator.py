"""
LLM-based slide script generator using Google Gemini
"""

import json
import re
from typing import Dict, List, Optional
import google.generativeai as genai
from app.config import settings

# Configure Gemini
genai.configure(api_key=settings.gemini_api_key)

class SlideGenerator:
    """Generate slide scripts from document content using Gemini"""
    
    def __init__(self, style: str = "concise"):
        self.style = style
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Style configurations
        self.style_configs = {
            "concise": {
                "num_slides": "5-8",
                "bullet_points": "3-4 per slide",
                "narration_length": "30-45 seconds per slide",
                "detail_level": "high-level overview, key points only"
            },
            "detailed": {
                "num_slides": "8-12",
                "bullet_points": "4-6 per slide",
                "narration_length": "45-60 seconds per slide",
                "detail_level": "comprehensive explanation with examples"
            }
        }
    
    async def generate_slide_script(
        self, 
        text: str, 
        sections: List[Dict],
        title: str = "Research Presentation"
    ) -> List[Dict]:
        """Generate slide script from document content"""
        
        style_config = self.style_configs.get(self.style, self.style_configs["concise"])
        
        # Prepare content summary for the prompt
        sections_text = ""
        if sections:
            for section in sections[:10]:  # Limit sections
                sections_text += f"\n### {section.get('title', 'Section')}\n"
                content = section.get('content', '')[:2000]  # Limit content length
                sections_text += content + "\n"
        else:
            sections_text = text[:10000]  # Use raw text if no sections
        
        prompt = f"""You are an expert at creating engaging academic presentations.

Given the following research paper content, create a slide-by-slide presentation script.

DOCUMENT TITLE: {title}

DOCUMENT CONTENT:
{sections_text}

STYLE: {self.style.upper()}
- Number of slides: {style_config['num_slides']}
- Bullet points: {style_config['bullet_points']}
- Narration length: {style_config['narration_length']}
- Detail level: {style_config['detail_level']}

Generate a JSON array of slides. Each slide should have:
1. "slide_number": integer
2. "title": string (slide title)
3. "bullet_points": array of strings (key points to display)
4. "narration": string (what the presenter should say, written naturally for text-to-speech)
5. "notes": string (any additional notes, optional)
6. "visual_suggestion": string (suggestion for visual/figure to include, optional)

IMPORTANT:
- First slide should be a title slide with paper title and key info
- Include slides for: Introduction, Methods/Approach, Key Results, Conclusion
- Make narration sound natural and engaging for spoken delivery
- Keep bullet points concise but informative
- The narration should expand on bullet points, not just read them

Return ONLY valid JSON array, no other text. Example format:
[
  {{
    "slide_number": 1,
    "title": "Paper Title",
    "bullet_points": ["Author names", "Institution", "Key contribution"],
    "narration": "Welcome to this presentation about...",
    "visual_suggestion": "Title with institution logo"
  }},
  ...
]
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            slides = self._parse_json_response(response_text)
            
            # Validate and clean slides
            slides = self._validate_slides(slides)
            
            return slides
            
        except Exception as e:
            print(f"Error generating slides: {e}")
            # Return a basic fallback structure
            return self._generate_fallback_slides(title, sections_text)
    
    def _parse_json_response(self, text: str) -> List[Dict]:
        """Parse JSON from LLM response"""
        # Try to find JSON array in the response
        text = text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            # Remove opening ```json or ```
            text = re.sub(r'^```(?:json)?\s*', '', text)
            # Remove closing ```
            text = re.sub(r'\s*```$', '', text)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON array from text
            match = re.search(r'\[[\s\S]*\]', text)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass
            return []
    
    def _validate_slides(self, slides: List[Dict]) -> List[Dict]:
        """Validate and clean slide data"""
        validated = []
        
        for i, slide in enumerate(slides):
            validated_slide = {
                "slide_number": slide.get("slide_number", i + 1),
                "title": slide.get("title", f"Slide {i + 1}"),
                "bullet_points": slide.get("bullet_points", []),
                "narration": slide.get("narration", ""),
                "notes": slide.get("notes", ""),
                "visual_suggestion": slide.get("visual_suggestion", "")
            }
            
            # Ensure bullet_points is a list
            if isinstance(validated_slide["bullet_points"], str):
                validated_slide["bullet_points"] = [validated_slide["bullet_points"]]
            
            # Ensure narration is not empty
            if not validated_slide["narration"]:
                validated_slide["narration"] = f"This slide covers {validated_slide['title']}. " + \
                    " ".join(validated_slide["bullet_points"][:3])
            
            validated.append(validated_slide)
        
        return validated
    
    def _generate_fallback_slides(self, title: str, content: str) -> List[Dict]:
        """Generate basic fallback slides if LLM fails"""
        # Split content into chunks
        words = content.split()
        chunk_size = len(words) // 5
        
        slides = [
            {
                "slide_number": 1,
                "title": title,
                "bullet_points": ["Research Presentation", "Generated automatically"],
                "narration": f"Welcome to this presentation about {title}.",
                "notes": "",
                "visual_suggestion": "Title slide"
            }
        ]
        
        section_titles = ["Introduction", "Background", "Methods", "Results", "Conclusion"]
        
        for i, section_title in enumerate(section_titles):
            start = i * chunk_size
            end = start + chunk_size
            chunk_words = words[start:end] if start < len(words) else []
            chunk_text = " ".join(chunk_words[:100])
            
            slides.append({
                "slide_number": i + 2,
                "title": section_title,
                "bullet_points": [chunk_text[:200] if chunk_text else f"Content for {section_title}"],
                "narration": f"In this section about {section_title}, we discuss the key points. {chunk_text[:300]}",
                "notes": "",
                "visual_suggestion": f"Visual for {section_title}"
            })
        
        return slides


async def generate_slides(
    text: str,
    sections: List[Dict],
    style: str = "concise",
    title: str = "Research Presentation"
) -> List[Dict]:
    """Main function to generate slide script"""
    generator = SlideGenerator(style=style)
    return await generator.generate_slide_script(text, sections, title)
