# 🧩 Juego de Puzzles

Aplicación de rompecabezas (puzzle) desarrollada con Python y Flet.
Permite cargar imágenes desde el sistema, dividirlas en piezas y jugar moviendo las fichas hasta armar la imagen original.

Incluye:
	•	✅ Soporte multiplataforma (Windows, macOS, Linux, Android, Web).
	•	✅ Carga de imágenes desde el sistema o desde la carpeta assets/.
	•	✅ Puzzle adaptable a tamaños: 2x2, 3x3, 4x4.
	•	✅ Movimiento de fichas con arrastrar y soltar (drag & drop).
	•	✅ Contador de movimientos.
	•	✅ Sonido de victoria 🎉.
	•	✅ Efectos visuales al ganar.
	•	✅ Botón para previsualizar la imagen completa.
	•	✅ Reinicio con imágenes aleatorias desde assets/.
	•	✅ Carga automática de un puzzle al iniciar.

## 🚀 Instalación y ejecución

### 1.	Clonar el repositorio:
	```
	git clone https://github.com/mecheverry/juego_puzzles.git
	```
### 2.	Navegar al directorio del proyecto:
	```
	cd juego_puzzles
	```
### 3.	Crear entorno virtual (opcional pero recomendado)
    ```
    python -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
    ```
### 4.	Instalar dependencias
	```
	pip install -r requirements.txt
	```
### 5. Ejecutar en local
   ```
   flet run main.py
   ```
### 6. Empaquetar para escritorio
   ```
   flet pack main.py --name "PuzzleIngeNovaSoft" --icon assets/icon.png
   ```
### 7. Construir para Android
   ```
   flet build apk
   ```
### 8. Construir para iOS
   ```
   flet build ios
   ```
### 9. Construir para web
   ```
   flet build web
   ```

## 📂 Estructura del proyecto
```
puzzle-flet/
├── assets/
│   ├── icon.png         # Icono de la app (1024x1024)
│   ├── splash.png       # Pantalla de inicio / splash
│   ├── favicon.png      # Favicon para web
│   ├── 1.jpg            # Imágenes del puzzle
│   ├── 2.png
│   └── ...
├── main.py              # Código principal
├── requirements.txt     # Dependencias
└── README.md            # Este archivo
```

### ⚙️ Personalización
- 🎨 Icono y splash: reemplaza assets/icon.png y assets/splash.png por tus imágenes personalizadas.
- 🖼️ Imágenes del puzzle: coloca tus imágenes en assets/. El juego elegirá aleatoriamente una al iniciar o al reiniciar.
- 🔊 Sonido de victoria: reemplaza assets/clang_and_wobble.ogg para personalizar el sonido.

### 📱 Plataformas soportadas
- ✅ Escritorio: Windows, macOS, Linux.
- ✅ Móvil: Android (APK o AAB), iOS (IPA).
- ✅ Web: se puede ejecutar en navegador (flet run --web).

### 💻 Desarrollado con
	- ✅ Python 3.10
	- ✅ Flet 0.28.3
	- ✅ Flet-audio 0.1.0
	- ✅ Pillow 11.1.0

# **Juego de puzzles**

#### **🖼️ Imágenes para el puzzle**

[Ver créditos](credits_images.md)