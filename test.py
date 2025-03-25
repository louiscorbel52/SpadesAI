import random
import time
import re
import urllib

import deck52
import bidding
import conf

from nn.models import Models
from objects import Card
from util import parse_history, to_bbo_handviewer, get_history


models = Models.from_conf(conf.load('default.conf'))

def main():
    hands_str_nesw = deck52.random_deal().split()
    dealer = random.choice('NESW')
    
    ## auction_padded = [14] * 'NESW'.index(dealer)  # Replace 'PAD_START' with 14
    auction_padded = [14] * 4  # Replace 'PAD_START' with 14
    
    played_cards = []

    turn_i = 'NESW'.index(dealer)

    while not bidding.auction_over(auction_padded):
        ## import pdb; pdb.set_trace()
        bid = call_api('NESW'[turn_i], dealer, hands_str_nesw, auction_padded, played_cards)
        ## auction_padded.append(bid)
        auction_padded[turn_i] = bid
        turn_i = (turn_i + 1) % 4

    ## import pdb; pdb.set_trace()
    
    turn_i = ('NESW'.index(dealer) + 1) % 4

    current_trick = []
    while len(played_cards) < 52:
        ## import pdb; pdb.set_trace()

        if len(current_trick) == 4:
            trick_winner_i = (turn_i + deck52.get_trick_winner_i(current_trick, 3)) % 4  # Spades is always trump
            current_trick = []
            turn_i = trick_winner_i

    
        pov = 'NESW'[turn_i]
        card = call_api(pov, dealer, hands_str_nesw, auction_padded, played_cards)
        played_cards.append(card)
        current_trick.append(Card.from_symbol(card).code())
        turn_i = (turn_i + 1) % 4
    
    ## import pdb; pdb.set_trace()

    
    print(to_bbo_handviewer(hands_str_nesw, auction_padded, played_cards))


def call_api(pov, dealer, hands_str_nesw, auction_padded, played_cards):
    ## import pdb; pdb.set_trace()
    history = get_history(auction_padded, played_cards)

    # TO DELETE DEBUG
    debug_auction_padded_len = len(auction_padded)
    debug_auction_padded, debug_played_cards = parse_history(dealer, history)
    ## DEBUG

    ## DEBUG
    #### import pdb; pdb.set_trace()
    ##s = f'http://localhost:8000/u_bm/robot.php?botstyle=advanced&sc=MP&pov={pov}&d={dealer}&n={hands_str_nesw[0]}&e={hands_str_nesw[1]}&s={hands_str_nesw[2]}&w={hands_str_nesw[3]}&h={history}'

    resp = urllib.request.urlopen(
        f'http://localhost/u_bm/robot.php?botstyle=advanced&sc=MP&pov={pov}&d={dealer}&n={hands_str_nesw[0]}&e={hands_str_nesw[1]}&s={hands_str_nesw[2]}&w={hands_str_nesw[3]}&h={history}'
        # f'http://ben.dev.cl.bridgebase.com/u_bm/robot.php?botstyle=advanced&sc=MP&pov={pov}&d={dealer}&n={hands_str_nesw[0]}&e={hands_str_nesw[1]}&s={hands_str_nesw[2]}&w={hands_str_nesw[3]}&h={history}'
        # f'http://ml01.bridgebase.com:8012/u_bm/robot.php?botstyle=advanced&sc=MP&pov={pov}&d={dealer}&n={hands_str_nesw[0]}&e={hands_str_nesw[1]}&s={hands_str_nesw[2]}&w={hands_str_nesw[3]}&h={history}'
    )
    return parse_api_resp(resp)

def parse_api_resp(resp):
    ## import pdb; pdb.set_trace()
    xml = resp.read().decode().replace('\n', '')

    if 'type="bid"' in xml:
        bid = re.findall(r'bid="(.+?)"', xml)[0]
        if 0 <= int(bid) <= 13:
            return bid
        else:
            raise ValueError(f"Invalid bid received: {bid}")

    if 'type="play"' in xml:
        return re.findall(r'card="(.+?)"', xml)[0]


if __name__ == '__main__':
    t_start = time.time()
    main()
    print(time.time() - t_start)
