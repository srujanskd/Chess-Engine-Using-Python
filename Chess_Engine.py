"""
This is responsible for storing all the info about the current state of the game. It will be 
responsible for determining valid moves. It will also keep a move log
"""


class Game_State():
    def __init__(self):
        #A 8*8 representation of chess board(2D List), where first character(ie. b, w) represents  the color of the piece.
        #Second character(ie. R, K) represents type of the piece like Rook, Queen etc.
        # '--' represents empty square 
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bp","bp","bp","bp","bp","bp","bp","bp"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["--","--","--","--","--","--","--","--"],
        ["wp","wp","wp","wp","wp","wp","wp","wp"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.white_to_move = True
        self.movelog = []
        self.white_king_loc = (7, 4) #inital position of white king
        self.black_king_loc = (0, 4) # initial position of black king
        self.in_check = False
        self.pins = []
        self.checks = []
        self.enpassant_possible = () #coordinates for the square where en passant capture is possible


        self.move_functions = {"p": self.get_pawn_moves, "R":self.get_rook_moves, 
                                "N": self.get_knight_moves, "B":self.get_bishop_moves, 
                                "Q": self.get_queen_moves, "K":self.get_king_moves} #this maps all the funtions for different types of pieces to piece name, this prevents us from writing 6 if statements

    """
    Takes a move as parameter and executes it (won't work for castling, en passant, pawn promotion)
    """
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move) # log the move
        self.white_to_move = not self.white_to_move

        #update kings position when moved
        if move.piece_moved == "wK":
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_loc = (move.end_row, move.end_col)
        
        #pawn promotion
        if move.pawn_promotion:
            promoted_piece = input("promote to Q, R, B or N ")
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece

        #en passant
        if move.enpassant:
            self.board[move.start_row][move.end_col] = "--" #capturing the pawn
        
        #update enpassant_possible variable
        if (move.piece_moved[1] == 'p') and  (abs(move.start_row - move.end_row) == 2): #only 2 square pawn advance
            self.enpassant_possible = ((move.end_row + move.start_row)//2, move.end_col)
        else:
            self.enpassant_possible = ()

            


    """
    Undo the last move
    """
    
    def undo_move(self):
        if len(self.movelog) > 0: # make sure that there is atleast one move in the movelog
            move = self.movelog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move # switch player turn

            #update kings position when undoing a move
            if move.piece_moved == "wK":
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_loc = (move.start_row, move.start_col)

            #undo en passant
            if move.enpassant:
                self.board[move.end_row][move.end_col] = "--"#leave landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)

            #undo aa 2 square pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible =  ()
        
    """
    Get all the valid moves considering checks
    """
    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        if self.white_to_move:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        if self.in_check:
            if len(self.checks) == 1: # only one check, then either move the king or block the check
                moves = self.get_all_possible_moves()

                #to block a check we must move a piece between king and attacking piece
                check = self.checks[0] #check info
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] #enemy piece checking the king
                valid_squares = [] #squares that pieces can move to

                #if knight, must capture the knight or move the king
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_row)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) #check[2] and check[3] are check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: #once we get to piece and checks
                            break

                #get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1): #iterating backwards to delete items
                    if moves[i].piece_moved[1] != 'K': #move dosen't move king so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: #move dosen't block check or capture piece
                            moves.remove(moves[i])
            else: #double check
                self.get_king_moves(king_row, king_col, moves)
        else: #if not in check
            moves = self.get_all_possible_moves()
            
        return moves

             
    """
    All possible moves without considering checks
    """
    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)): #iterating through all row
            for col in range(len(self.board[row])): # iterating through all column of the row
                cur_turn = self.board[row][col][0] #gives w or b
                if (cur_turn == 'w' and self.white_to_move) or (cur_turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves) #using move_funtion dictionary, we call the respective funtions
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add that move to moves list
    """
    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            enemy_color = 'b'
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            enemy_color = 'w'
        pawn_promotion = False

        if self.board[row+move_amount][col] == "--": #pawn moves forward (if that square is empty)
            if not piece_pinned or pin_direction == (move_amount, 0):
                if row + move_amount == back_row:
                    pawn_promotion = True
                moves.append(Move((row, col), (row+move_amount, col), self.board, pawn_promotion=pawn_promotion))
                if row == start_row and self.board[row+2*move_amount][col] == "--": #pawn moves 2 squares forward (if that square is empty and it is on the initial position)
                    moves.append(Move((row, col), (row+2*move_amount, col), self.board))
        if col - 1 >= 0: #capture to left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col-1][0] == enemy_color:
                    if row + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col - 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board, enpassant = True))
        if col + 1 <= 7: #capture to left
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[row + move_amount][col+1][0] == enemy_color:
                    if row + move_amount == back_row:
                        pawn_promotion = True
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col + 1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board, enpassant = True))




    """
    Get all the rook moves for the rook located at row, col and add that move to moves list
    """
    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q': #can't remove queen from pin on rook moves, only remove it on bishop move
                    self.pins.remove(self.pins[i])
                break

        direction = ((0, 1), (1, 0), (0, -1), (-1, 0)) #all four directions; right, down, left, up
        enemy_color = "b" if self.white_to_move else "w"
        
        for dir in direction:
            for i in range(1, 8):
                end_row = row + dir[0] * i
                end_col = col + dir[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #inside the board
                    if not piece_pinned or pin_direction == dir or pin_direction == (-dir[0], -dir[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: #if there exist a enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else: # same colored piece then stop
                            break
                else: #off the board
                    break



    """
    Get all the knight moves for the knight located at row, col and add that move to moves list
    """
    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        direction = ((-2,-1),(-2,1), (2, -1),(2,1), (1,2),(-1,2),(1, -2),(-1,-2))
        ally_color = "w" if self.white_to_move else "b"
        for dir in direction:
            end_row = row + dir[0]
            end_col = col + dir[1]
            if 0 <= end_row < 8 and 0<= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color: # not an ally piece, empty of enemy piece
                        moves.append(Move((row, col), (end_row, end_col), self.board))
    """
    Get all the bishop moves for the bishop located at row, col and add that move to moves list
    """
    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        direction = ((-1,1), (1, 1), (1, -1), (-1, -1)) #all four directions of bishop
        enemy_color = "b" if self.white_to_move else "w"
        
        for dir in direction:
            for i in range(1, 8):
                end_row = row + dir[0] * i
                end_col = col + dir[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: #inside the board
                    if not piece_pinned or pin_direction == dir or pin_direction == (-dir[0], -dir[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: #if there exist a enemy piece
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else: # same colored piece then stop
                            break
                else: #off the board
                    break

    """
    Get all the queen moves for the queen located at row, col and add that move to moves list
    """
    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)


    """
    Get all the king moves for the king located at row, col and add that move to moves list
    """
    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.white_to_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    #place king on end squares and check for checks
                    if ally_color == 'w':
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    #place king back on original location
                    if ally_color == 'w':
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)



    """
    Returns if the player is in check, a list of pins, and a list of checks
    """
    def check_for_pins_and_checks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from
        checks = [] #squares where enemy is givin check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1,0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () #reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == (): #first ally piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else: # second allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] ==  enemy_color:
                        type = end_piece[1]
                        # there are 5 possibilities
                        # 1) orthogonally away from king and piece is a rook
                        # 2) diagonally away from king and piece is a bishop
                        # 3) 1 square diagonally away from king and piece is a pawn
                        # 4) any direction and the piece is queen
                        # 5) any direction 1 square away and piece is a king
                        
                        if (0<= j <= 3 and type == 'R') or \
                        (4 <= j <= 7 and type == 'B') or \
                         (i == 1 and type == 'p' and ((enemy_color == 'w' and 6<= j <= 7) or \
                          (enemy_color == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or ( i == 1 and type == 'K'):
                            if possible_pin == (): #no piece is blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                #piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:
                            #enemy piece not giving check
                            break
                else:
                    break
        #check for knight checks
        knight_moves = ((-2,-1),(-2,1), (2, -1),(2,1), (1,2),(-1,2),(1, -2),(-1,-2))
        for m in knight_moves:
            end_row = start_row + m[0] 
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N": #enemy knight attacking the king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks




class Move():

    ranks_to_rows = {"1":7, "2":6, "3":5, "4" : 4, "5": 3, "6":2, "7":1, "8":0}
    rows_to_ranks = {v:k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a":0, "b": 1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    cols_to_files = {v:k for k,v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, enpassant = False, pawn_promotion = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_col = end_sq[1]
        self.end_row = end_sq[0]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        #pawn promotion
        self.pawn_promotion = pawn_promotion
        #en passant
        self.enpassant = enpassant
        if enpassant:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp' #enpassant captures opposite colored pawn

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col #creates a unique mid btw 0 to 7777

    """
    Overiding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False


    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    
    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]