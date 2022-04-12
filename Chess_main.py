"""
This is the main driver file. It is responsible for handling all user inputs, 
displaying Game_State
"""

import pygame as pyg
import Chess_Engine

WIDTH = 512
HEIGHT = 512

DIMENSION = 8 #8*8 dimension
SQUARE_SIZE = WIDTH//DIMENSION
MAX_FPS = 15 # For animation
IMAGES = {}

"""
Inistialize a global dictionary of images
Load exactly one time in main
"""
def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wp","wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        IMAGES[piece] = pyg.transform.scale(pyg.image.load("images/"+piece+".png"), (SQUARE_SIZE, SQUARE_SIZE))


"""
This is the main driver code. It will handle user input and updation of graphics
"""
def main():
    pyg.init()
    screen = pyg.display.set_mode((WIDTH, HEIGHT))
    clock = pyg.time.Clock()
    screen.fill(pyg.Color("white"))
    gs = Chess_Engine.Game_State()
    valid_moves = gs.get_valid_moves()#get a list of all the valid moves in the position
    animate = False #flag variable for when we have to animate
    move_made = False # flag variable for when a move is made
    load_images() 
    sq_selected = () # no square is is selected, keep track of last click of the user (tuple:(row, col))
    player_clicks = [] # keep track of player clicks (two tuples: (a,b), (x,y))

    running = True
    while running:
        for evt in pyg.event.get():
            if evt.type == pyg.QUIT:
                running = False
            
            #mouse handler
            elif evt.type == pyg.MOUSEBUTTONDOWN:
                location = pyg.mouse.get_pos() # mouse location
                col = location[0] // SQUARE_SIZE
                row = location[1] // SQUARE_SIZE
                
                if sq_selected == (row, col): # if player clicks the same square twice, then deselect that square
                    sq_selected = () #deselect
                    player_clicks = [] # clear player clicks
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected) # append both the clicks
                
                if len(player_clicks) == 2: # after the second click
                    move = Chess_Engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])
                            move_made = True
                            animate = True
                            sq_selected = () # reset user clicks
                            player_clicks = []
                    if not move_made:
                        player_clicks = [sq_selected]
            elif evt.type == pyg.KEYDOWN:
                if evt.key == pyg.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                if evt.key == pyg.K_r: #reset board by pressing r
                    gs = Chess_Engine.Game_State()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

        if move_made:
            if animate:
                animate_move(gs.movelog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves() #generate all the moves for the opponent
            move_made = False
            animate = False

        
        draw_game_state(screen, gs, valid_moves, sq_selected)
        clock.tick(MAX_FPS)
        pyg.display.flip()

"""
Highlight square selected and  moves for piece selected
"""
def highlighted_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        row, col = sq_selected
        if gs.board[row][col][0] == ('w' if gs.white_to_move else 'b'):
            #highlight the selected square
            s = pyg.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100) #transparency value - 0 transparent, 255 opaque
            s.fill(pyg.Color('blue'))
            screen.blit(s, (col * SQUARE_SIZE, row*SQUARE_SIZE))
            #highlight moves from that square
            s.fill('yellow')
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (SQUARE_SIZE*move.end_col, SQUARE_SIZE * move.end_row))



"""
Responsible for all the graphics within a current gamestate
"""
def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_squares_on_board(screen) #draw the squares on the board
    highlighted_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board) #draw pieces on top of the squares

#draw the squares on the board
def draw_squares_on_board(screen):
    colors = [pyg.Color("white"), pyg.Color("red")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row+col)%2]
            pyg.draw.rect(screen, color, pyg.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

#draw pieces on top of the squares
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], pyg.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

"""
Animating a move
"""
def animate_move(move, screen, board, clock):
    colors = [pyg.Color("white"), pyg.Color("red")]
    d_r = move.end_row - move.start_row
    d_c = move.end_col - move.start_col
    frames_per_square = 10 #frames to move one square
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_square
    for frame in range(frame_count+1):
        row, col = (move.start_row + d_r * frame/frame_count, move.start_col + d_c * frame/frame_count)
        draw_squares_on_board(screen)
        draw_pieces(screen, board)

        #erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = pyg.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pyg.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], end_square)
        #draw the moving piece
        screen.blit(IMAGES[move.piece_moved], pyg.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pyg.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()

