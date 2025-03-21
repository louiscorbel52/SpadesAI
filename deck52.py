import random
import numpy as np

def hand_to_str(hand):
    x = hand.reshape((4, 13))
    symbols = 'AKQJT98765432'
    suits = []
    for i in range(4):
        s = ''
        for j in range(13):
            if x[i,j] > 0:
                s += symbols[j]
        suits.append(s)
    return '.'.join(suits)

def random_deal():
    all_cards = list(range(52))
    random.shuffle(all_cards)

    hands_cards = [all_cards[:13], all_cards[13:26], all_cards[26:39], all_cards[39:]]
    hands = []

    for cards in hands_cards:
        hand = np.zeros(52, dtype=int)
        for c in cards:
            hand[c] += 1
        hands.append(hand)

    return ' '.join(map(hand_to_str, hands))

def get_trick_winner_i(trick, strain_i):
    trick_cards_suit = [card // 13 for card in trick]

    is_trumped = any([suit_i == strain_i for suit_i in trick_cards_suit])

    highest_trump_i = 0
    highest_trump = 99
    for i in range(4):
        if trick_cards_suit[i] == strain_i and trick[i] < highest_trump:
            highest_trump_i = i
            highest_trump = trick[i]

    lead_suit = trick_cards_suit[0]

    highest_lead_suit_i = 0
    highest_lead_suit = 99
    for i in range(4):
        if trick_cards_suit[i] == lead_suit and trick[i] < highest_lead_suit:
            highest_lead_suit_i = i
            highest_lead_suit = trick[i]

    return highest_trump_i if is_trumped else highest_lead_suit_i

def get_trick_winner_np(trick_np, strain_i):
    trick_cards_suit = trick_np // 13
    rank = 13 - trick_np % 13

    is_trump = trick_cards_suit == (strain_i - 1)
    is_led_suit = np.zeros_like(trick_np, dtype=np.uint8)
    is_led_suit[:,0] = 1
    is_led_suit[:,1] = np.equal(trick_cards_suit[:,0], trick_cards_suit[:,1])
    is_led_suit[:,2] = np.equal(trick_cards_suit[:,0], trick_cards_suit[:,2])
    is_led_suit[:,3] = np.equal(trick_cards_suit[:,0], trick_cards_suit[:,3])

    value = rank * is_led_suit + 100 * rank * is_trump

    return np.argmax(value, axis=1)
