import random
import time
import re
import urllib
import argparse  # Import argparse for command-line arguments

import deck52
import bidding
import conf

from nn.models import Models
from objects import Card
from util import parse_history, to_bbo_handviewer, get_history


models = Models.from_conf(conf.load('default.conf'))

def main(is_sandbag_on, is_dumb, is_risky):
    hands_str_nesw = deck52.random_deal().split()
    dealer = random.choice('NESW')
    
    auction_padded = [14] * 4  # Replace 'PAD_START' with 14
    played_cards = []
    bids = [0] * 4  # Initialize bids for each player
    tricks_won = [0] * 4  # Initialize tricks won for each player

    turn_i = ('NESW'.index(dealer) + 1) % 4

    # Auction phase
    while not bidding.auction_over(auction_padded):
        pov = 'NESW'[turn_i]
        is_dumb_status = is_dumb[pov]  # Get the dumb status for the current player
        is_risky_status = is_risky[pov]  # Get the risky status for the current player
        bid = call_api(pov, dealer, hands_str_nesw, auction_padded, played_cards, is_sandbag_on, is_dumb_status, is_risky_status)
        auction_padded[turn_i] = bid
        bids[turn_i] = int(bid) if bid.isdigit() else 0  # Track the bid
        turn_i = (turn_i + 1) % 4

    turn_i = ('NESW'.index(dealer) + 1) % 4
    current_trick = []

    # Play phase
    while len(played_cards) < 52:
        if len(current_trick) == 4:
            trick_winner_i = (turn_i + deck52.get_trick_winner_i(current_trick)) % 4  # Spades is always trump
            tricks_won[trick_winner_i] += 1  # Track the trick winner
            current_trick = []
            turn_i = trick_winner_i

        pov = 'NESW'[turn_i]
        is_dumb_status = is_dumb[pov]  # Get the dumb status for the current player
        is_risky_status = is_risky[pov]  # Get the risky status for the current player
        card = call_api(pov, dealer, hands_str_nesw, auction_padded, played_cards, is_sandbag_on, is_dumb_status, is_risky_status)
        played_cards.append(card)
        current_trick.append(Card.from_symbol(card).code())
        turn_i = (turn_i + 1) % 4

    # Print the final summary
    
    print_game_visualization(hands_str_nesw, auction_padded, played_cards, dealer)
    print_game_summary(bids, tricks_won)
    print(to_bbo_handviewer(hands_str_nesw, auction_padded, played_cards, dealer))

def call_api(pov, dealer, hands_str_nesw, auction_padded, played_cards, is_sandbag_on, is_dumb_status, is_risky_status):
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
        f'http://localhost/u_bm/robot.php?botstyle=advanced&sc=MP&pov={pov}&d={dealer}&n={hands_str_nesw[0]}&e={hands_str_nesw[1]}&s={hands_str_nesw[2]}&w={hands_str_nesw[3]}&h={history}&b={is_sandbag_on}&dumb={is_dumb_status}&risky={is_risky_status}'
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


def print_game_visualization(hands_str_nesw, auction_padded, played_cards, dealer):
    """
    Prints an ASCII visualization of the game state trick by trick.

    Args:
        hands_str_nesw: List of strings representing the hands of North, East, South, and West.
        auction_padded: List representing the auction history.
        played_cards: List of all cards played in the game, in the order they were played.
        dealer: The player who dealt the cards ('N', 'E', 'S', 'W').
    """
    print("\n" + "=" * 50 + " GAME VISUALIZATION " + "=" * 50)

    print("\nDealer: {}".format(dealer))
    # Print the auction
    print("\nAuction:")
    for i, bid in enumerate(auction_padded):
        print(f"{'NESW'[i % 4]}: {bid if bid != 14 else 'PASS'}", end="  ")
    print("\n" + "-" * 100)

    # Print the hands of each player
    print("\nHands:")
    for i, hand in enumerate(hands_str_nesw):
        print(f"{'NESW'[i]}: {hand}")

    # Print the played cards trick by trick
    print("\nPlayed Cards (Trick by Trick):")
    starting_player = ('NESW'.index(dealer) + 1) % 4  # First trick starts with the player after the dealer
    for i in range(0, len(played_cards), 4):
        trick_cards = played_cards[i:i + 4]
        print(f"Trick {i // 4 + 1}: ", end="")
        for j, card in enumerate(trick_cards):
            player = 'NESW'[(starting_player + j) % 4]
            print(f"{player}: {card}  ", end="")
        print()
        # Update the starting player for the next trick
        if len(trick_cards) == 4:
            trick_winner = (starting_player + deck52.get_trick_winner_i(
                [Card.from_symbol(c).code() for c in trick_cards])) % 4
            starting_player = trick_winner
    print("=" * 120 + "\n")


def print_game_summary(bids, tricks_won):
    """
    Prints a summary of the game including bids and tricks won by each player.

    Args:
        bids: List of bids made by each player.
        tricks_won: List of tricks won by each player.
    """
    print("\n" + "=" * 50 + " GAME SUMMARY " + "=" * 50)
    print("\nBids:")
    for i, bid in enumerate(bids):
        print(f"{'NESW'[i]}: {bid}")

    print("\nTricks Won:")
    for i, tricks in enumerate(tricks_won):
        print(f"{'NESW'[i]}: {tricks}")
    print("=" * 120 + "\n")


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a Spades AI simulation.")
    parser.add_argument(
        '--is_sandbag_on',
        type=str,
        default='F',
        help="Set to 'T' to enable sandbagging, or 'F' to disable it (default: 'F')."
    )
    parser.add_argument(
        '--is_dumb',
        type=str,
        default='N0E0S0W0',
        help="Specify which players are dumb using the format N0E1S2W0 (default: N0E0S0W0). The higher the number, the less relevant the candidate chosen by search."
    )
    parser.add_argument(
        '--is_risky',
        type=str,
        default='NFEFSFWF',
        help="Specify which players are risky using the format NFETSTWF (default: NFEFSFWF). Use 'T' for True and 'F' for False."
    )
    args = parser.parse_args()

    # Parse the is_dumb argument into a dictionary
    is_dumb = {player: int(status) for player, status in zip(args.is_dumb[::2], args.is_dumb[1::2])}

    # Parse the is_risky argument into a dictionary
    is_risky = {player: status for player, status in zip(args.is_risky[::2], args.is_risky[1::2])}

    # Pass the parsed arguments to the main function
    t_start = time.time()
    main(args.is_sandbag_on, is_dumb, is_risky)
    print(time.time() - t_start)
