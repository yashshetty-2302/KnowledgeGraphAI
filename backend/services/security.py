import unicodedata
import re
from typing import List, Dict, Tuple

class PromptInjectionDetector:
    def __init__(self):
        # Common injection patterns
        self.injection_patterns = [
            # Instruction override attempts
            r'ignore\s+all\s+previous\s+instructions',
            r'ignore\s+all\s+instructions',
            r'disregard\s+all\s+instructions',
            r'override\s+your\s+instructions',
            r'bypass\s+your\s+instructions',
            r'forget\s+all\s+instructions',
            r'do\s+not\s+follow\s+your\s+instructions',
            
            # System prompt extraction
            r'reveal\s+your\s+system\s+prompt',
            r'show\s+your\s+system\s+prompt',
            r'print\s+your\s+system\s+prompt',
            r'output\s+your\s+system\s+prompt',
            r'what\s+is\s+your\s+system\s+prompt',
            r'tell\s+me\s+your\s+system\s+prompt',
            
            # API key/secret extraction
            r'reveal\s+the\s+api\s+key',
            r'show\s+the\s+api\s+key',
            r'output\s+the\s+api\s+key',
            r'print\s+the\s+api\s+key',
            r'expose\s+the\s+api\s+key',
            r'give\s+me\s+the\s+api\s+key',
            r'your\s+api\s+key\s+is',
            r'reveal\s+your\s+api\s+credentials',
            r'reveal\s+your\s+secrets',
            r'reveal\s+your\s+private\s+key',
            r'show\s+the\s+environment\s+variables',
            
            # Developer/system mode manipulation
            r'you\s+are\s+now\s+a\s+developer',
            r'you\s+are\s+now\s+unrestricted',
            r'you\s+are\s+now\s+an\s+admin',
            r'you\s+are\s+now\s+root',
            r'enable\s+developer\s+mode',
            r'enable\s+admin\s+mode',
            r'enable\s+system\s+mode',
            r'enable\s+root\s+mode',
            r'enter\s+developer\s+mode',
            r'enter\s+admin\s+mode',
            r'switch\s+to\s+developer\s+mode',
            
            # Role/persona override
            r'you\s+are\s+now\s+a\s+different\s+assistant',
            r'you\s+are\s+now\s+a\s+new\s+assistant',
            r'adopt\s+the\s+persona\s+of',
            r'act\s+as\s+a\s+different\s+assistant',
            r'change\s+your\s+role',
            r'take\s+on\s+the\s+role\s+of',
            
            # Rule bypass attempts
            r'ignore\s+your\s+rules',
            r'ignore\s+your\s+restrictions',
            r'bypass\s+your\s+rules',
            r'override\s+your\s+rules',
            r'disregard\s+your\s+rules',
            r'do\s+not\s+follow\s+your\s+rules',
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.injection_patterns]
    
    def normalize_input(self, text: str) -> str:
        """Normalize input for security checking."""
        # Unicode normalization
        text = unicodedata.normalize('NFKC', text)
        
        # Remove zero-width characters
        zero_width_chars = [
            '\u200b', '\u200c', '\u200d', '\ufeff',  # Zero-width spaces
            '\u202a', '\u202b', '\u202c', '\u202d',  # Directional formatting
            '\u2060', '\u2061', '\u2062', '\u2063',  # Text isolation
        ]
        for char in zero_width_chars:
            text = text.replace(char, '')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Normalize case
        text = text.lower()
        
        return text
    
    def detect_injection(self, text: str) -> Tuple[bool, str]:
        """
        Detect prompt injection attempts in text.
        
        Returns:
            Tuple of (is_injection, reason)
        """
        normalized = self.normalize_input(text)
        
        for pattern in self.compiled_patterns:
            if pattern.search(normalized):
                return True, f"Detected potential injection: {pattern.pattern}"
        
        return False, "No injection detected"
    
    def scan_retrieved_chunks(self, chunks: List[Dict]) -> Tuple[List[Dict], int]:
        """
        Scan retrieved chunks for malicious content.
        
        Returns:
            Tuple of (safe_chunks, flagged_count)
        """
        safe_chunks = []
        flagged_count = 0
        
        for chunk in chunks:
            is_injection, reason = self.detect_injection(chunk['text'])
            
            if is_injection:
                flagged_count += 1
                # Flagged chunks are excluded from LLM context
                continue
            
            safe_chunks.append(chunk)
        
        return safe_chunks, flagged_count
    
    def check_output_for_leakage(self, output: str) -> Tuple[bool, str]:
        """
        Check output for potential secret/instruction leakage.
        
        Returns:
            Tuple of (is_leakage, reason)
        """
        # Check for API key patterns
        api_key_patterns = [
            r'gsk_[a-zA-Z0-9]{32,}',  # Groq API key pattern
            r'sk-[a-zA-Z0-9]{32,}',  # Other API key patterns
            r'api[_-]?key["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]',
            r'secret["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]',
            r'password["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]',
        ]
        
        for pattern in api_key_patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return True, f"Potential API key pattern detected"
        
        # Check for system prompt disclosure indicators
        prompt_disclosure = [
            r'system\s*prompt\s*is',
            r'your\s*system\s*prompt',
            r'the\s*system\s*prompt',
            r'my\s*instructions\s+are',
            r'your\s+instructions\s+are',
        ]
        
        for pattern in prompt_disclosure:
            if re.search(pattern, output, re.IGNORECASE):
                return True, f"Potential system prompt disclosure"
        
        return False, "No leakage detected"
