import numpy as np
import bidding

def parse_history(dealer, history):
    auction = []
    play = []
    moves = []
    if history:
        moves = history.strip().upper().split('-')

    is_play = False
    for move in moves:
        if is_play:
            play.append(move)
        else:
            if move.isdigit() and 0 <= int(move) <= 13:
                auction.append(move)
            if bidding.auction_over(auction):
                is_play = True

    auction_padded = auction  # Replace 'PAD_START' with 14
    
    return auction_padded, play

def get_history(auction_padded, played_cards):
    auction = '-'.join(map(str, auction_padded)).replace('PASS', 'P').replace('14', '').strip('-')  # Replace 'PAD_START' with 14
    play = '-'.join(played_cards)
    
    return f'{auction}-{play}'.strip('-')

def to_bbo_hand(hand):
    suits = hand.split('.')
    return f's{suits[0]}h{suits[1]}d{suits[2]}c{suits[3]}'

def to_bbo_handviewer(hands_str_nesw, auction_padded, cards_played):
    dealer = 'NESW'[bidding.get_dealer_i(auction_padded)]
    auction_bbo = '-'.join(map(str, auction_padded)).replace('PASS', 'P').replace('14', '').replace('-', '')  # Replace 'PAD_START' with 14
    h_bbo = [to_bbo_hand(hand) for hand in hands_str_nesw]
    return f'https://www.bridgebase.com/tools/handviewer.html?d={dealer}&a={auction_bbo}&n={h_bbo[0]}&e={h_bbo[1]}&s={h_bbo[2]}&w={h_bbo[3]}&p={"".join(cards_played)}'

def from_bbo_hand(bbo_hand):
    '''
    S843HJTDAKQ5CK543 --> 843.JT.AKQ5.K543
    '''
    suit_indexes = [bbo_hand.index(s) for s in 'SHDC']
    suits = []
    for i in range(3):
        suits.append(bbo_hand[suit_indexes[i] + 1 : suit_indexes[i + 1]])
    suits.append(bbo_hand[suit_indexes[3]+1 : ])
    return '.'.join(suits)

SUIT_MASK = np.array([
    [1] * 13 + [0] * 39,
    [0] * 13 + [1] * 13 + [0] * 26,
    [0] * 26 + [1] * 13 + [0] * 13,
    [0] * 39 + [1] * 13,
], dtype=np.int32)

def follow_suit(cards_softmax, own_cards, trick_suit, spades_broken, n_trick_cards):
    assert cards_softmax.shape[1] == 52
    assert own_cards.shape[1] == 52
    assert trick_suit.shape[1] == 4
    assert trick_suit.shape[0] == cards_softmax.shape[0]
    assert cards_softmax.shape[0] == own_cards.shape[0]

    suit_defined = np.max(trick_suit, axis=1) > 0
    trick_suit_i = np.argmax(trick_suit, axis=1)

    mask = (own_cards > 0).astype(np.int32)

    has_cards_of_suit = np.sum(mask * SUIT_MASK[trick_suit_i], axis=1) > 0

    mask[suit_defined & has_cards_of_suit] *= SUIT_MASK[trick_suit_i[suit_defined & has_cards_of_suit]]

    # If spades are not broken and it's the first card of the trick, spades cannot be played
    ## DEBUG - REMOVING THIS CONDITION TO SEE IF IT IS WAS IS CAUSING EMPTY CANDIDATES IN SEARCH
    ##if not spades_broken and n_trick_cards == 0:
    ##    mask[:, 39:52] = 0  # Spades are in the range 39-51

    legal_cards_softmax = cards_softmax * mask

    s = np.sum(legal_cards_softmax, axis=1, keepdims=True)
    s[s < 1e-9] = 1e-9
    import pdb; pdb.set_trace()
    return legal_cards_softmax / s

def hands_bin_52_to_32(hands_np):
    n_samples = hands_np.shape[0]
    hands32 = np.zeros((n_samples, 4, 4, 8))

    hands_np_reshaped = hands_np.reshape((n_samples, 4, 4, 13))
    # TODO: maybe vectorize this
    for i in range(4):
        for j in range(4):
            hands32[:, i, j, :7] = hands_np_reshaped[:, i, j, :7]
            hands32[:, i, j, 7] = hands_np_reshaped[:, i, j, 7:].sum(axis=1)

    return hands32.reshape((n_samples, 4, -1))

def get_norm_lookup(dead_cards):
    norm_lookup = np.arange(52).reshape((4, 13)) 

    for card_i in range(52):
        if card_i in dead_cards:
            suit = card_i // 13
            rank = card_i % 13

            for j in range(rank + 1, 13):
                norm_lookup[suit, j] -= 1
    
    return norm_lookup.reshape(52)

def normalize_hands(samples):
    # TODO: the live_cards doesn't work properly for multiple samples because it only looks at sample 0
    # => vectorized form can only be used for bidding eval.
    live_cards = set()
    for i in range(4):
        live_cards = live_cards.union(set(samples[0, i].nonzero()[0]))
    dead_cards = set(range(52)) - live_cards

    norm_lookup = get_norm_lookup(dead_cards)

    hands_norm = np.zeros_like(samples)
    for card_i in live_cards:
        norm_i = norm_lookup[card_i]
        for k in range(4):
            hands_norm[:,k,norm_i] = samples[:,k,card_i]
    
    return hands_norm


def eval_position(poseval_model, samples, on_play_i):
    n_samples = samples.shape[0]
    n_cards = int(samples[0, 0].sum())
    X = np.zeros((n_samples, 4*32 + 4 + 5 + 4 + 14), dtype=np.uint8)
    s_all = np.arange(n_samples)

    hands_norm = normalize_hands(samples)
    
    hands_norm_32 = hands_bin_52_to_32(hands_norm)

    X[:, 4*32 + 4 + 5 + on_play_i] = 1  # one-hot who is on lead NESW
    X[:, 4*32 + 4 + 5 + 4 + n_cards] = 1  # one-hot max possible trick number available now

    X[:, :32] = hands_norm_32[:,0]
    X[:, 32:64] = hands_norm_32[:,1]
    X[:, 64:96] = hands_norm_32[:,2]
    X[:, 96:128] = hands_norm_32[:,3]

    p_tricks = poseval_model.model(X)

    return p_tricks
