import sys

VUL = '-NEBNEB-EB-NB-NE'

def squash_board(n_boards, board_number, lin):
    new_board_number = (board_number - 1) % n_boards + 1

    i_board = lin.index('|Board')
    i_sv = lin.index('|sv|')

    new_lin = lin[: i_board]
    new_lin += f'|Board {new_board_number}'
    new_lin += f'|sv|{VUL[new_board_number-1]}|'
    new_lin += lin[i_sv + 6 : ]

    return new_board_number, new_lin


if __name__ == '__main__':
    n = int(sys.argv[1])

    for line in sys.stdin:
        line = line.strip()
        [board_num_str, lin] = line.split('\t')
        new_board_num, new_lin = squash_board(n, int(board_num_str), lin)
        print(f'{new_board_num}\t{new_lin}')
