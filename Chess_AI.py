import random

piece_score = {'K':0, 'Q':9, 'R':5, 'B':3, 'N':3, 'p':1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


"""
Find the best move based on material alone.
"""
def find_best_move(gs, valid_moves):

    turn_multiplier = 1 if gs.white_to_move else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponent_moves = gs.get_valid_moves()
        if gs.stalemate:
            opponent_max_score = STALEMATE
        elif gs.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponent_move in opponent_moves:
                gs.make_move(opponent_move)
                gs.get_valid_moves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undo_move()

        if opponent_max_score < opponent_minmax_score:
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()

    return best_player_move


"""Helper method to make the first recursive call"""
def find_best_move_minmax(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    find_move_minmax(gs, valid_moves, DEPTH, gs.white_to_move)
    return next_move



"""recursive min max algo"""
def find_move_minmax(gs, valid_moves, depth, white_to_move):
    global next_move
    if depth == 0:
        return score_material(gs.board)
    
    if white_to_move:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score
    

"""A positive score is good for white, a negative score is good for black"""
def score_board(gs):

    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE #black wins
        else:
            return CHECKMATE #white wins
    
    elif gs.stalemate:
        return STALEMATE
    score  = 0
    for row in gs.board:
        for sq in row:
            if sq[0] == 'w':
                score += piece_score[sq[1]]
            elif sq[1] == 'b':
                score -= piece_score[sq[1]]
    return score






"""
Score the board based on material
"""
def score_material(board):
    score  = 0
    for row in board:
        for sq in row:
            if sq[0] == 'w':
                score += piece_score[sq[1]]
            elif sq[1] == 'b':
                score -= piece_score[sq[1]]
    return score
