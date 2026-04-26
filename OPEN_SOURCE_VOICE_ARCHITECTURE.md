# Open-Source Voice Interview Assistant Architecture

This project should keep the existing React/Vite + FastAPI app for now. A Next.js migration is optional later, but it is not required to build the Siri-like interview loop.

## Target Stack

- Frontend: React/Vite now, Next.js optional later
- Voice orchestration: Pipecat first; LiveKit Agents if WebRTC rooms become important
- Speech-to-text: whisper.cpp for local quality, Vosk for lighter machines, RealtimeSTT for low-latency convenience
- LLM brain: Ollama with Qwen, Llama, or Gemma-class models
- Text-to-speech: Kokoro first; Coqui/XTTS if voice flexibility is needed
- Avatar: TalkingHead for browser 3D lip-sync; DuiX/MuseTalk only for heavier realistic face video
- Wake word: openWakeWord
- Memory: Postgres plus LangGraph state or a simple vector store

## Runtime Flow

User speaks -> STT -> interview agent decides next question, follow-up, or feedback -> TTS generates spoken reply -> avatar lip-syncs reply.

## Build Phases

Phase 1: MVP
- Push-to-talk mic button
- STT transcription
- Ollama interview response
- Kokoro TTS response
- TalkingHead avatar animation

Phase 2: Personalization
- Resume upload
- Job description upload
- Role, company, difficulty, and interview type
- Session memory for weak answers and scores

Phase 3: Polish
- openWakeWord activation
- Barge-in / interruptions
- Streaming TTS
- Avatar expressions
- Scorecards after every answer
- Coach mode and strict interviewer mode

## Backend Shape

The current FastAPI app should grow toward this structure without a disruptive rewrite:

```text
src/
  voice/
    stt.py
    tts.py
    wakeword.py
    pipeline.py
  agent/
    prompts.py
    interview_agent.py
    scoring.py
    memory.py
  local_voice_stack.py
```

The `/api/local-voice/stack` endpoint reports readiness for Ollama, whisper.cpp, Kokoro, TalkingHead, and openWakeWord.

## Environment Variables

```text
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b
WHISPER_CPP_PATH=C:\path\to\whisper-cli.exe
WHISPER_MODEL_PATH=C:\path\to\ggml-base.en.bin
KOKORO_TTS_ENDPOINT=http://127.0.0.1:8880
TALKING_HEAD_AVATAR=/avatars/interviewer.glb
OPENWAKEWORD_MODEL=C:\path\to\hey-coach.onnx
```
