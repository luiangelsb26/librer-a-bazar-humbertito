"""Punto de entrada compatible para Uvicorn y la administración local."""

from backend.api import create_app as create_app, main


if __name__ == "__main__":
    main()
