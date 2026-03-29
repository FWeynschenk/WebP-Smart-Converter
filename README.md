# WebP Smart Converter

A drag-and-drop Windows utility that converts **only the incompatible WebP variants** (Lossless & Extended) to JPG, while leaving standard lossy WebPs untouched.

## Why?

WebP comes in three flavors:

| Type | Chunk | Compatibility |
|------|-------|---------------|
| Lossy | `VP8 ` | Broadly compatible — most old software can open these |
| Lossless | `VP8L` | Often breaks older image editors and viewers |
| Extended (alpha/metadata) | `VP8X` | Often breaks older image editors and viewers |

This tool reads the raw WebP header to detect the type. Only `VP8L` and `VP8X` files are converted to JPG (quality 90). `VP8` files are left alone. The original `.webp` file is deleted after a successful conversion.

## Download

Grab the latest `WebP-Smart-Converter.exe` from the [Releases](../../releases/latest) page — no installation or Python required.

## Usage

1. Run `WebP-Smart-Converter.exe`
2. Drag and drop `.webp` files onto the window
3. A summary dialog reports how many files were converted, skipped, or errored

## Run from source

```bash
pip install -r requirements.txt
python webp_smart_converter.py
```

Requires Python 3.8+.

## Build the executable yourself

```bash
pip install pyinstaller
pip install -r requirements.txt
pyinstaller --onefile --windowed --name "WebP-Smart-Converter" --collect-all tkinterdnd2 webp_smart_converter.py
```

The `.exe` will be in the `dist/` folder.

## License

MIT — see [LICENSE](LICENSE).
