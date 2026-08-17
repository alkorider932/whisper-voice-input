# 🎙️ Локальный голосовой ввод на macOS (Whisper MLX)

> Фоновый сервис голосового набора текста на базе нейросети Whisper Turbo, оптимизированной для чипов Apple Silicon (M1/M2/M3/M4).

## ⚡ Как это работает:
1. Нажимаете клавишу **Ctrl** два раза подряд — звучит сигнал старта записи.
2. Надиктовываете текст в микрофон.
3. Нажимаете **Ctrl** два раза подряд еще раз — нейросеть локально расшифровывает речь и мгновенно печатает текст в любое активное поле (Telegram, браузер, VS Code, Notion).

## 🚀 Быстрый старт:
Подробная интерактивная инструкция находится в файле `GUIDE_WHISPER_VOICE_INPUT.html`.

```bash
# Установка окружения
/opt/homebrew/bin/python3.11 -m venv venv || python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install mlx-whisper sounddevice soundfile numpy pynput pyobjc-framework-Quartz

# Запуск сервиса
./venv/bin/python3 voice_input.py
```
