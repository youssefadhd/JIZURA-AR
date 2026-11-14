# JIZURA-AR

<p align="center">
  <strong>Arabic deserves beautiful lyric animations.</strong>
</p>

<p align="center">
  An Arabic-compatible evolution of JIZURA, bringing proper Arabic typography, RTL rendering, and animated lyrics to the creative workflow.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Experimental-orange" alt="Experimental" />
  <img src="https://img.shields.io/badge/Platform-Web-blue" alt="Web" />
  <img src="https://img.shields.io/badge/Language-Arabic%20%7C%20English-green" alt="Arabic and English" />
</p>

---

## ✨ About

JIZURA-AR is an open-source project extending [JIZURA](https://github.com/852wa/JIZURA) with Arabic language support.

Arabic typography presents unique challenges in animated text rendering. Letters change shape depending on their neighboring characters, text flows from right to left, and mixed Arabic-English content requires bidirectional text handling.

Our goal is to make Arabic lyric videos as expressive, beautiful, and accessible as those created in other languages.

## 🚀 Features

### Arabic Typography
- Contextual Arabic letter shaping.
- Right-to-left text rendering.
- Mixed Arabic and English support.
- Diacritics and punctuation handling.
- Arabic-compatible font support.

### Animation
- Animated lyric typography.
- Shaped Arabic text groups.
- Preserved animation effects.
- Dynamic visual compositions.

### Export
- MP4 video export.
- PNG frame export.
- Browser-based previews.

*Experimental implementation: feature behavior and compatibility are still being tested.*

## 🛠️ Technology

JIZURA-AR builds upon the original JIZURA architecture.

- JavaScript
- HTML5 Canvas
- Python build system
- Browser-native text rendering
- Unicode bidirectional text support

## 💻 Development

### Requirements
- Python
- A modern web browser
- Git

### Clone the repository

```bash
git clone https://github.com/youssefadhd/JIZURA-AR.git
cd JIZURA-AR
```

### Build the application

```bash
python build.py
```

### Build with development assets

```bash
python build.py --dev
```

## 🧪 Testing

Arabic rendering is being tested against:

- Arabic contextual shaping.
- Arabic diacritics.
- Mixed Arabic and Latin text.
- Arabic punctuation.
- English text compatibility.
- Japanese text compatibility.
- Animation and video export.

## 🎯 Project Roadmap

- [x] Initial Arabic rendering implementation.
- [x] Arabic language detection.
- [x] RTL-aware text rendering.
- [x] Mixed Arabic and English support.
- [x] Initial PNG and MP4 export tests.
- [ ] Complete visual regression testing.
- [ ] Improve Arabic-specific animation effects.
- [ ] Validate After Effects integration.
- [ ] Publish a stable public release.

## 🤝 Contributing

Contributions, bug reports, testing, and suggestions are welcome.

If you discover a rendering issue, please include:

- A sample lyric.
- A screenshot or recording.
- The browser you're using.
- The animation effect involved.

## 🙏 Credits

JIZURA-AR is based on [JIZURA](https://github.com/852wa/JIZURA).

Original project: https://github.com/852wa/JIZURA

We are grateful to the original developers for creating the foundation that makes this project possible.

Please refer to the original repository's license and preserve all required notices and attribution.

---

<p align="center">
  <strong>Made for Arabic typography. Built for creative freedom.</strong>
</p>
