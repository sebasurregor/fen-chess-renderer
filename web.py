from flask import Flask, send_from_directory
from main import render_board, fen_to_str, create_bg, validate_fen, FenError
import os

app = Flask(__name__)

# Usamos <path:fen> para aceptar la FEN completa con sus "/"
@app.route('/fen/<path:fen>/<flipped>')
def send_fen(fen, flipped):
    if flipped not in ['0', '1']:
        return 'INVALID FEN - flipped must be 0 or 1'

    # ✅ Validar la FEN antes de dibujar
    try:
        validate_fen(fen)
    except FenError as e:
        return f"Invalid FEN string: {e}"

    # Nombre de archivo para cachear la imagen
    safe_fen = fen.replace("/", "-")
    filename = f"{safe_fen}-{flipped}.png"
    path = os.path.join('fens', filename)

    # Generar imagen si no existe
    if not os.path.exists(path):
        try:
            image = render_board(fen_to_str(fen), create_bg(), flipped == '1')
            image.save(path)
        except Exception as e:
            print("Error al generar imagen:", e)
            return 'Error al generar la imagen'

    # Devolver la imagen
    return send_from_directory('fens', filename)

if __name__ == '__main__':
    app.run(debug=True)
