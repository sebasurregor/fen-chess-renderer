from flask import Flask, send_from_directory
from main import render_board, fen_to_str, create_bg, validate_fen, FenError
import os

app = Flask(__name__)

# -----------------------------
# Routes
# -----------------------------
@app.route('/fen/<path:fen>/<flipped>')
def send_fen(fen: str, flipped: str):
    """
    Endpoint to render a chessboard image from a FEN string.
    - fen: Forsyth-Edwards Notation string (piece placement and optional fields).
    - flipped: '0' for normal orientation, '1' for flipped board.
    """
    if flipped not in ['0', '1']:
        return "Invalid request: 'flipped' must be 0 or 1"

    # Validate the FEN string before rendering
    try:
        validate_fen(fen)
    except FenError as e:
        return f"Invalid FEN string: {e}"

    # Generate a safe filename for caching
    safe_fen = fen.replace("/", "-")
    filename = f"{safe_fen}-{flipped}.png"
    path = os.path.join("fens", filename)

    # Generate the image if it does not exist
    if not os.path.exists(path):
        try:
            image = render_board(fen_to_str(fen), create_bg(), flipped == '1')
            image.save(path)
        except Exception as e:
            print("Error generating image:", e)
            return "Error generating the image"

    # Return the cached or newly generated image
    return send_from_directory("fens", filename)


# -----------------------------
# Main entry point
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
