import binary
import bidding

class Ben:

    def __init__(self, bidder, player):
        self.bidder = bidder
        self.player = player

    def call(self, pov, dealer, hands_str_nesw, auction_padded, played_cards, scoring):
        hands_bin_nesw = []
        for hand_str in hands_str_nesw:
            if hand_str is None:
                hands_bin_nesw.append(None)
            else:
                hands_bin_nesw.append(binary.parse_hand_f(52)(hand_str.upper()))

        if played_cards:
            if len(played_cards) >= 52:
                return None
            card = self.player.play(hands_bin_nesw, auction_padded, played_cards)
            return card

        if not bidding.auction_over(auction_padded):
            bid = self.bidder.bid(hands_bin_nesw, auction_padded)
            return bid
        
        if bidding.auction_over(auction_padded):
            card = self.player.opening_lead(hands_bin_nesw, auction_padded)
            return card


