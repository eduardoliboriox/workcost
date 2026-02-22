from pathlib import Path

try:
    from PIL import Image
except ImportError:
    raise SystemExit(
        "Pillow não instalado. Rode: pip install Pillow\n"
        "Ou adicione 'Pillow' no requirements.txt temporariamente."
    )

ROOT = Path(__file__).resolve().parents[1]

SRC = ROOT / "app" / "static" / "images" / "logos" / "icon-logo-mobile.png"
OUT_DIR = ROOT / "app" / "static" / "images" / "logos"

TARGETS = [
    ("pwa-192.png", (192, 192)),
    ("pwa-512.png", (512, 512)),
    ("pwa-512-maskable.png", (512, 512)),
]

def main():
    if not SRC.exists():
        raise SystemExit(f"Ícone não encontrado: {SRC}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    img = Image.open(SRC).convert("RGBA")

    for name, size in TARGETS:
        out = OUT_DIR / name
        resized = img.resize(size, Image.LANCZOS)
        resized.save(out, format="PNG", optimize=True)
        print(f"OK -> {out} ({size[0]}x{size[1]})")

if __name__ == "__main__":
    main()
