# Sesli Arayüzlü Yapay Zeka Asistanı

Hem metin hem de ses ile etkileşim kurabilen, bellek yönetimi ve çeşitli API entegrasyonları içeren Python tabanlı bir yapay zeka asistanı.

## ⚠️ Sorumluluk Reddi

Bu yazılım "olduğu gibi" sunulmaktadır ve hiçbir garanti verilmemektedir. Bu yazılımı kullanarak:

- Tüm riski kendiniz üstlendiğinizi
- Yazarların bilgisayarınıza, verilerinize veya diğer mallarınıza gelebilecek zararlardan sorumlu olmadığını
- Yazarların yazılımın veya komutlarının yanlış kullanımından sorumlu olmadığını
- Sistem komutlarının sisteminizi değiştirebileceğini ve dikkatli kullanılması gerektiğini

kabul etmiş olursunuz.

## Özellikler

- Metin ve ses etkileşim modları
- Uyanma kelimesi algılama ("Hey Jarvis")
- SQLite veritabanı ile bellek yönetimi
- Çeşitli API entegrasyonları:
  - Hava durumu bilgisi
  - Borsa fiyatları
  - Wikipedia özetleri
  - Haber güncellemeleri
- Sistem komutları çalıştırma yeteneği
- URL açma işlevselliği

## Gereksinimler

- Python 3.8+
- PyTorch
- transformers
- SpeechRecognition
- pyttsx3
- sentence-transformers
- Diğer bağımlılıklar requirements.txt içinde

## Kurulum

1. Depoyu klonlayın:
```bash
git clone https://github.com/yusufekorman/ai-assistant.git
cd ai-assistant
```

2. Sanal ortam oluşturun ve etkinleştirin:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate  # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. API anahtarlarını yapılandırın:
`secrets.json` dosyası oluşturun ve API anahtarlarınızı ekleyin:
```json
{
    "weather_api_key": "openweathermap_anahtarınız"
}
```

## Kullanım

1. Programı başlatın:
```bash
python main.py
```

2. Giriş modunu seçin:
   - Metin modu (1): Sorgularınızı doğrudan yazın
   - Ses modu (2): "Hey Jarvis" ile başlayan sesli komutları kullanın

3. Kullanılabilir komutlar:
   - Hava durumu: "[şehir] hava durumu nasıl?"
   - Borsa: "[hisse sembolü] fiyatı nedir?"
   - Wikipedia: "[konu] hakkında bilgi ver"
   - Haberler: "[konu] ile ilgili haberleri göster"
   - Sistem: Çeşitli sistem komutları ve URL açma

## Proje Yapısı

- `main.py`: Ana uygulama dosyası
- `voice_auth.py`: Ses doğrulama ve uyanma kelimesi algılama
- `utils/`:
  - `database_pool.py`: SQLite veritabanı bağlantı yönetimi
  - `vector_memory_manager.py`: Vektör benzerliği ile bellek yönetimi
  - `execute_response.py`: Yanıt yürütme ve API entegrasyonları
  - `query.py`: LLM sorgu işleme

## Katkıda Bulunma

Sorunları bildirmekten, depoyu çatallamaktan ve iyileştirmeler için pull request göndermekten çekinmeyin.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın. 