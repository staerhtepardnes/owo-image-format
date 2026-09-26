# OWO image format

Implementação de referência em Python do formato de imagem `.owo`, com suporte
para RGB/RGBA, payload raw e compressão RLE sem perdas.

## Instalação

```bash
python -m pip install -e .
```

## Uso da API

```python
from PIL import Image
from owo import encode, decode

image = Image.open("input.png")
encode(image, "output.owo", compression="rle")
restored = decode("output.owo")
restored.save("roundtrip.png")
```

## CLI

```bash
python owo_tool.py encode input.png output.owo --compression rle
python owo_tool.py decode output.owo output.png
```

## Testes

```bash
python -m pytest
```

A especificação compatível está em [spec.md](spec.md).
