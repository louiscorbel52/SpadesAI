import numpy as np

BID2ID = {
    'PAD_START': 14,
    'PAD_END': 15,
}

# Bids are the number of tricks from 0 to 13
TRICK_BIDS = {str(i): (i + 2) for i in range(14)}  # Adjusted indices to account for PAD_START and PAD_END
BID2ID.update(TRICK_BIDS)

ID2BID = {bid: i for i, bid in BID2ID.items()}

def encode_bid(bid):
    bid_one_hot = np.zeros((1, 16), dtype=np.float32)
    bid_one_hot[0, int(bid)] = 1
    return bid_one_hot

def can_bid(bid, auction):
    if 0 <= int(bid) <= 13:
        return True
    return False

def auction_over(auction):
    if len(auction) != 4:
        return False
    for bid in auction:
        if not (0 <= int(bid) <= 13):
            return False
    return True

def get_bid_ids(auction, player_i, n_steps):
    i = player_i
    result = []

    while len(result) < n_steps:
        if i >= len(auction):
            result.append(15)  # Use 15 as PAD_END
            continue
        call = auction[i]
        if not (call == 14 and len(result) == 0):  # Replace 'PAD_START' with 14
            result.append(int(call))
        i = i + 4

    return np.array(result)

def get_dealer_i(auction_padded):
    dealer_i = 0
    for bid in auction_padded:
        if bid == 14:  # Replace 'PAD_START' with 14
            dealer_i = (dealer_i + 1) % 4
        else:
            break
    return dealer_i
