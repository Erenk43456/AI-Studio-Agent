# AI-Studio-Agent

Python ile geliştirilmiş, local çalışan modüler bir AI Agent framework.

Bu proje; LLM tabanlı karar verme, tool kullanımı, hafıza yönetimi ve konuşma geçmişi özelliklerini bir araya getirerek kişiselleştirilebilir bir AI asistan altyapısı sunar.

## Özellikler

- Local LLM desteği (Ollama + Qwen2.5)
- Planner Agent ile görev analizi ve yönlendirme
- Tool Agent ile araç çalıştırma sistemi
- Chat Agent ile doğal dil konuşma desteği
- Memory sistemi ile kalıcı bilgi saklama
- Conversation history yönetimi
- Tool Registry mimarisi
- Calculator tool
- File operation tool
- Pytest ile otomatik test sistemi

---

## Proje Mimarisi

```text
User
 |
 v
Planner Agent
 |
 +----------------+
 |                |
 v                v
Tool Agent     Chat Agent
 |
 +----------------+
 |       |        |
 v       v        v
Memory Calculator File Tool
```

---

## Agent Yapısı

### Planner Agent

- Kullanıcı isteğini analiz eder.
- Uygun agent veya tool seçimini yapar.
- JSON tabanlı görev planı oluşturur.

### Tool Agent

- Seçilen araçları çalıştırır.
- Calculator, Memory ve File işlemlerini yönetir.

### Chat Agent

- Normal sohbet isteklerini yönetir.
- Local LLM üzerinden doğal dil cevapları üretir.

---

## Kullanılan Teknolojiler

- Python 3.12+
- Ollama
- Qwen2.5 Local LLM
- Requests
- JSON
- Pytest

---

## Kurulum

Projeyi klonlayın:

```bash
git clone https://github.com/Erenk43456/AI-Studio-Agent.git
```

Proje klasörüne girin:

```bash
cd AI-Studio-Agent
```

Virtual environment oluşturun:

```bash
python -m venv venv
```

Virtual environment aktif edin:

Windows:

```bash
venv\Scripts\activate
```

Bağımlılıkları yükleyin:

```bash
pip install -r requirements.txt
```

---

## Local LLM Kurulumu

Bu proje Ollama üzerinden local LLM kullanır.

Qwen2.5 modelini indirmek için:

```bash
ollama pull qwen2.5:1.5b
```

Ollama servisini başlatın:

```bash
ollama serve
```

---

## Kullanım

Projeyi çalıştırın:

```bash
python main.py
```

Örnek:

```
İstek:
20 ile 40'ı topla

Sonuç:
60
```

Memory örneği:

```
İstek:
Benim adım Eren

Sonuç:
isim kaydedildi.
```

Daha sonra:

```
İstek:
Benim adım ne

Sonuç:
eren
```

---

## Testler

Proje otomatik test desteğine sahiptir.

Testleri çalıştırmak için:

```bash
pytest
```

Örnek çıktı:

```
3 passed
```

Test edilen bileşenler:

- Calculator
- Memory sistemi

---

## Veri Gizliliği

Kullanıcı hafızası ve konuşma geçmişi lokal olarak saklanır.

Aşağıdaki dosyalar GitHub'a gönderilmez:

```
data/memory.json
data/conversation.json
```

Bu sayede kişisel kullanıcı verileri kaynak koddan ayrı tutulur.

---

## Geliştirme Hedefleri

- Web tabanlı kullanıcı arayüzü eklemek
- Yeni tool entegrasyonları geliştirmek
- Daha gelişmiş agent karar mekanizması oluşturmak
- RAG tabanlı bilgi sistemi eklemek
- Daha büyük local modeller ile çalışmak

---

## Proje Hakkında

AI-Studio-Agent; agent mimarileri, local LLM kullanımı, tool entegrasyonu ve hafıza sistemleri üzerine geliştirilmiş bir yapay zeka asistan prototipidir.