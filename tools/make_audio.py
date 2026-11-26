"""Gera os áudios do app (pasta audio/) com o modelo de voz Kokoro.

Uso:  pip install kokoro-onnx soundfile
      baixe kokoro-v1.0.onnx e voices-v1.0.bin de
      https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
      python3 tools/make_audio.py PASTA_DOS_MODELOS
Precisa do ffmpeg instalado. Ao mudar palavras em index.html, mude aqui também.
"""
import json, os, subprocess, sys, tempfile
import soundfile as sf
from kokoro_onnx import Kokoro

EN_VOICE, PT_VOICE = "af_heart", "pf_dora"

WORDS = """dog cat fish bird cow lion red blue yellow green orange pink
one two three four five six apple banana milk bread egg cheese
ball car teddy-bear robot book kite eye ear nose mouth hand foot""".split()

CLIPS = {f"w-{w}": ("en", w.replace("-", " ").capitalize() + ".", 0.8) for w in WORDS}
CLIPS.update({
    "hello-bolt": ("en", "Hello! I am Bolt!", 0.9),
    "hello-luna": ("en", "Hello! I am Luna!", 0.9),
    "hello-tuco": ("en", "Hello! I am Tuco!", 0.9),
    "lets-play": ("en", "Hello! Let's play!", 0.9),
    "yes": ("en", "Yes!", 0.9),
    "great": ("en", "Great job!", 0.9),
    "bye": ("en", "Bye-bye!", 0.9),
    "toque": ("pt", "Toque em uma figura para brincar!", 1.0),
    "escute": ("pt", "Escute!", 1.0),
    "fala": ("pt", "Agora fala você!", 1.0),
    "mic": ("pt", "Toque no microfone e fale!", 1.0),
    "cade": ("pt", "Cadê?", 1.0),
    "esse": ("pt", "Esse é:", 1.0),
    "quase": ("pt", "Quase! Escute de novo.", 1.0),
    "boa": ("pt", "Boa tentativa!", 1.0),
    "p1": ("pt", "Muito bem!", 1.0),
    "p2": ("pt", "Isso mesmo!", 1.0),
    "p3": ("pt", "Você acertou!", 1.0),
    "p4": ("pt", "Que legal!", 1.0),
    "s1": ("pt", "Você ganhou uma estrela!", 1.0),
    "s2": ("pt", "Você ganhou duas estrelas!", 1.0),
    "s3": ("pt", "Você ganhou três estrelas!", 1.0),
    "learn-animals": ("pt", "Vamos aprender os animais em inglês!", 1.0),
    "learn-colors": ("pt", "Vamos aprender as cores em inglês!", 1.0),
    "learn-numbers": ("pt", "Vamos aprender os números em inglês!", 1.0),
    "learn-food": ("pt", "Vamos aprender as comidas em inglês!", 1.0),
    "learn-toys": ("pt", "Vamos aprender os brinquedos em inglês!", 1.0),
    "learn-body": ("pt", "Vamos aprender o corpo em inglês!", 1.0),
})

def main(models):
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio")
    os.makedirs(out, exist_ok=True)
    k = Kokoro(os.path.join(models, "kokoro-v1.0.onnx"), os.path.join(models, "voices-v1.0.bin"))
    for name, (lang, text, speed) in CLIPS.items():
        samples, sr = k.create(text, voice=EN_VOICE if lang == "en" else PT_VOICE,
                               speed=speed, lang="en-us" if lang == "en" else "pt-br")
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            sf.write(tmp.name, samples, sr)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-af",
                            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                            "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                            "adelay=40,apad=pad_dur=0.12,loudnorm=I=-16:TP=-1.5",
                            "-ac", "1", "-ar", "24000", "-b:a", "48k",
                            os.path.join(out, name + ".mp3")], check=True)
        print(name, f"{len(samples) / sr:.2f}s")
    with open(os.path.join(out, "index.json"), "w") as f:
        json.dump(sorted(CLIPS), f)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
