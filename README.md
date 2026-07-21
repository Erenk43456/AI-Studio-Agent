# AI-Studio-Agent 🤖

Python ile geliştirilmiş, local çalışan modüler AI Agent masaüstü asistanı.

AI-Studio-Agent; LLM tabanlı karar verme, tool kullanımı, hafıza yönetimi ve konuşma geçmişi özelliklerini bir araya getirerek kişiselleştirilebilir bir yapay zeka asistan altyapısı sunar.

Proje tamamen local çalışır. Kullanıcı verileri, hafıza kayıtları ve konuşma geçmişi cihaz üzerinde tutulur.

---

# Özellikler

- 🤖 Local LLM desteği (Ollama + Qwen2.5)
- 🧠 Planner Agent ile görev analizi ve yönlendirme
- 🛠 Tool Agent ile araç çalıştırma sistemi
- 💬 Chat Agent ile doğal dil konuşma desteği
- 💾 Memory sistemi ile kalıcı bilgi saklama
- 📝 Conversation history yönetimi
- 🔌 Tool Registry mimarisi
- 🧮 Calculator Tool
- 📁 File Operation Tool
- 🖥 PySide6 masaüstü kullanıcı arayüzü
- ⚡ QThread ile arka plan işlem yönetimi
- 🧪 Pytest otomatik test sistemi
- 📦 Windows EXE desteği

---

# Proje Mimarisi

```text
User
 |
 v
Desktop GUI
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

# Agent Yapısı

## Planner Agent

- Kullanıcı isteğini analiz eder.
- Uygun agent veya tool seçimini yapar.
- JSON tabanlı görev planı oluşturur.

Örnek:

```json
{
 "tool":"calculator",
 "operation":"add",
 "numbers":[20,30]
}
```

---

## Tool Agent

Seçilen araçları çalıştırır.

Desteklenen araçlar:

- Calculator
- Memory
- File Operations

---

## Chat Agent

Normal sohbet isteklerini yönetir.

Local LLM üzerinden doğal dil cevapları üretir.

---

# Kullanılan Teknolojiler

- Python 3.12+
- PySide6
- Ollama
- Qwen2.5 Local LLM
- Requests
- JSON
- Pytest
- PyInstaller

---

# Kurulum

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

# Local LLM Kurulumu

Bu proje Ollama üzerinden local LLM kullanır.

Qwen2.5 modelini indirmek için:

```bash
ollama pull qwen2.5:3b
```

Ollama servisini başlatın:

```bash
ollama serve
```

---

# Kullanım

GUI uygulamasını başlatmak için:

```bash
python -m app.gui
```

Örnek:

```
Kullanıcı:
20 ile 40'ı topla

AI:
60
```

Memory örneği:

```
Kullanıcı:
Benim adım Eren

AI:
İsim kaydedildi.
```

Daha sonra:

```
Kullanıcı:
Benim adım ne

AI:
eren
```

---

# Windows EXE Kullanımı

Hazırlanan executable sürümü ile uygulama Python kurulumu olmadan çalıştırılabilir.

```
AI-Studio-Agent.exe
```

Not:

Local AI modeli kullanıldığı için bilgisayarda:

- Ollama
- qwen2.5:3b modeli

kurulu olmalıdır.

---

# Testler

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

# Veri Gizliliği

Kullanıcı hafızası ve konuşma geçmişi lokal olarak saklanır.

Aşağıdaki dosyalar GitHub'a gönderilmez:

```
data/memory.json
data/conversation.json
```

Bu sayede kişisel kullanıcı verileri kaynak koddan ayrı tutulur.

---

# Gelecek Geliştirmeler

- RAG tabanlı bilgi sistemi
- Plugin mimarisi
- Sesli asistan desteği
- Daha gelişmiş uzun süreli hafıza
- Model değiştirme sistemi
- Web tabanlı dashboard
- Multi-agent koordinasyonu

---

# Proje Hakkında

AI-Studio-Agent; agent mimarileri, local LLM kullanımı, tool entegrasyonu ve hafıza sistemleri üzerine geliştirilmiş bir yapay zeka asistan prototipidir.

Amaç; kullanıcı isteklerini analiz edebilen, uygun araçları seçebilen ve lokal olarak çalışan modüler bir AI sistemi oluşturmaktır.