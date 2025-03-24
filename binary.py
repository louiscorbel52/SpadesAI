import numpy as np
import bidding

def get_cards_from_binary_hand(hand):
    cards = []
    for i, count in enumerate(hand):
        for _ in range(int(count)):
            cards.append(i)
    return np.array(cards)

def get_binary_hand_from_cards(cards):
    hand = np.zeros(32)
    for card in cards:
        hand[int(card)] += 1
    return hand

CARD_INDEX_LOOKUP = dict(
    zip(
        ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'],
        range(13)
    )
)

def get_card_index(card, n_cards):
    assert(n_cards % 4 == 0)
    x_card_index = n_cards // 4 - 1
    if card not in CARD_INDEX_LOOKUP:
        return x_card_index
    return min(CARD_INDEX_LOOKUP[card], x_card_index)

def parse_hand_f(n_cards):
    def f(hand):
        x = np.zeros((1, n_cards))
        suits = hand.split('.')
        assert(len(suits) == 4)
        for suit_index in [0, 1, 2, 3]:
            for card in suits[suit_index]:
                card_index = get_card_index(card, n_cards)
                x[0, suit_index * n_cards // 4 + card_index] += 1
        return x
    return f

def get_shape(hand):
    return np.sum(hand.reshape((hand.shape[0], 4, -1)), axis=2)

def get_hcp(hand):
    x = hand.reshape((hand.shape[0], 4, -1))
    A = np.zeros_like(x)
    A[:,:,0] = 1
    K = np.zeros_like(x)
    K[:,:,1] = 1
    Q = np.zeros_like(x)
    Q[:,:,2] = 1
    J = np.zeros_like(x)
    J[:,:,3] = 1

    points = 4 * A * x + 3 * K * x + 2 * Q * x + J * x

    return np.sum(points, axis=(1,2))

POINTS = np.array([4.5, 3, 1.5, 0.75, 0.25])
CONTROLS = np.array([2, 1])

def get_val(hand, values):
    n_samples, n_dim = hand.shape
    part = np.zeros(n_dim // 4)
    part[:len(values)] = values
    tiled_values = np.tile(part, 4)

    return (hand * tiled_values).reshape((n_samples, 4, n_dim // 4)).sum(axis=2)

def get_points(hand):
    return get_val(hand, POINTS)

def get_controls(hand):
    return get_val(hand, CONTROLS)

def get_auction_binary_4(n_steps, auction_input, hand_ix, hand):
    assert(len(hand.shape) == 2)

    n_samples = hand.shape[0]

    X = np.zeros((n_samples, n_steps, 16 + 4*40))
    
    auction = auction_input
    if isinstance(auction, list):
        auction_input = auction_input + ['PAD_END'] * 4 * n_steps
        auction = bidding.BID2ID['PAD_END'] * np.ones((n_samples, len(auction_input)), dtype=np.int32)

        #import pdb; pdb.set_trace()

        for i, bid in enumerate(auction_input):
            auction[:,i] = bidding.BID2ID[bid]
    
    bid_i = hand_ix
    while np.all(auction[:, bid_i] == bidding.BID2ID['PAD_START']):
        bid_i += 4

    X[:, :, 2:6] = get_shape(hand).reshape((-1, 1, 4)) / 4
    X[:, :, 6] = np.sum(get_points(hand), axis=1, keepdims=True) / 10
    X[:, :, 7] = np.sum(get_controls(hand), axis=1, keepdims=True) / 4
    X[:, :, 8:12] = get_points(hand).reshape((-1, 1, 4)) / 4
    X[:, :, 12:16] = get_controls(hand).reshape((-1, 1, 4))

    step_i = 0
    s_all = np.arange(n_samples, dtype=np.int)
    while step_i < n_steps:
        my_bid = auction[:, bid_i - 4] if bid_i -4 >= 0 else bidding.BID2ID['PAD_START']
        lho_bid = auction[:, bid_i - 3] if bid_i - 3 >= 0 else bidding.BID2ID['PAD_START']
        partner_bid = auction[:, bid_i - 2] if bid_i - 2 >= 0 else bidding.BID2ID['PAD_START']
        rho_bid = auction[:, bid_i - 1] if bid_i - 1 >= 0 else bidding.BID2ID['PAD_START']
        
        X[s_all,step_i,16+my_bid] = 1
        X[s_all,step_i,(16+40)+lho_bid] = 1
        X[s_all,step_i,(16+2*40)+partner_bid] = 1
        X[s_all,step_i,(16+3*40)+rho_bid] = 1

        step_i += 1
        bid_i += 4

    return X
