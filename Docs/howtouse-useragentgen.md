# useragentgen

Random User-Agent string generator for Chrome, Firefox, Safari, Edge, and Opera.
All browser templates are **embedded inside the package** — no external files needed after install.

## Installation

```bash
pip install useragentgen
```

## Quick start

```python
import useragentgen

# Single UA, random browser
useragentgen.generate()

# Single UA, specific browser
useragentgen.generate("chrome")
useragentgen.generate("firefox")
useragentgen.generate("safari")
useragentgen.generate("edge")
useragentgen.generate("opera")

# Batch generation
useragentgen.generate_many(10)            # 10 random-browser UAs
useragentgen.generate_many(5, "chrome")   # 5 Chrome UAs
```

Reproducible output with a seed:

```python
import useragentgen

useragentgen.init(42)
print(useragentgen.generate("chrome"))  # same result every run
```

## Supported browsers

| Key        | Covers                         |
|------------|-------------------------------|
| `chrome`   | Windows, macOS, Linux, Android |
| `firefox`  | All platforms                  |
| `safari`   | macOS, iOS, Windows            |
| `edge`     | Windows, macOS, Linux, Android |
| `opera`    | Windows, macOS, Linux          |

## License

[MIT License Copyright (c) 2026 Masrkai, rights reserved](LICENSE)
