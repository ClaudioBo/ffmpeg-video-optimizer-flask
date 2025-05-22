# Optimizador de vídeos
Servicio que optimizará con FFMPEG videos con subidos en la ruta definida **`'WATCH_DIR'`** y los dejara en **`'OUTPUT_DIR'`** y mostrara estadisticas y datos a tiempo real en una pagina expuesta bajo Flask.  
Este servicio lo hice para usarlo en un **contenedor LXC** en mi **Proxmox** configurandole a que exponga un directorio bajo Samba para poder subir ahi los archivos desde mi computadora Windows.  

## Requisitos
- [Hacer un contenedor LXC en Proxmox](docs/LXC.md)
- [Hacerle passthrough](docs/PASSTHROUGH.md) de una iGPU de AMD Ryzen (ya que **`ffmpeg`** esta configurado que use **`vaapi`**) al **contenedor LXC**
- Instalarle **`samba`** al contenedor LXC y [configurarlo](docs/SAMBA.md)
- Instalarle **`ffmpeg`** al contenedor LXC

## Instalación
1. Descargar repositorio
    ```sh
    git clone https://github.com/ClaudioBo/ffmpeg-video-optimizer-flask
    cd ffmpeg-video-optimizer-flask/
    ```
2. Crear entorno virtual de Python y instalarle las librerias necesarias
    ```sh
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    ```
3. Clonar archivo `.env.example` y configurarlo
    ```sh
    cp .env.example .env
    nano .env
    ``` 
4. Correr servicio
    ```sh
    python main.py
    ```
