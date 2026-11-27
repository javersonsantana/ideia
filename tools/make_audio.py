"""Gera os áudios do app (pasta audio/) com o modelo de voz Kokoro e confere cada um.

Cada gravação é "ouvida" por um reconhecedor de voz (Whisper). Se ele não entender exatamente
a palavra, o script tenta outra voz ou outra frase, até acertar. Palavra solta é o ponto fraco do
modelo (sai artificial), então cada palavra é gravada dentro de uma frase e depois recortada.

Uso:  pip install kokoro-onnx soundfile sherpa-onnx
      numa pasta, baixe e extraia:
        kokoro-v1.0.onnx e voices-v1.0.bin
          (https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0)
        sherpa-onnx-whisper-small
          (https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models)
      python3 tools/make_audio.py PASTA_DOS_MODELOS [--all] [--only=PREFIXO]
Sem --all, só grava os arquivos que ainda não existem; --only=w- regrava os que começam com "w-". Precisa do ffmpeg instalado.
Ao mudar palavras em index.html, mude aqui também.
"""
import difflib, json, os, re, subprocess, sys, tempfile
import numpy as np
import sherpa_onnx
import soundfile as sf
from kokoro_onnx import Kokoro

EN_VOICES, PT_VOICES = ["af_heart", "af_bella", "af_nicole", "af_sarah", "af_sky", "af_kore", "am_michael", "am_adam"], ["pf_dora", "pm_alex"]
WORD_SPEED = 0.9   # palavras e frases novas são faladas um pouco mais devagar

WORDS = """dog cat fish bird cow lion red blue yellow green orange pink
one two three four five six apple banana milk bread egg cheese
ball car teddy-bear robot book kite eye ear nose mouth hand foot""".split()

CLIPS = {f"w-{w}": ("en", w.replace("-", " ").capitalize() + ".", WORD_SPEED) for w in WORDS}
CLIPS.update({
    "hello-bolt": ("en", "Hello! I am Bolt!", 1.0),
    "hello-luna": ("en", "Hello! I am Luna!", 1.0),
    "hello-tuco": ("en", "Hello! I am Tuco!", 1.0),
    "lets-play": ("en", "Hello! Let's play!", 1.0),
    "yes": ("en", "Yes!", 1.0),
    "great": ("en", "Great job!", 1.0),
    "bye": ("en", "Bye-bye!", 1.0),
    "toque": ("pt", "Toque em um desenho para brincar!", 1.0),
    "escute": ("pt", "Escute!", 1.0),
    "fala": ("pt", "Agora fala você!", 1.0),
    "mic": ("pt", "Aperte o microfone, segure e fale!", 1.0),
    "cade": ("pt", "Cadê?", 1.0),
    "esse": ("pt", "Esse se chama", 1.0),
    "quase": ("pt", "Quase! Escute de novo.", 1.0),
    "boa": ("pt", "Boa tentativa!", 1.0),
    "p1": ("pt", "Muito bem!", 1.0),
    "p2": ("pt", "Isso mesmo!", 1.0),
    "p3": ("pt", "Você acertou!", 1.0),
    "p4": ("pt", "Que legal!", 1.0),
    "p5": ("pt", "Parabéns!", 1.0),
    "p6": ("pt", "Você é demais!", 1.0),
    "learn-hello": ("pt", "Vamos aprender a dizer olá em inglês!", 1.0),
    "learn-phrases": ("pt", "Vamos aprender frases em inglês!", 1.0),
    "album": ("pt", "Olha quantas estrelinhas você já ganhou!", 1.0),
    "estrelinha": ("pt", "Você ganhou uma estrelinha!", 1.0),
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

# Palavras que soam igual à palavra certa: o reconhecedor pode escrever qualquer uma delas.
SAME_SOUND = {"eye": {"i", "aye"}}
# Frases do dia a dia: nome do áudio -> (inglês, tradução falada em português)
PHRASES = {
    "f-hello": ("Hello, my friend!", "Olá, meu amigo!"),
    "f-love-you": ("I love you!", "Eu te amo!"),
    "f-thank-you": ("Thank you!", "Obrigado!"),
    "f-morning": ("Good morning!", "Bom dia!"),
    "f-night": ("Good night!", "Boa noite!"),
    "f-happy": ("I am happy!", "Eu estou feliz!"),
    "f-dog": ("I have a dog.", "Eu tenho um cachorro."),
    "f-car": ("My car is blue.", "Meu carro é azul."),
    "f-grandma": ("I love my grandma.", "Eu amo minha vovó."),
    "f-apples": ("I like apples.", "Eu gosto de maçã."),
    "f-bird": ("I see a bird.", "Eu vejo um pássaro."),
    "f-cat": ("My cat is orange.", "Meu gato é laranja."),
}
for _id, (_en, _pt) in PHRASES.items():
    CLIPS[_id] = ("en", _en, WORD_SPEED)
    CLIPS["m-" + _id] = ("pt", "Quer dizer: " + _pt, 1.0)

DIGITS = dict(zip("0123456789", "zero one two three four five six seven eight nine".split()))

def norm(t):
    t = re.sub(r"[^a-zà-ú0-9 ]", " ", t.lower().replace("-", " "))
    return " ".join(DIGITS.get(x, x) for x in t.split())

class Ear:
    """Reconhecedor de voz usado para conferir as gravações."""
    def __init__(self, models):
        d = os.path.join(models, "sherpa-onnx-whisper-small", "small-")
        self.rec = {lang: sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=d + "encoder.int8.onnx", decoder=d + "decoder.int8.onnx", tokens=d + "tokens.txt",
            language=lang, task="transcribe", num_threads=4) for lang in ("en", "pt")}

    def hear(self, path, lang):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                             capture_output=True, check=True).stdout
        pad = np.zeros(6000, dtype=np.float32)
        s = self.rec[lang].create_stream()
        s.accept_waveform(16000, np.concatenate([pad, np.frombuffer(raw, dtype=np.float32), pad]))
        self.rec[lang].decode_stream(s)
        return s.result.text.strip()

# Uma palavra sozinha sai artificial. Dentro de uma frase a voz fica natural, então gravamos
# a frase inteira e recortamos só o que vem depois da última pausa: a palavra.
CARRIERS = ["Listen. {}.", "This one is called... {}.", "Now you say: {}."]

def last_segment(x, sr, min_gap=0.14):
    """Trecho depois da última pausa de pelo menos min_gap segundos, ou None se não houver pausa."""
    win = int(sr * 0.01)
    n = len(x) // win
    e = np.sqrt((x[:n * win].reshape(n, win) ** 2).mean(axis=1))
    quiet = e < max(0.01, e.max() * 0.03)
    end = n
    while end > 0 and quiet[end - 1]:
        end -= 1
    run = 0
    for i in range(end - 1, -1, -1):
        run = run + 1 if quiet[i] else 0
        if run * 0.01 >= min_gap:
            j = i
            while j < end and quiet[j]:
                j += 1
            seg = x[max(0, (j - 4) * win):min(len(x), (end + 10) * win)].copy()
            fade = int(sr * 0.008)
            seg[:fade] *= np.linspace(0, 1, fade)
            seg[-fade:] *= np.linspace(1, 0, fade)
            return seg
    return None

def encode(samples, sr, dest):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, samples, sr)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-af",
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                        "adelay=60,apad=pad_dur=0.15,loudnorm=I=-16:TP=-1.5",
                        "-ac", "1", "-ar", "24000", "-b:a", "64k", dest], check=True)

def takes(k, name, lang, text, speed):
    """Gera as tentativas de gravação de um áudio, da melhor para a pior."""
    kl = "en-us" if lang == "en" else "pt-br"
    voices = EN_VOICES if lang == "en" else PT_VOICES
    if name.startswith("w-"):
        bare = text.rstrip(".!?:")
        for voice in voices:
            for carrier in CARRIERS:
                samples, sr = k.create(carrier.format(bare), voice=voice, speed=speed, lang=kl)
                seg = last_segment(samples, sr)
                if seg is not None:
                    yield voice, carrier.format(bare), seg, sr
        for voice in voices:   # último recurso: a palavra sozinha
            samples, sr = k.create(text, voice=voice, speed=1.0, lang=kl)
            yield voice, text, samples, sr
    else:
        for voice in voices:
            samples, sr = k.create(text, voice=voice, speed=speed, lang=kl)
            yield voice, text, samples, sr

def main(models, redo, only):
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio")
    os.makedirs(out, exist_ok=True)
    k = Kokoro(os.path.join(models, "kokoro-v1.0.onnx"), os.path.join(models, "voices-v1.0.bin"))
    ear = Ear(models)
    # Sininho de acerto: duas notas curtas.
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "sine=frequency=1047:duration=0.14", "-f", "lavfi", "-i", "sine=frequency=1568:duration=0.5",
                    "-filter_complex", "[0][1]concat=n=2:v=0:a=1,afade=t=out:st=0.2:d=0.44,volume=0.5",
                    "-ac", "1", "-ar", "24000", "-b:a", "48k", os.path.join(out, "ding.mp3")], check=True)
    failed = []
    for name, (lang, text, speed) in CLIPS.items():
        dest = os.path.join(out, name + ".mp3")
        again = redo or any(name.startswith(p) for p in only)
        if os.path.exists(dest) and not again:
            continue
        want, need = norm(text), (1.0 if name.startswith("w-") else 0.9)
        best = (-1, None)
        for voice, said, samples, sr in takes(k, name, lang, text, speed):
            with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
                encode(samples, sr, tmp.name)
                got = norm(ear.hear(tmp.name, lang))
                score = 1.0 if got == want or got in SAME_SOUND.get(want, ()) else min(0.99, difflib.SequenceMatcher(None, got, want).ratio())
                if score > best[0]:
                    best = (score, (voice, said, got, len(samples) / sr, open(tmp.name, "rb").read()))
            if best[0] >= need:
                break
        score, (voice, said, got, secs, data) = best
        open(dest, "wb").write(data)
        if score < need:
            failed.append(name)
        print("OK  " if score >= need else "FALHOU", name, voice, repr(said), f"{secs:.2f}s", "-> ouviu:", repr(got), flush=True)
    with open(os.path.join(out, "index.json"), "w") as f:
        json.dump(sorted([*CLIPS, "ding"]), f)
    print("Conferir à mão:", failed if failed else "nada, todas passaram")

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    only = [a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--only=")]
    main(args[0] if args else ".", "--all" in sys.argv, only)
