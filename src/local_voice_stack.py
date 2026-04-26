import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LocalVoiceConfig:
    ollama_base_url: str
    ollama_model: str
    faster_whisper_model: str
    piper_binary_path: str
    piper_voice_path: str
    openwakeword_model: str
    memory_database_url: str
    livekit_url: str


def get_local_voice_config() -> LocalVoiceConfig:
    return LocalVoiceConfig(
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip(),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b").strip(),
        faster_whisper_model=os.getenv("FASTER_WHISPER_MODEL", "small").strip(),
        piper_binary_path=os.getenv("PIPER_BINARY_PATH", "").strip(),
        piper_voice_path=os.getenv("PIPER_VOICE_PATH", "").strip(),
        openwakeword_model=os.getenv("OPENWAKEWORD_MODEL", "").strip(),
        memory_database_url=os.getenv("MEMORY_DATABASE_URL", "sqlite:///data/interview_memory.db").strip(),
        livekit_url=os.getenv("LIVEKIT_URL", "").strip(),
    )


def _path_ready(value: str) -> bool:
    return bool(value and Path(value).exists())


def _package_ready(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def local_voice_stack_status() -> dict[str, Any]:
    config = get_local_voice_config()
    piper_ready = _path_ready(config.piper_binary_path) and _path_ready(config.piper_voice_path)
    wake_word_ready = _path_ready(config.openwakeword_model) or _package_ready("openwakeword")

    return {
        "goal": "Free/open-source Jarvis-style mock interviewer with voice, wake word, local LLM, TTS, vision cues, scoring, and memory.",
        "recommended_stack": {
            "frontend": "React/Vite now; Next.js optional later",
            "voice_orchestration": "Pipecat first; LiveKit Agents if you want WebRTC rooms",
            "wake_word": "openWakeWord",
            "vad_turn_detection": "Silero VAD or LiveKit turn detector",
            "stt": "faster-whisper",
            "llm": "Ollama with Qwen/Llama/Gemma-class instruct model",
            "tts": "Piper local neural TTS",
            "vision": "MediaPipe Face Landmarker and Pose Landmarker in browser",
            "memory": "SQLite first; PostgreSQL/pgvector later",
        },
        "configured": {
            "ollama": bool(config.ollama_base_url and config.ollama_model),
            "pipecat_package": _package_ready("pipecat"),
            "livekit_agents_package": _package_ready("livekit"),
            "faster_whisper_package": _package_ready("faster_whisper"),
            "silero_vad_package": _package_ready("silero_vad"),
            "piper_binary_and_voice": piper_ready,
            "openwakeword": wake_word_ready,
            "memory_database": bool(config.memory_database_url),
        },
        "env": {
            "ollama_base_url": config.ollama_base_url,
            "ollama_model": config.ollama_model,
            "faster_whisper_model": config.faster_whisper_model,
            "piper_binary_path_set": bool(config.piper_binary_path),
            "piper_voice_path_set": bool(config.piper_voice_path),
            "openwakeword_model_set": bool(config.openwakeword_model),
            "memory_database_url": config.memory_database_url,
            "livekit_url_set": bool(config.livekit_url),
        },
        "phases": [
            {
                "name": "Phase 1 - Working MVP",
                "items": [
                    "Push-to-talk mic in browser",
                    "Transcribe with faster-whisper or current browser speech fallback",
                    "Generate interviewer response with Ollama/local LLM or current backend LLM fallback",
                    "Speak with Piper or current single-voice fallback",
                    "Save session history",
                ],
            },
            {
                "name": "Phase 2 - Jarvis behavior",
                "items": [
                    "Wake word with openWakeWord",
                    "End-of-turn with Silero VAD or LiveKit turn detector",
                    "MediaPipe face/posture coaching",
                    "Filler-word and speaking-pace scoring",
                ],
            },
            {
                "name": "Phase 3 - Personalization",
                "items": [
                    "Resume and job-description memory",
                    "Weak-area tracking across sessions",
                    "Role-specific interview modes",
                    "Coach mode and strict interviewer mode",
                ],
            },
        ],
        "api_keys": {
            "required_for_free_local_stack": [],
            "optional": [
                {
                    "name": "OPENAI_API_KEY",
                    "needed_for": "Cloud LLM/TTS fallback if you do not run Ollama/Piper locally.",
                    "currently_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
                },
                {
                    "name": "APIFY_API_TOKEN",
                    "needed_for": "Live LinkedIn/Indeed job scraping instead of demo job results.",
                    "currently_configured": bool(os.getenv("APIFY_API_TOKEN", "").strip()),
                },
                {
                    "name": "YOUTUBE_API_KEY",
                    "needed_for": "Real YouTube API course search instead of simulated YouTube search links.",
                    "currently_configured": bool(os.getenv("YOUTUBE_API_KEY", "").strip()),
                },
                {
                    "name": "DUIX_APP_ID / DUIX_APP_KEY / DUIX_CONVERSATION_ID",
                    "needed_for": "Hosted DuiX face. Not required if you use MediaPipe plus local/browser avatar.",
                    "currently_configured": bool(
                        os.getenv("DUIX_APP_ID", "").strip()
                        and os.getenv("DUIX_APP_KEY", "").strip()
                        and os.getenv("DUIX_CONVERSATION_ID", "").strip()
                    ),
                },
                {
                    "name": "LIVEKIT_API_KEY / LIVEKIT_API_SECRET",
                    "needed_for": "LiveKit-hosted realtime rooms. Not required for Pipecat/local MVP.",
                    "currently_configured": bool(
                        os.getenv("LIVEKIT_API_KEY", "").strip()
                        and os.getenv("LIVEKIT_API_SECRET", "").strip()
                    ),
                },
            ],
        },
        "api_key_answer": "No API key is required for the fully local free stack. API keys are only needed for optional cloud services such as OpenAI, Apify, YouTube Data API, DuiX, or hosted LiveKit.",
    }
