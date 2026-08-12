# Stack de visuales — investigación verificada jul-2026
> Objetivo: 3 videos/día (~100 imágenes/día, 3.000/mes) con $0-14/mes

## Stack recomendado (en orden de integración)
1. **Gemini 2.5 Flash Image "Nano Banana"** (Google AI Studio API) — ~500 img/día GRATIS. Excelente en estética sepia/vintage. Requiere GOOGLE_AI_API_KEY (gratis, sin tarjeta) → aistudio.google.com
2. **Library of Congress — colección FSA/OWI**: 175.000 negativos B/N 1935-1944 (Dorothea Lange, Russell Lee; comunidades hispanas rurales de Texas/Arizona/California). DOMINIO PÚBLICO TOTAL = monetizable. API JSON gratis (20 req/min). loc.gov/pictures/collection/fsa/
3. **FLUX schnell** en fal.ai — $0.003/img (respaldo si cae el free tier de Google; ~$9/mes como principal)
4. **mflux local** (Flux en Apple Silicon via MLX): `pip install mflux` → 100 img gratis en 1-2h desatendidas. Plan B sin APIs
5. **Ideogram 4.0 Turbo** — $0.03/img, EL MEJOR en texto dentro de imágenes → solo miniaturas (3-5/día = $3-5/mes)
6. **Pexels API** (20K req/mes gratis) + **Pixabay API** (generosa) — b-roll en video
7. **Real-ESRGAN ncnn-vulkan** (CLI local gratis) — upscalar fotos históricas pequeñas antes del render (nunca más pixelado)

## ⚠️ Legal
- Mediateca INAH / Fototeca Nacional (Archivo Casasola): licencia "uso personal sin fines de lucro" → NO usable en canal monetizado
- Flickr Commons: "no known copyright restrictions" — verificar caso a caso
- Free tier de Google: imágenes llevan watermark invisible SynthID (no visible, no afecta)

## Tipografías (gratis, uso comercial) — anti-genérico
- Títulos: **Fraunces** o **Zodiak** (Fontshare) — el vintage moderno; alternativa: Playfair Display ✓ (descargada)
- Números/lower thirds: **Oswald** ✓ (descargada), **Bebas Neue**, **Anton** (cifras impactantes)
- Citas/documentos de época: **Special Elite** (máquina de escribir), **Old Standard TT**
- Texto sobre sepia: **Libre Caslon** ✓ (descargada)
- Regla: jamás Montserrat/Roboto/Lato en títulos

## Pendientes de integración en pipeline/visuals.py
- [ ] Cliente LOC API (búsqueda + descarga TIFF alta res)
- [ ] Cliente Gemini image gen (GOOGLE_AI_API_KEY en .env)
- [ ] Paso Real-ESRGAN para imágenes <1200px
- [ ] Pixabay como tercera fuente stock
- [ ] Descargar Fraunces + Special Elite + Bebas Neue
