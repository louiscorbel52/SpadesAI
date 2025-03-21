import binary
import bidding

class Ben:

    def __init__(self, bidder, player):
        self.bidder = bidder
        self.player = player

    def call(self, pov, dealer, vuln, hands_str_nesw, auction_padded, played_cards, scoring):
        vuln_ns_ew = get_vuln_ns_ew(vuln)

        hands_bin_nesw = []
        for hand_str in hands_str_nesw:
            if hand_str is None:
                hands_bin_nesw.append(None)
            else:
                hands_bin_nesw.append(binary.parse_hand_f(52)(hand_str.upper()))

        if played_cards:
            if len(played_cards) >= 52:
                return None
            card = self.player.play(vuln_ns_ew, hands_bin_nesw, auction_padded, played_cards, scoring)
            return card

        if not bidding.auction_over(auction_padded):
            bid = self.bidder.bid(vuln_ns_ew, hands_bin_nesw, auction_padded, scoring)
            return bid
        
        if bidding.get_contract(auction_padded):
            card = self.player.opening_lead(vuln_ns_ew, hands_bin_nesw, auction_padded, scoring)
            return card


def get_vuln_ns_ew(vul):
    return {
        'N': [True, False],
        'E': [False, True],
        'B': [True, True],
        '-': [False, False],
    }[vul]


