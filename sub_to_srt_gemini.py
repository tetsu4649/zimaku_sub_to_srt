import os
import sys
import time
import json
import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import google.generativeai as genai

@dataclass
class SubtitleEntry:
    start_time: str
    end_time: str
    text: str

@dataclass
class TranslationResult:
    language: str
    translations: List[str]
    success: bool
    error_message: Optional[str] = None

class SubToSrtGeminiTranslator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Language mappings
        self.languages = {
            'en': 'English',
            'ko': 'Korean', 
            'zh-tw': 'Traditional Chinese',
            'zh-cn': 'Simplified Chinese',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
    
    def parse_sub_file(self, file_path: str) -> List[SubtitleEntry]:
        """Parse SUB file and extract subtitle entries"""
        subtitles = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='shift_jis') as file:
                lines = file.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            # Check if line contains timestamp
            if ',' in line and '.' in line:
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
                        subtitles.append(SubtitleEntry(start_time, end_time, text))
                    continue
            
            i += 1
        
        return subtitles
    
    def convert_time_format(self, time_str: str) -> str:
        """Convert SUB time format to SRT time format"""
        time_str = time_str.strip()
        parts = time_str.split(':')
        
        if len(parts) != 3:
            return time_str
        
        hours = parts[0]
        minutes = parts[1]
        sec_parts = parts[2].split('.')
        seconds = sec_parts[0]
        
        if len(sec_parts) > 1:
            milliseconds = sec_parts[1][:3].ljust(3, '0')
        else:
            milliseconds = "000"
        
        return f"{hours}:{minutes}:{seconds},{milliseconds}"
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of tokens for text"""
        # Rough estimation: 1 token ≈ 0.75 words for Japanese
        return len(text.split()) + len(text) // 4
    
    def rate_limit_wait(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            print(f"Rate limiting: waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def translate_batch_simultaneous(self, subtitles: List[SubtitleEntry], 
                                   target_languages: List[str]) -> Dict[str, TranslationResult]:
        """Translate all subtitles to multiple languages in one request"""
        
        # Prepare the text
        subtitle_text = ""
        for i, subtitle in enumerate(subtitles, 1):
            subtitle_text += f"字幕{i}: {subtitle.text}\n"
        
        # Estimate tokens
        input_tokens = self.estimate_tokens(subtitle_text)
        estimated_output = input_tokens * len(target_languages) * 1.5
        
        print(f"Estimated tokens: Input={input_tokens}, Output≈{estimated_output}, Total≈{input_tokens + estimated_output}")
        
        if input_tokens + estimated_output > 30000:  # Conservative limit for free tier
            print("Warning: Estimated token usage is high. Consider using batch mode.")
        
        # Prepare language list
        lang_names = [self.languages.get(lang, lang) for lang in target_languages]
        
        prompt = f"""
以下の日本語字幕を以下の言語に翻訳してください：
{', '.join([f"{i+1}. {name}" for i, name in enumerate(lang_names)])}

全体の文脈を考慮し、一貫性のある自然な翻訳を行ってください。
専門用語や固有名詞は適切に翻訳し、各言語の文化的ニュアンスに配慮してください。

字幕テキスト：
{subtitle_text}

出力形式（必須）：
字幕1:
- {lang_names[0]}: [翻訳]
{f"- {lang_names[1]}: [翻訳]" if len(lang_names) > 1 else ""}
{f"- {lang_names[2]}: [翻訳]" if len(lang_names) > 2 else ""}

字幕2:
- {lang_names[0]}: [翻訳]
{f"- {lang_names[1]}: [翻訳]" if len(lang_names) > 1 else ""}
{f"- {lang_names[2]}: [翻訳]" if len(lang_names) > 2 else ""}

(続く...)
"""
        
        try:
            self.rate_limit_wait()
            print("Sending request to Gemini 2.5 Pro...")
            
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("Empty response from Gemini API")
            
            print("Parsing response...")
            return self._parse_simultaneous_response(response.text, target_languages, len(subtitles))
            
        except Exception as e:
            error_msg = f"Simultaneous translation failed: {str(e)}"
            print(error_msg)
            
            # Return error results for all languages
            results = {}
            for lang in target_languages:
                results[lang] = TranslationResult(
                    language=lang,
                    translations=[],
                    success=False,
                    error_message=error_msg
                )
            return results
    
    def translate_batch_sequential(self, subtitles: List[SubtitleEntry], 
                                 target_languages: List[str]) -> Dict[str, TranslationResult]:
        """Translate to each language sequentially"""
        results = {}
        
        # Prepare the text once
        subtitle_text = ""
        for i, subtitle in enumerate(subtitles, 1):
            subtitle_text += f"字幕{i}: {subtitle.text}\n"
        
        for lang in target_languages:
            lang_name = self.languages.get(lang, lang)
            
            prompt = f"""
以下の日本語字幕を{lang_name}に翻訳してください。

全体の文脈を考慮し、一貫性のある自然な翻訳を行ってください。
専門用語や固有名詞は適切に翻訳し、{lang_name}の文化的ニュアンスに配慮してください。

字幕テキスト：
{subtitle_text}

出力形式（必須）：
字幕1: [翻訳]
字幕2: [翻訳]
字幕3: [翻訳]
(続く...)
"""
            
            try:
                self.rate_limit_wait()
                print(f"Translating to {lang_name}...")
                
                response = self.model.generate_content(prompt)
                
                if not response.text:
                    raise Exception("Empty response from Gemini API")
                
                translations = self._parse_sequential_response(response.text, len(subtitles))
                
                results[lang] = TranslationResult(
                    language=lang,
                    translations=translations,
                    success=True
                )
                
                print(f"✓ {lang_name} translation completed ({len(translations)} entries)")
                
            except Exception as e:
                error_msg = f"Translation to {lang_name} failed: {str(e)}"
                print(f"✗ {error_msg}")
                
                results[lang] = TranslationResult(
                    language=lang,
                    translations=[],
                    success=False,
                    error_message=error_msg
                )
        
        return results
    
    def _parse_simultaneous_response(self, response_text: str, target_languages: List[str], 
                                   num_subtitles: int) -> Dict[str, TranslationResult]:
        """Parse simultaneous translation response"""
        results = {}
        
        # Initialize results
        for lang in target_languages:
            results[lang] = TranslationResult(
                language=lang,
                translations=[],
                success=False
            )
        
        try:
            # Split response by subtitle entries
            lines = response_text.split('\n')
            current_subtitle = -1
            
            for line in lines:
                line = line.strip()
                
                # Check for subtitle header
                subtitle_match = re.match(r'字幕(\d+):', line)
                if subtitle_match:
                    current_subtitle = int(subtitle_match.group(1)) - 1
                    continue
                
                # Check for translations
                for i, lang in enumerate(target_languages):
                    lang_name = self.languages.get(lang, lang)
                    if line.startswith(f'- {lang_name}:'):
                        translation = line.replace(f'- {lang_name}:', '').strip()
                        # Remove brackets if present
                        translation = re.sub(r'^\[|\]$', '', translation)
                        
                        # Ensure we have enough entries
                        while len(results[lang].translations) <= current_subtitle:
                            results[lang].translations.append("")
                        
                        if current_subtitle >= 0:
                            results[lang].translations[current_subtitle] = translation
            
            # Mark successful translations
            for lang in target_languages:
                if len(results[lang].translations) == num_subtitles:
                    results[lang].success = True
                else:
                    results[lang].error_message = f"Expected {num_subtitles} translations, got {len(results[lang].translations)}"
            
        except Exception as e:
            for lang in target_languages:
                results[lang].error_message = f"Failed to parse response: {str(e)}"
        
        return results
    
    def _parse_sequential_response(self, response_text: str, num_subtitles: int) -> List[str]:
        """Parse sequential translation response"""
        translations = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Look for numbered subtitle entries
            match = re.match(r'字幕\d+:\s*(.+)', line)
            if match:
                translation = match.group(1)
                # Remove brackets if present
                translation = re.sub(r'^\[|\]$', '', translation)
                translations.append(translation)
        
        # If regex didn't work, try line-by-line
        if len(translations) < num_subtitles:
            translations = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('字幕') and ':' in line:
                    # Extract text after colon
                    translation = line.split(':', 1)[1].strip()
                    # Remove brackets if present
                    translation = re.sub(r'^\[|\]$', '', translation)
                    if translation:
                        translations.append(translation)
        
        return translations
    
    def create_srt_content(self, subtitles: List[SubtitleEntry], translations: List[str]) -> str:
        """Create SRT format content"""
        srt_content = ""
        
        for i, (subtitle, translation) in enumerate(zip(subtitles, translations), 1):
            start_srt = self.convert_time_format(subtitle.start_time)
            end_srt = self.convert_time_format(subtitle.end_time)
            
            srt_content += f"{i}\n"
            srt_content += f"{start_srt} --> {end_srt}\n"
            srt_content += f"{translation}\n\n"
        
        return srt_content
    
    def convert_sub_to_srt(self, input_file: str, target_languages: List[str], 
                          mode: str = 'batch', output_dir: str = None):
        """Main conversion function"""
        
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.")
            return
        
        print(f"Parsing SUB file: {input_file}")
        subtitles = self.parse_sub_file(input_file)
        print(f"Found {len(subtitles)} subtitle entries")
        
        if not subtitles:
            print("No subtitles found in the file.")
            return
        
        if output_dir is None:
            output_dir = os.path.dirname(input_file)
        
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        
        # Validate languages
        valid_languages = []
        for lang in target_languages:
            if lang in self.languages:
                valid_languages.append(lang)
            else:
                print(f"Warning: Language '{lang}' not supported. Available: {list(self.languages.keys())}")
        
        if not valid_languages:
            print("Error: No valid target languages specified.")
            return
        
        print(f"Target languages: {[self.languages[lang] for lang in valid_languages]}")
        print(f"Translation mode: {mode}")
        
        # Perform translation
        if mode == 'simultaneous':
            results = self.translate_batch_simultaneous(subtitles, valid_languages)
        else:  # batch mode
            results = self.translate_batch_sequential(subtitles, valid_languages)
        
        # Generate output files
        successful_translations = 0
        
        for lang, result in results.items():
            if result.success and len(result.translations) == len(subtitles):
                # Create SRT file
                srt_content = self.create_srt_content(subtitles, result.translations)
                
                output_file = os.path.join(output_dir, f"{base_name}_{lang}.srt")
                
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(srt_content)
                
                print(f"✓ Created: {output_file}")
                successful_translations += 1
            else:
                lang_name = self.languages.get(lang, lang)
                print(f"✗ Failed to create {lang_name} SRT: {result.error_message}")
        
        print(f"\nTranslation completed: {successful_translations}/{len(valid_languages)} languages successful")

def main():
    if len(sys.argv) < 3:
        print("Usage: python sub_to_srt_gemini.py <input_file.sub> <languages> [options]")
        print("Languages: en,ko,zh-tw (comma-separated)")
        print("Options:")
        print("  --mode [batch|simultaneous]  Translation mode (default: batch)")
        print("  --output-dir <directory>     Output directory")
        print("  --api-key <key>             Gemini API key")
        print("\nExamples:")
        print("  python sub_to_srt_gemini.py sample.sub en,ko,zh-tw")
        print("  python sub_to_srt_gemini.py sample.sub en --mode simultaneous")
        print("  python sub_to_srt_gemini.py sample.sub en,ko --output-dir ./output")
        print("\nSupported languages:")
        print("  en: English, ko: Korean, zh-tw: Traditional Chinese")
        print("  zh-cn: Simplified Chinese, es: Spanish, fr: French, de: German")
        return
    
    input_file = sys.argv[1]
    languages_str = sys.argv[2]
    target_languages = [lang.strip() for lang in languages_str.split(',')]
    
    # Parse options
    mode = 'batch'
    output_dir = None
    api_key = None
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--mode' and i + 1 < len(sys.argv):
            mode = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output-dir' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--api-key' and i + 1 < len(sys.argv):
            api_key = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    try:
        translator = SubToSrtGeminiTranslator(api_key=api_key)
        translator.convert_sub_to_srt(input_file, target_languages, mode, output_dir)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='AIzaSyBrxql1gZ4kAP13ewqXPm0QwK-9LNzqSGY'")
        print("Or use --api-key option")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()