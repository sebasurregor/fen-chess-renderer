from PIL import Image
import re

# -----------------------------
# Excepción personalizada
# -----------------------------
class FenError(Exception):
    pass

# -----------------------------
# Funciones de validación
# -----------------------------
def validate_fen(fen: str):
    """Valida una cadena FEN según la gramática básica."""
    parts = fen.strip().split()
    if len(parts) < 1:
        raise FenError("FEN vacío")

    # --- 1. Validar filas ---
    rows = parts[0].split('/')
    if len(rows) != 8:
        raise FenError(f"Se esperaban 8 filas, se encontraron {len(rows)}")

    for i, row in enumerate(rows, start=1):
        count = 0
        for char in row:
            if char.isdigit():
                count += int(char)
            elif char in "PNBRQKpnbrqk":
                count += 1
            else:
                raise FenError(f"Carácter inválido '{char}' en fila {i}")
        if count != 8:
            raise FenError(f"Fila {i} tiene {count} casillas en lugar de 8")

    # --- 2. Validar turno ---
    if len(parts) > 1 and parts[1] not in ["w", "b"]:
        raise FenError("Campo de turno inválido (debe ser 'w' o 'b')")

    # --- 3. Validar enroques ---
    if len(parts) > 2:
        castling = parts[2]
        if castling != "-" and not re.fullmatch(r"[KQkq]+", castling):
            raise FenError("Campo de enroques inválido")

    # --- 4. Validar en-passant ---
    if len(parts) > 3:
        ep = parts[3]
        if ep != "-" and not re.fullmatch(r"[a-h][36]", ep):
            raise FenError("Campo en-passant inválido")

    # --- 5. Validar medio-movimientos y número de jugada ---
    if len(parts) > 4:
        if not parts[4].isdigit():
            raise FenError("Medio-movimientos inválido")
    if len(parts) > 5:
        if not parts[5].isdigit():
            raise FenError("Número de jugada inválido")

    return True

# -----------------------------
# Funciones gráficas
# -----------------------------
def square_to_pos(square):
    x = (square % 8) * 100
    y = (7 - square // 8) * 100  # fila 8 arriba
    return x, y

def fen_to_str(fen):
    fen = fen.split()[0]  # solo la parte de las piezas
    rows = fen.split('/')
    output = ''
    for row in rows:
        for char in row:
            if char.isdigit():
                output += int(char) * '_'
            else:
                output += char
    return output

def render_piece(piece, color, square, bg):
    try:
        pieceImg = Image.open(f'img/{color}_{piece}.png')
        bg.paste(pieceImg, square_to_pos(square), pieceImg)
    except Exception as e:
        print(f"Error al cargar {color}_{piece}.png:", e)
    return bg

def render_board(fenStr, bg, flipped):
    if flipped:
        fenStr = fenStr[::-1]
    for square, piece in enumerate(fenStr):
        if piece != '_':
            color = 'white' if piece.isupper() else 'black'
            kind = {
                'p': 'pawn', 'n': 'knight', 'b': 'bishop',
                'r': 'rook', 'q': 'queen', 'k': 'king'
            }[piece.lower()]
            bg = render_piece(kind, color, square, bg)
    return bg

def create_bg():
    whiteTile = Image.open('img/whitetile.png')
    blackTile = Image.open('img/blacktile.png')
    bg = Image.new('RGBA', (800, 800))
    for square in range(64):
        x, y = square_to_pos(square)
        tile = whiteTile if (square + square // 8) % 2 == 0 else blackTile
        bg.paste(tile, (x, y))
    return bg
