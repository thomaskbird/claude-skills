#!/usr/bin/env python3
"""
Transcribe the audio track of a screen recording, with timestamps.

Designed to fail SOFTLY: if there's no audio track, if faster-whisper
can't be installed, or if the model can't be downloaded (e.g. no network
access to huggingface.co), this prints {"available": false, "reason": ...}
and exits 0 rather than crashing. The calling skill should treat that as
a signal to fall back to visual-only documentation.

Usage:
    python3 transcribe_audio.py <video_path> <output_json_path>
"""
import json
import os
import subprocess
import sys
import tempfile


def has_audio_stream(video_path):
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=index", "-of", "csv=p=0", video_path],
            capture_output=True, text=True, timeout=30
        )
        return bool(out.stdout.strip())
    except Exception:
        return False


def extract_audio_wav(video_path, wav_path):
    subprocess.run(
        ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000",
         "-f", "wav", wav_path],
        capture_output=True, timeout=120, check=True
    )


def write_result(output_json_path, result):
    with open(output_json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


def main(video_path, output_json_path):
    if not has_audio_stream(video_path):
        write_result(output_json_path, {"available": False, "reason": "no audio track in video"})
        return

    try:
        import faster_whisper  # noqa
    except ImportError:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--break-system-packages",
                 "-q", "faster-whisper"],
                check=True, timeout=180
            )
            import faster_whisper  # noqa
        except Exception as e:
            write_result(output_json_path, {
                "available": False,
                "reason": f"could not install faster-whisper: {e}"
            })
            return

    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "audio.wav")
        try:
            extract_audio_wav(video_path, wav_path)
        except Exception as e:
            write_result(output_json_path, {"available": False, "reason": f"audio extraction failed: {e}"})
            return

        try:
            from faster_whisper import WhisperModel
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, _info = model.transcribe(wav_path, vad_filter=True)
            seg_list = [
                {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
                for s in segments
            ]
        except Exception as e:
            write_result(output_json_path, {
                "available": False,
                "reason": f"model load/transcribe failed (likely no network access to model host): {e}"
            })
            return

    if not seg_list or not any(s["text"] for s in seg_list):
        write_result(output_json_path, {"available": False, "reason": "no speech detected"})
        return

    write_result(output_json_path, {"available": True, "segments": seg_list})


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(json.dumps({"available": False, "reason": "usage: transcribe_audio.py <video> <output_json>"}))
        sys.exit(0)
    main(sys.argv[1], sys.argv[2])
