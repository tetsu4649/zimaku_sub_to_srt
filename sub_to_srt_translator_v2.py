import re
import os
import sys
from typing import List, Tuple
import requests
import json
import time
import urllib.parse

class SubToSrtTranslator:
    def __init__(self):
        self.base_url = "https://translate.googleapis.com/translate_a/single"
    
    def parse_sub_file(self, file_path: str) -> List[Tuple[str, str, str]]:
        """
        Parse SUB file and extract subtitle entries
        Returns list of tuples: (start_time, end_time, text)
        """
        subtitles = []
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check if line contains timestamp
            if ',' in line and '.' in line:
                # Extract start and end times
                times = line.split(',')
                if len(times) == 2:
                    start_time = times[0].strip()
                    end_time = times[1].strip()
                    
                    # Get subtitle text (next non-empty line)
                    i += 1
                    text = ""
                    while i < len(lines) and lines[i].strip():
                        text += lines[i].strip()
                        i += 1
                    
                    if text:
                        subtitles.append((start_time, end_time, text))
                    continue
            
            i += 1
        
        return subtitles
    
    def convert_time_format(self, time_str: str) -> str:
        """
        Convert SUB time format to SRT time format
        SUB: 00:00:06.7000000
        SRT: 00:00:06,700
        """
        # Remove leading/trailing whitespace
        time_str = time_str.strip()
        
        # Split by colon and period
        parts = time_str.split(':')
        if len(parts) != 3:
            return time_str
        
        hours = parts[0]
        minutes = parts[1]
        
        # Handle seconds and milliseconds
        sec_parts = parts[2].split('.')
        seconds = sec_parts[0]
        
        if len(sec_parts) > 1:
            # Convert 7 digits to 3 digits for milliseconds
            milliseconds = sec_parts[1][:3].ljust(3, '0')
        else:
            milliseconds = "000"
        
        return f"{hours}:{minutes}:{seconds},{milliseconds}"
    
    def translate_text_google(self, text: str, src_lang='ja', dest_lang='en') -> str:
        """
        Translate text using Google Translate API (free endpoint)
        """
        try:
            # Prepare parameters
            params = {
                'client': 'gtx',
                'sl': src_lang,
                'tl': dest_lang,
                'dt': 't',
                'q': text
            }
            
            # Make request
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            # Extract translated text
            if result and len(result) > 0 and len(result[0]) > 0:
                translated_text = ""
                for translation in result[0]:
                    if len(translation) > 0:
                        translated_text += translation[0]
                return translated_text
            else:
                return text
                
        except Exception as e:
            print(f"Translation error for '{text[:50]}...': {e}")
            return text
    
    def translate_text_batch(self, texts: List[str], src_lang='ja', dest_lang='en') -> List[str]:
        """
        Translate multiple texts with rate limiting
        """
        translated_texts = []
        
        for i, text in enumerate(texts):
            print(f"Translating {i+1}/{len(texts)}: {text[:50]}...")
            translated = self.translate_text_google(text, src_lang, dest_lang)
            translated_texts.append(translated)
            
            # Rate limiting - wait between requests
            if i < len(texts) - 1:
                time.sleep(0.5)
        
        return translated_texts
    
    def create_srt_content(self, subtitles: List[Tuple[str, str, str]], translate: bool = True) -> str:
        """
        Create SRT format content from subtitle data
        """
        srt_content = ""
        
        if translate:
            # Extract all texts for batch translation
            texts = [text for _, _, text in subtitles]
            translated_texts = self.translate_text_batch(texts)
        
        for i, (start_time, end_time, text) in enumerate(subtitles):
            # Convert time format
            start_srt = self.convert_time_format(start_time)
            end_srt = self.convert_time_format(end_time)
            
            # Use translated text if available
            if translate and i < len(translated_texts):
                display_text = translated_texts[i]
            else:
                display_text = text
            
            # Create SRT entry
            srt_content += f"{i+1}\n"
            srt_content += f"{start_srt} --> {end_srt}\n"
            srt_content += f"{display_text}\n\n"
        
        return srt_content
    
    def convert_sub_to_srt(self, input_file: str, output_file: str = None, translate: bool = True):
        """
        Convert SUB file to SRT format with optional translation
        """
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            return
        
        # Parse SUB file
        print("Parsing SUB file...")
        subtitles = self.parse_sub_file(input_file)
        print(f"Found {len(subtitles)} subtitle entries.")
        
        if not subtitles:
            print("No subtitles found in the file.")
            return
        
        # Create output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            suffix = "_translated" if translate else "_converted"
            output_file = f"{base_name}{suffix}.srt"
        
        # Generate SRT content
        print("Converting to SRT format...")
        if translate:
            print("Translating Japanese text to English...")
        
        srt_content = self.create_srt_content(subtitles, translate)
        
        # Write SRT file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(srt_content)
        
        print(f"Successfully created: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python sub_to_srt_translator_v2.py <input_file.sub> [output_file.srt] [--no-translate]")
        print("Example: python sub_to_srt_translator_v2.py sample.sub")
        print("Example: python sub_to_srt_translator_v2.py sample.sub output.srt")
        print("Example: python sub_to_srt_translator_v2.py sample.sub --no-translate")
        return
    
    input_file = sys.argv[1]
    output_file = None
    translate = True
    
    # Parse command line arguments
    if len(sys.argv) > 2:
        for arg in sys.argv[2:]:
            if arg == "--no-translate":
                translate = False
            elif not arg.startswith("--"):
                output_file = arg
    
    # Create converter instance
    converter = SubToSrtTranslator()
    
    # Convert file
    converter.convert_sub_to_srt(input_file, output_file, translate)

if __name__ == "__main__":
    main()