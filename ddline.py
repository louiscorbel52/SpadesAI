import sys
import numpy as np

import bidding
import binary
import deck52
import conf

from ddsolver import ddsolver
from nn.models import Models
from objects import Card
from test import to_bbo_handviewer
from datetime import datetime

dd = ddsolver.DDSolver()

models = Models.from_conf(conf.load('default.conf'))

MIN_SCORE = 0.1


def ddline(hands_str_nesw, auction_padded):
    contract = bidding.get_contract(auction_padded)
    if contract is None:
        return [], []
    
    strain_i = bidding.get_strain_i(contract)
    decl_i = bidding.get_decl_i(contract)

    hands_bin_nesw = []
    for hand_str in hands_str_nesw:
        hands_bin_nesw.append(binary.parse_hand_f(52)(hand_str))

    played_cards, scores = [], []

    current_trick = []
    on_play_i = (decl_i + 1) % 4
    while len(played_cards) < 52:

        X = np.zeros((1, 369))
        X[:, 364 + strain_i] = 1
        if len(current_trick) > 0:
            X[:, 312 + current_trick[-1]] = 1
        if len(current_trick) > 1:
            X[:, 260 + current_trick[-2]] = 1
        if len(current_trick) > 2:
            X[:, 208 + current_trick[-3]] = 1
        
        X[:, :52] = hands_bin_nesw[on_play_i]
        X[:, 52:104] = hands_bin_nesw[(on_play_i + 1) % 4]
        X[:, 104:156] = hands_bin_nesw[(on_play_i + 2) % 4]
        X[:, 156:208] = hands_bin_nesw[(on_play_i + 3) % 4]

        p_peek = models.peekplay.model(X)
        peek_scores = np.mean(p_peek, axis=0)

        hands_pbn = ['N:' + ' '.join([deck52.hand_to_str(h[0]) for h in hands_bin_nesw])]

        card_dd = dd.solve(strain_i, (on_play_i - len(current_trick)) % 4, current_trick, hands_pbn)

        score_card = [(tricks[0], peek_scores[card], card) for card, tricks in card_dd.items() if peek_scores[card] > MIN_SCORE]
        score_card = sorted(score_card, reverse=True)

        _, score, card = score_card[0]

        played_cards.append(Card.from_code(card).symbol())
        scores.append(score)

        current_trick.append(card)

        hands_bin_nesw[on_play_i][0, card] -= 1

        if len(current_trick) == 4:
            trick_leader_i = (on_play_i + 1) % 4
            trick_winner_i = (trick_leader_i + deck52.get_trick_winner_i(current_trick, (strain_i - 1) % 5)) % 4
            on_play_i = trick_winner_i
            current_trick = []
        else:
            on_play_i = (on_play_i + 1) % 4
    
    return played_cards, scores


def test_ddline():
    # hands_str_nesw = ['K752.KJ.K53.JT98', 'AT6.A4.92.AK6532', '984.Q98762.T4.74', 'QJ3.T53.AQJ876.Q']
    hands_str_nesw = ['J5.K42.JT2.KQ754', 'Q9.AQT9876.A3.93', 'K87643.5.965.T62', 'AT2.J3.KQ874.AJ8']
    # auction_padded = 'P.1C.P.1D.P.2C.P.3N.P.6N.P.P.P'.replace('P', 'PASS').split('.')
    auction_padded = ['PAD_START'] + '1H.P.2D.P.4H.P.P.P'.replace('P', 'PASS').split('.')

    played_cards, scores = ddline(hands_str_nesw, auction_padded)

    print(to_bbo_handviewer('-', hands_str_nesw, auction_padded, played_cards))

    for card, score in zip(played_cards, scores):
        print(card, score)


def gib_iterator(lines):
    buf = []
    for i, line in enumerate(lines):
        if i % 5 in (0, 1, 2, 3):
            buf.append(line.strip())
        if i % 5 == 4:
            yield tuple(buf)
            buf = []


if __name__ == '__main__':
    for i, (hands_pbn, dealer_vuln, contract, auction) in enumerate(gib_iterator(sys.stdin)):
        if i % 1000 == 0:
            sys.stderr.write(f'{i}. {datetime.now()}\n')
            sys.stderr.flush()

        hands_str = hands_pbn.strip()[2:].split()
        hands_str_nesw = [*hands_str[1:], hands_str[0]]
        dealer = dealer_vuln[0]
        auction_padded = ['PAD_START'] * 'NESW'.index(dealer) + auction.replace('P', 'PASS').split('.')

        played_cards, scores = ddline(hands_str_nesw, auction_padded)

        if not(played_cards):
            continue

        print(hands_pbn)
        print(dealer_vuln)
        print(contract)
        print(auction)
        print(''.join(played_cards))
        print(' '.join([('%1.2f' % score) for score in scores]))

        # print(min(scores))
        # print(to_bbo_handviewer('-', hands_str_nesw, auction_padded, played_cards))

