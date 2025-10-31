from PIL import Image
import re

# -----------------------------
# Custom Exception
# -----------------------------
class FenError(Exception):
    """Custom exception for invalid FEN strings."""
    pass


# -----------------------------
# Validation Functions
# -----------------------------
def validate_fen(fen: str) -> bool:
    """
    Validate a FEN string according to basic grammar rules.
    Raises FenError if the string is invalid.
    """
    parts = fen.strip().split()
    if len(parts) < 1:
        raise FenError("Empty FEN string")

    # 1. Validate rows
    rows = parts[0].split('/')
    if len(rows) != 8:
        raise FenError(f"Expected 8 rows, found {len(rows)}")

    for i, row in enumerate(rows, start=1):
        count = 0
        for char in row:
            if char.isdigit():
                count += int(char)
            elif char in "PNBRQKpnbrqk":
                count += 1
            else:
                raise FenError(f"Invalid character '{char}' in row {i}")
        if count != 8:
            raise FenError(f"Row {i} has {count} squares instead of 8")

    # 2. Validate turn
    if len(parts) > 1 and parts[1] not in ["w", "b"]:
        raise FenError("Invalid turn field (must be 'w' or 'b')")

    # 3. Validate castling rights
    if len(parts) > 2:
        castling = parts[2]
        if castling != "-" and not re.fullmatch(r"[KQkq]+", castling):
            raise FenError("Invalid castling field")

    # 4. Validate en passant
    if len(parts) > 3:
        ep = parts[3]
        if ep != "-" and not re.fullmatch(r"[a-h][36]", ep):
            raise FenError("Invalid en passant field")

    # 5. Validate halfmove and fullmove counters
    if len(parts) > 4 and not parts[4].isdigit():
        raise FenError("Invalid halfmove counter")
    if len(parts) > 5 and not parts[5].isdigit():
        raise FenError("Invalid fullmove number")

    return True


# -----------------------------
# Rendering Functions
# -----------------------------
def square_to_pos(square: int) -> tuple[int, int]:
    """
    Convert a square index (0–63) into pixel coordinates.
    Top-left is (0,0), each square is 100x100 pixels.
    """
    x = (square % 8) * 100
    y = (7 - square // 8) * 100  # row 8 is at the top
    return x, y


def fen_to_str(fen: str) -> str:
    """
    Convert the piece placement part of a FEN string into
    a flat string of 64 characters (pieces or underscores).
    """
    fen = fen.split()[0]  # only the piece placement part
    rows = fen.split('/')
    output = ''
    for row in rows:
        for char in row:
            if char.isdigit():
                output += int(char) * '_'
            else:
                output += char
    return output


def render_piece(piece: str, color: str, square: int, bg: Image.Image) -> Image.Image:
    """
    Render a single piece onto the board background.
    """
    try:
        piece_img = Image.open(f'img/{color}_{piece}.png')
        bg.paste(piece_img, square_to_pos(square), piece_img)
    except Exception as e:
        print(f"Error loading {color}_{piece}.png:", e)
    return bg


def render_board(fen_str: str, bg: Image.Image, flipped: bool) -> Image.Image:
    """
    Render all pieces from a FEN string onto the board background.
    """
    if flipped:
        fen_str = fen_str[::-1]

    for square, piece in enumerate(fen_str):
        if piece != '_':
            color = 'white' if piece.isupper() else 'black'
            kind = {
                'p': 'pawn', 'n': 'knight', 'b': 'bishop',
                'r': 'rook', 'q': 'queen', 'k': 'king'
            }[piece.lower()]
            bg = render_piece(kind, color, square, bg)
    return bg


def create_bg() -> Image.Image:
    """
    Create an empty 8x8 chessboard background using tile images.
    """
    white_tile = Image.open('img/whitetile.png')
    black_tile = Image.open('img/blacktile.png')
    bg = Image.new('RGBA', (800, 800))

    for square in range(64):
        x, y = square_to_pos(square)
        tile = white_tile if (square + square // 8) % 2 == 0 else black_tile
        bg.paste(tile, (x, y))
    return bg
