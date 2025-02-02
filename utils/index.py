import re
from typing import Optional
from functools import lru_cache
from utils.logger import get_logger

logger = get_logger()

# Sık kullanılan regex kalıplarını önceden derle
THINK_TAG_PATTERN = re.compile(r'</think>.*$', re.DOTALL)
JSON_BLOCK_PATTERN = re.compile(r'```json(.*?)```', re.DOTALL)
NEWLINE_PATTERN = re.compile(r'\s+')

@lru_cache(maxsize=1000)
def clean_unicode(text: str) -> str:
    """Unicode karakterleri temizle"""
    try:
        return text.encode('ascii', 'ignore').decode('ascii')
    except Exception as e:
        logger.error(f"Unicode cleaning error: {e}")
        return text

def clean_think_tags(text: str) -> str:
    """Düşünme etiketlerini temizle"""
    try:
        match = THINK_TAG_PATTERN.search(text)
        return match.group(0).replace('</think>', '').strip() if match else text
    except Exception as e:
        logger.error(f"Think tag cleaning error: {e}")
        return text

def clean_json_blocks(text: str) -> str:
    """JSON bloklarını temizle"""
    try:
        match = JSON_BLOCK_PATTERN.search(text)
        return match.group(1).strip() if match else text
    except Exception as e:
        logger.error(f"JSON block cleaning error: {e}")
        return text

def clean_whitespace(text: str) -> str:
    """Gereksiz boşlukları ve satır sonlarını temizle"""
    try:
        return NEWLINE_PATTERN.sub(' ', text).strip()
    except Exception as e:
        logger.error(f"Whitespace cleaning error: {e}")
        return text

def outputCleaner(output: str) -> str:
    """
    Çıktı metnini temizle ve formatla
    
    Args:
        output: Temizlenecek metin
        
    Returns:
        Temizlenmiş metin
        
    Example:
        >>> outputCleaner("```json\\n{\\n  'key': 'value'\\n}\\n```")
        "{'key': 'value'}"
    """
    if not isinstance(output, str):
        logger.warning(f"Invalid input type: {type(output)}")
        return str(output)

    try:
        # Sıralı temizleme işlemleri
        output = clean_unicode(output)
        output = clean_think_tags(output)
        output = clean_json_blocks(output)
        output = clean_whitespace(output)
        
        return output
    except Exception as e:
        logger.error(f"Output cleaning error: {e}")
        return output

def sanitize_input(text: str) -> str:
    """
    Kullanıcı girdisini güvenli hale getir
    
    Args:
        text: Temizlenecek metin
        
    Returns:
        Temizlenmiş metin
    """
    if not isinstance(text, str):
        return str(text)

    # Tehlikeli karakterleri temizle
    text = re.sub(r'[<>]', '', text)
    # Kontrol karakterlerini kaldır
    text = ''.join(char for char in text if ord(char) >= 32)
    return text.strip()

def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """
    Metni belirli bir uzunlukta kes
    
    Args:
        text: Kesilecek metin
        max_length: Maksimum uzunluk
        suffix: Kesme sonrası eklenecek son ek
        
    Returns:
        Kesilmiş metin
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].strip() + suffix

def extract_code_blocks(text: str) -> list:
    """
    Metindeki kod bloklarını çıkar
    
    Args:
        text: İşlenecek metin
        
    Returns:
        Kod bloklarının listesi
    """
    pattern = r'```(?:\w+\n)?(.*?)```'
    matches = re.finditer(pattern, text, re.DOTALL)
    return [match.group(1).strip() for match in matches]

# Export
export = {
    "outputCleaner": outputCleaner,
    "sanitize_input": sanitize_input,
    "truncate_text": truncate_text,
    "extract_code_blocks": extract_code_blocks
}