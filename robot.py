import time
import sys
import numpy as np
import functools
import operator

import binary
import deck52
import scoring
import bidding

from collections import defaultdict

from sample import distr2_vec, distr_vec, sample_cards_auction
from search import Searcher
from objects import Card, CandidateBid
from util import follow_suit, eval_position, hands_bin_52_to_32, normalize_hands


class Player:

    def __init__(self, models, search=False, dd_analysis=False, n_samples=64):
        self.models = models
        self.search = search
        self.dd_analysis = dd_analysis
        self.n_samples = n_samples
        self.claim_info = None
        self.spades_broken = False  # Track if spades are broken

    def play(self, hands_bin_nesw, auction_padded, played_cards):
        ## import pdb; pdb.set_trace()
        self.claim_info = None
        assert len(played_cards) > 0

        np.random.seed(1337)

        # Ensure auction_padded only contains valid bids
        ## auction_padded = [bid for bid in auction_padded and 0 <= int(bid) <= 13]

        searcher = Searcher(self.models.peekplay, self.models.poseval)
        
        (
            tricks, 
            trick_leaders, 
            trick_winners, 
            current_trick, 
            on_play_i,
            cards_played_by,
            shown_out_suits
        ) = step_through_cardplay(auction_padded, played_cards)

        # Check if spades are broken
        for trick in tricks:
            if any(card // 13 == 3 for card in trick):
                self.spades_broken = True

        n_tricks_def_decl = [0, 0]
        n_tricks_def_decl[0] = len([twin for twin in trick_winners if twin % 2 != on_play_i % 2])
        n_tricks_def_decl[1] = len([twin for twin in trick_winners if twin % 2 == on_play_i % 2])
        print(n_tricks_def_decl)

        hand_bin = hands_bin_nesw[on_play_i] # this is the hand on play

        dummy_i = (on_play_i + 2) % 4
        cards_dummy = binary.get_cards_from_binary_hand(hands_bin_nesw[dummy_i].reshape(52))


        cards_own = binary.get_cards_from_binary_hand(hand_bin.reshape(52))

        hidden_cards = list(
            set(range(52)) - set(cards_own) - set(cards_dummy) - set(functools.reduce(operator.add, cards_played_by))
        )

        h_1_nesw, h_2_nesw = get_h1_h2_nesw(on_play_i)

        ## import pdb; pdb.set_trace()
        samples_bid_batches = []
        print(f"JUST BEFORE ENTERING FOR LOOP THAT INITIALIZE SAMPLES WITH n_samples: {self.n_samples}")
        for _ in range(self.n_samples // 16):
            h1_h2 = shuffle_cards_bidding_info(
                n_samples=16 * 4,
                binfo=self.models.binfo,
                auction_padded=auction_padded,
                hand=hand_bin,
                known_nesw=on_play_i,
                h_1_nesw=h_1_nesw,
                h_2_nesw=h_2_nesw,
                hidden_cards=hidden_cards,
                cards_played=[cards_played_by[h_1_nesw], cards_played_by[h_2_nesw]],
                shown_out_suits=[shown_out_suits[h_1_nesw], shown_out_suits[h_2_nesw]],
            )

            samples = np.zeros((h1_h2.shape[0], 4, 52), dtype=np.uint8)
            samples[:,on_play_i,:] = hand_bin
            samples[:,dummy_i,:] = hands_bin_nesw[dummy_i]
            samples[:,h_1_nesw,:] = h1_h2[:,0,:]
            samples[:,h_2_nesw,:] = h1_h2[:,1,:]
            print("_: {}".format(_))
            print("samples[:,on_play_i,:] : {}".format(samples[:,on_play_i,:]))
            print("samples[:,dummy_i,:] : {}".format(samples[:,dummy_i,:]))
            print("samples[:,h_1_nesw,:] : {}".format(samples[:,h_1_nesw,:]))
            print("samples[:,h_2_nesw,:] : {}".format(samples[:,h_2_nesw,:]))

            samples_bid_batch, _, _ = sample_accept_auction(
                samples,
                h_1_nesw=h_1_nesw,
                h_2_nesw=h_2_nesw,
                auction_padded=auction_padded,
                bidder_model=self.models.bidder_model
            )
            print("samples_bid_batch: {}".format(samples_bid_batch))
            samples_bid_batches.append(samples_bid_batch)

        samples_bid = np.concatenate(samples_bid_batches)
        ## import pdb; pdb.set_trace()

        print(f'{samples_bid.shape[0]} samples')

        n_dd_samples = self.n_samples

        weights = self.accept_samples_play(samples_bid[:n_dd_samples], (h_1_nesw, h_2_nesw), played_cards)
        weights_play = weights / weights.sum()

        # remove played cards
        for nesw_i, cards_played in enumerate(cards_played_by):
            samples_bid[:, nesw_i, cards_played] -= 1
        
        trick_np = np.zeros((samples_bid.shape[0], 4), dtype=np.uint16)
        for i, card in enumerate(current_trick):
            trick_np[:,i] = card 

        p_peek = play_next_card(self.models.peekplay, samples_bid[:n_dd_samples], current_trick, on_play_i, self.spades_broken)
        peek_scores = np.mean(p_peek, axis=0)

        trick_suit = np.zeros((1, 4), dtype=np.uint8)
        if current_trick:
            trick_suit[0, current_trick[0] // 13] = 1
        
        ##import pdb; pdb.set_trace()
        p_card = follow_suit(peek_scores.reshape((1, -1)), samples_bid[0, on_play_i].reshape((1, 52)), trick_suit, self.spades_broken, len(current_trick))
        candidates = [(p_card[0, c], c) for c in np.nonzero(p_card[0])[0] if p_card[0, c] >= 0.01]  # TODO: magic number
        if not candidates:
            candidates = [(p_card[0, c], c) for c in np.nonzero(p_card[0])[0]]
        candidates = sorted(candidates, reverse=True)
        candidates = [c for _, c in candidates]

        peek_card = candidates[0]
        card = peek_card

        is_maximizer = False
        if (on_play_i % 2) == (on_play_i % 2):
            is_maximizer = True

        search_scores = {}
        ## import pdb; pdb.set_trace()
        if self.search and len(candidates) > 1:
             
            search_results_vec = defaultdict(list)
            search_results = defaultdict(list)
            search_for = ()

            sample_results_vec = []
            t_start = time.time()
            ## import pdb; pdb.set_trace()
            sample_results_vec = searcher.search(samples_bid[:n_dd_samples], candidates, on_play_i, current_trick, 0, 13, search_for, self.spades_broken)
            print(f'search took {time.time() - t_start} seconds')
            for s_result in sample_results_vec:
                for card, ev in s_result.items():
                    search_results_vec[card].append(ev)
            search_results = search_results_vec

            sorted_cards = []
            for c, vals in search_results.items():
                e_tricks = n_tricks_def_decl[1] + np.array(vals) if is_maximizer else 13 - n_tricks_def_decl[1] - np.array(vals)
                e_vals = e_tricks
                w_insta_factor = 0.5
                sorted_cards.append((
                    e_vals @ weights_play + w_insta_factor * p_card[0, c], c
                ))
            sorted_cards = [(v, k) for k, v in sorted(sorted_cards, reverse=True)]

            print('search sorted_cards:', sorted_cards)

            search_scores = dict(sorted_cards)
            best_card, _ = sorted_cards[0]
            card = best_card

        return Card.from_code(card).symbol()


    def accept_samples_play(self, samples_in, hidden_indexes_nesw, played_cards):
        on_play_i = (len(played_cards) + 1) % 4

        samples = samples_in.copy()

        n_samples = samples.shape[0]
        score_played_card = np.ones((n_samples, len(played_cards)))
        trick = []
        trick_leader_i = on_play_i
        
        for k, card in enumerate(played_cards):
            if len(trick) == 4:
                trick_winner_i = (trick_leader_i + deck52.get_trick_winner_i(trick, 3)) % 4
                on_play_i = trick_winner_i
                trick = []
                trick_leader_i = on_play_i
            
            card = Card.from_symbol(card).code()
            
            if on_play_i in hidden_indexes_nesw:
                p_peek = play_next_card(self.models.peekplay, samples, trick, on_play_i, self.spades_broken)
                
                z_peek = np.log(p_peek) - np.log(1 - p_peek)
                temperature = 4
                p_peek_t = 1 / (1 + np.exp(-(1/temperature)*z_peek))  # using temperature to be more relaxed

                score_played_card[:,k] = p_peek_t[:,card]

            trick.append(card)
            samples[:, on_play_i, card] = 0
            on_play_i = (on_play_i + 1) % 4
        
        weights = np.exp(np.sum(np.log(score_played_card), axis=1))

        return weights

    
    def opening_lead(self, hands_bin_nesw, auction_padded):
        self.claim_info = None
        np.random.seed(1337)

        on_play_i = (len(auction_padded) + 1) % 4

        if (len(auction_padded) - 1) % 4 == on_play_i:
            auction_lead = auction_padded[:-1]
        else:
            auction_lead = auction_padded + [15]  # Replace 'PAD_END' with 15

        lho_pard_rho = sample_cards_auction(1024, auction_lead, on_play_i, hands_bin_nesw[on_play_i], self.models.bidder_model, self.models.binfo)
        n_samples = lho_pard_rho.shape[0]

        # get card scores from peekplay
        X = np.zeros((n_samples, 369))
        
        X[:, :52] = hands_bin_nesw[on_play_i]
        X[:, 52:104] = lho_pard_rho[:, 0, :]
        X[:, 104:156] = lho_pard_rho[:, 1, :]
        X[:, 156:208] = lho_pard_rho[:, 2, :]
        
        p_peek = self.models.lead.model(X)
        p_peek = p_peek * hands_bin_nesw[on_play_i]
        p_peek = p_peek / p_peek.sum(axis=1, keepdims=True)
        peek_scores = np.mean(p_peek, axis=0)

        candidate_cards = (peek_scores * (peek_scores > 0.1)).nonzero()[0]

        hands_np = np.zeros((n_samples, 4, 52), dtype=np.uint8)    
        hands_np[:,0,:] = hands_bin_nesw[on_play_i] # leader. this is us
        hands_np[:,1,:] = lho_pard_rho[:,0,:] # dummy
        hands_np[:,2,:] = lho_pard_rho[:,1,:] # 3rd hand defender
        hands_np[:,3,:] = lho_pard_rho[:,2,:] # declr

        hands32 = hands_bin_52_to_32(hands_np)

        X_sd = np.zeros((n_samples, 32 + 5 + 4*32))

        # lefty
        X_sd[:,(32 + 5 + 0*32):(32 + 5 + 1*32)] = hands32[:, 0]
        # dummy
        X_sd[:,(32 + 5 + 1*32):(32 + 5 + 2*32)] = hands32[:, 1]
        # righty
        X_sd[:,(32 + 5 + 2*32):(32 + 5 + 3*32)] = hands32[:, 2]
        # declarer
        X_sd[:,(32 + 5 + 3*32):] = hands32[:, 3]

        cand_ev = {}

        for card in candidate_cards:
            suit = card // 13
            rank = min(7, card % 13)
            card32 = suit * 8 + rank
            
            X_sd[:, :32] = 0
            X_sd[:, card32] = 1

            decl_tricks_softmax = self.models.sd_model.model(X_sd)

            expected_tricks = np.mean(decl_tricks_softmax @ np.arange(14))

            card_symbol = Card.from_code(card).symbol()

            sys.stderr.write(f'lead cand {card_symbol} score={peek_scores[card]} exp_tricks={expected_tricks}\n')

            expected_value = expected_tricks
            factor = 5
            cand_ev[card_symbol] = (
                expected_value
                +
                (1 - peek_scores[card]) / factor
            )

        sorted_cards = sorted([(ev, card) for card, ev in cand_ev.items()])
        
        _, card = sorted_cards[0]

        return card


def play_next_card(playmodel, samples, current_trick, on_play_i, spades_broken):
    X = np.zeros((samples.shape[0], 369))
    n_trick_cards = len(current_trick)
    if n_trick_cards > 0:
        X[:, 312 + current_trick[n_trick_cards - 1]] = 1
    if n_trick_cards > 1:
        X[:, 260 + current_trick[n_trick_cards - 2]] = 1
    if n_trick_cards > 2:
        X[:, 208 + current_trick[n_trick_cards - 3]] = 1

    X[:, :52] = samples[:, on_play_i, :]
    X[:, 52:104] = samples[:, (on_play_i + 1) % 4, :]
    X[:, 104:156] = samples[:, (on_play_i + 2) % 4, :]
    X[:, 156:208] = samples[:, (on_play_i + 3) % 4, :]
    
    p_peek = playmodel.model(X)

    # Ensure only legal cards are considered
    trick_suit = np.zeros((samples.shape[0], 4), dtype=np.uint8)
    if n_trick_cards > 0:
        trick_suit[:, current_trick[0] // 13] = 1
    ## import pdb; pdb.set_trace()
    p_follow = follow_suit(p_peek, samples[:, on_play_i, :], trick_suit, spades_broken, n_trick_cards)

    return p_follow


class Bidder:

    def __init__(self, models, n_samples, search, min_candidate_score):
        self.models = models
        self.n_samples = n_samples
        self.search = search
        self.min_candidate_score = min_candidate_score

    def bid(self, hands_bin_nesw, auction_padded):
        np.random.seed(1337)

        hand_ix = len(auction_padded) % 4
        hand_bin = hands_bin_nesw[hand_ix]

        candidates = self.get_bid_candidates(hand_bin, auction_padded)
        candidates_sorted = candidates

        for cand in candidates_sorted:
            print(cand.to_dict())
        
        return candidates_sorted[0].bid
    
    def get_bid_candidates(self, hand_bin, auction_padded):
        n_steps = get_n_steps_auction(auction_padded)
        hand_ix = len(auction_padded) % 4
        X = binary.get_auction_binary_4(n_steps, auction_padded, hand_ix, hand_bin)

        bid_softmax = self.models.bidder_model.model_seq(X)[-1]

        candidates = []
        while True:
            bid_i = np.argmax(bid_softmax)
            if bid_softmax[bid_i] < self.min_candidate_score and len(candidates) > 0:
                break
            if bidding.can_bid(str(bid_i), auction_padded):
                candidates.append(CandidateBid(bid=str(bid_i), insta_score=bid_softmax[bid_i]))
            bid_softmax[bid_i] = 0

        return candidates
    

def step_through_cardplay(auction_padded, played_cards):
    ## import pdb; pdb.set_trace()
    tricks = []
    trick_leaders = []
    trick_winners = []
    current_trick = []
    cards_played_by = [[], [], [], []]  # nesw
    shown_out_suits = [set(), set(), set(), set()]  # nesw

    on_play_i = 0
    for card_symbol in played_cards:
        card = Card.from_symbol(card_symbol).code()

        if current_trick and current_trick[0] // 13 != card // 13:
            shown_out_suits[on_play_i].add(current_trick[0] // 13)
        
        cards_played_by[on_play_i].append(card)
        current_trick.append(card)

        if len(current_trick) == 4:
            tricks.append(current_trick)

            trick_leader_i = (on_play_i + 1) % 4
            trick_leaders.append(trick_leader_i)

            trick_winner_i = (trick_leader_i + deck52.get_trick_winner_i(current_trick, 3)) % 4  # Spades is always trump
            trick_winners.append(trick_winner_i)

            on_play_i = trick_winner_i
            current_trick = []
        else:
            on_play_i = (on_play_i + 1) % 4
    
    return tricks, trick_leaders, trick_winners, current_trick, on_play_i, cards_played_by, shown_out_suits

def get_h1_h2_nesw(on_play_i):
    h_1_nesw, h_2_nesw = -1, -1
    if on_play_i == 1: # lefty
        h_1_nesw, h_2_nesw = 0, 2
    elif on_play_i == 2: # dummy
        h_1_nesw, h_2_nesw = 1, 3
    elif on_play_i == 3: # righty
        h_1_nesw, h_2_nesw = 2, 0
    else: # declarer on play
        h_1_nesw, h_2_nesw = 3, 1
    
    return h_1_nesw, h_2_nesw


def get_n_steps_auction(auction):
    hand_i = len(auction) % 4
    i = hand_i
    while i < len(auction) and auction[i] == 14:  # Replace 'PAD_START' with 14
        i += 4
    return 1 + (len(auction) - i) // 4

def get_hands_pbn(samples):
    hands_pbn = []
    for i in range(samples.shape[0]):
        hands_pbn.append(f'N:{" ".join(map(deck52.hand_to_str, samples[i]))}')
    return hands_pbn


def shuffle_cards_random(n_samples, h_1_nesw, h_2_nesw, hidden_cards, cards_played, shown_out_suits):
    n_cards_to_receive = np.array([len(hidden_cards) // 2, len(hidden_cards) - len(hidden_cards) // 2])
    
    h1_h2 = np.zeros((n_samples, 2, 52), dtype=np.uint8)

    # distribute all cards of suits which are known to have shown out
    cards_shownout_suits = []
    for i, suits in enumerate(shown_out_suits):
        for suit in suits:
            for card in filter(lambda x: x // 13 == suit, hidden_cards):
                other_hand_i = (i + 1) % 2
                h1_h2[:,other_hand_i,card] += 1
                n_cards_to_receive[other_hand_i] -= 1
                cards_shownout_suits.append(card)
    
    hidden_cards = [c for c in hidden_cards if c not in cards_shownout_suits]
    cards_out = np.zeros((n_samples, len(hidden_cards)), dtype=np.uint8)
    cards_out[:,:] = hidden_cards
    cards_out = np.apply_along_axis(np.random.permutation, arr=cards_out, axis=1)

    h1_h2[:,0,cards_played[0]] = 1
    h1_h2[:,1,cards_played[1]] = 1

    for i in range(n_samples):
        h1_h2[i, 0, cards_out[i, :n_cards_to_receive[0]]] = 1
        h1_h2[i, 1, cards_out[i, n_cards_to_receive[0]:]] = 1
    
    return h1_h2


def shuffle_cards_bidding_info(n_samples, binfo, auction_padded, hand, known_nesw, h_1_nesw, h_2_nesw, hidden_cards, cards_played, shown_out_suits):
    n_cards_to_receive = np.array([len(hidden_cards) // 2, len(hidden_cards) - len(hidden_cards) // 2])

    n_steps = 1 + len(auction_padded) // 4

    A = binary.get_auction_binary_4(n_steps, auction_padded, known_nesw, hand)

    p_hcp, p_shp = binfo.model(A)

    p_hcp = p_hcp.reshape((-1, n_steps, 3))[:,-1,:]
    p_shp = p_shp.reshape((-1, n_steps, 12))[:,-1,:]

    p_hcp = p_hcp[0, [(h_1_nesw - known_nesw) % 4 - 1, (h_2_nesw - known_nesw) % 4 - 1]]
    p_shp = p_shp.reshape((3, 4))[[(h_1_nesw - known_nesw) % 4 - 1, (h_2_nesw - known_nesw) % 4 - 1], :]

    c_hcp = p_hcp.copy()
    c_shp = p_shp.copy()

    h1_h2 = np.zeros((n_samples, 2, 52), dtype=np.uint8)
    cards_received = np.zeros((n_samples, 2), dtype=np.uint8)

    card_hcp = [4,3,2,1,0,0,0,0,0,0,0,0,0] * 4

    # acknowledge all played cards
    for i, cards in enumerate(cards_played):
        for c in cards:
            p_hcp[i] -= card_hcp[c] / 1.2
            suit = c // 13
            p_shp[i,suit] -= 0.5

    # distribute all cards of suits which are known to have shown out
    cards_shownout_suits = []
    for i, suits in enumerate(shown_out_suits):
        for suit in suits:
            for card in filter(lambda x: x // 13 == suit, hidden_cards):
                other_hand_i = (i + 1) % 2
                h1_h2[:,other_hand_i,card] += 1
                cards_received[:,other_hand_i] += 1
                p_hcp[other_hand_i] -= card_hcp[card] / 1.2
                p_shp[other_hand_i,suit] -= 0.5
                cards_shownout_suits.append(card)

    AK = {0, 1, 13, 14, 26, 27, 39, 40}
    hidden_cards = [c for c in hidden_cards if c not in cards_shownout_suits]
    ak_cards = [c for c in hidden_cards if c in AK]
    small_cards = [c for c in hidden_cards if c not in AK]

    ak_out_i = np.zeros((n_samples, len(ak_cards)), dtype=np.uint8)
    ak_out_i[:,:] = np.array(ak_cards)
    # ak_out_i = np.vectorize(np.random.permutation, signature='(n)->(n)')(ak_out_i)
    ak_out_i = np.apply_along_axis(np.random.permutation, arr=ak_out_i, axis=1)
    small_out_i = np.zeros((n_samples, len(small_cards)), dtype=np.int8)
    small_out_i[:,:] = np.array(small_cards)
    # small_out_i = np.vectorize(np.random.permutation, signature='(n)->(n)')(small_out_i)
    small_out_i = np.apply_along_axis(np.random.permutation, arr=small_out_i, axis=1)

    r_hcp = np.zeros((n_samples, 2)) + p_hcp
    r_shp = np.zeros((n_samples, 2, 4)) + p_shp

    s_all = np.arange(n_samples)

    n_max_cards = np.zeros((n_samples, 2), dtype=np.uint8) + n_cards_to_receive

    js = np.zeros(n_samples, dtype=int)
    while True:
        s_all_r = s_all[js < ak_out_i.shape[1]]
        if len(s_all_r) == 0:
            break

        js_r = js[s_all_r]
        cards = ak_out_i[s_all_r, js_r]
        receivers = distr2_vec(r_shp[s_all_r,:,cards//13], r_hcp[s_all_r])

        can_receive_cards = cards_received[s_all_r, receivers] < n_max_cards[s_all_r,receivers]

        cards_received[s_all_r[can_receive_cards], receivers[can_receive_cards]] += 1
        h1_h2[s_all_r[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards]] += 1
        r_hcp[s_all_r[can_receive_cards], receivers[can_receive_cards]] -= 3
        r_shp[s_all_r[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards] // 13] -= 0.5
        js[s_all_r[can_receive_cards]] += 1

    js = np.zeros(n_samples, dtype=int)
    while True:
        s_all_r = s_all[js < small_out_i.shape[1]]

        if len(s_all_r) == 0:
            break

        js_r = js[s_all_r]
        cards = small_out_i[s_all_r, js_r]
        receivers = distr_vec(r_shp[s_all_r,:,cards//13])

        can_receive_cards = cards_received[s_all_r, receivers] < n_max_cards[s_all_r,receivers]

        cards_received[s_all_r[can_receive_cards], receivers[can_receive_cards]] += 1
        h1_h2[s_all_r[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards]] += 1
        r_shp[s_all_r[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards] // 13] -= 0.5
        js[s_all_r[can_receive_cards]] += 1
    
    h1_h2[:,0,cards_played[0]] = 1
    h1_h2[:,1,cards_played[1]] = 1

    # re-apply constraints
    accept_hcp = np.ones(n_samples).astype(bool)

    for i in range(2):
        if np.round(c_hcp[i]) >= 11:
            accept_hcp &= binary.get_hcp(h1_h2[:,i,:]) >= np.round(c_hcp[i]) - 5
        
    accept_shp = np.ones(n_samples).astype(bool)

    for i in range(2):
        for j in range(4):
            if np.round(c_shp[i,j] >= 5):
                accept_shp &= np.sum(h1_h2[:,i,(j*13):((j+1)*13)], axis=1) >= np.round(c_shp[i,j]) - 1

    accept = accept_hcp & accept_shp

    if accept.sum() < 10:  # TODO
        return h1_h2
    
    return h1_h2[accept]

def get_bid_scores(nesw_i, auction_padded, hand, bidder_model):
    n_steps = 1 + len(auction_padded) // 4

    A = binary.get_auction_binary_4(n_steps, auction_padded, nesw_i, hand)

    X = np.zeros((hand.shape[0], n_steps, A.shape[-1]))

    X[:,:,:] = A
    X[:,:,2:6] = binary.get_shape(hand).reshape((-1, 1, 4)) / 4
    X[:,:,6] = np.sum(binary.get_points(hand), axis=1, keepdims=True) / 10
    X[:,:,7] = np.sum(binary.get_controls(hand), axis=1, keepdims=True) / 4
    X[:,:,8:12] = binary.get_points(hand).reshape((-1, 1, 4)) / 4
    X[:,:,12:16] = binary.get_controls(hand).reshape((-1, 1, 4))

    actual_bids = bidding.get_bid_ids(auction_padded, nesw_i, n_steps)
    sample_bids = bidder_model.model_seq(X).reshape((hand.shape[0], n_steps, -1))

    min_scores = np.ones(hand.shape[0])

    for i in range(n_steps):
        if actual_bids[i] not in (14, 15):  # PAD_START and PAD_END
            min_scores = np.minimum(min_scores, sample_bids[:,i,actual_bids[i]])

    return min_scores

def sample_accept_auction(samples, h_1_nesw, h_2_nesw, auction_padded, bidder_model):
    n_samples = samples.shape[0]

    min_bid_scores = np.ones(n_samples)

    for h_i_nesw in [h_1_nesw, h_2_nesw]:
        bid_scores = get_bid_scores(h_i_nesw, auction_padded, samples[:, h_i_nesw, :], bidder_model)

        min_bid_scores = np.minimum(min_bid_scores, bid_scores)

    bid_accept_threshold = 0.1
    i_try = 0
    while np.sum(min_bid_scores > bid_accept_threshold) < 10 and i_try < 100:
        bid_accept_threshold *= 0.9
        i_try += 1
    
    if i_try == 100:
        bid_accept_threshold = 0
    
    print(f'bid_accept_threshold={bid_accept_threshold}')

    return (
        samples[min_bid_scores > bid_accept_threshold],
        min_bid_scores[min_bid_scores > bid_accept_threshold],
        bid_accept_threshold
    )

def plot_tricks_softmax(tricks_softmax):
    from ascii_graph import Pyasciigraph
    
    graph = Pyasciigraph()
    for line in graph.graph('p_tricks', enumerate(tricks_softmax)):
        print(line)

def plot_sample_hand(deal, start_i, weight=None):
    hands_str = []
    for i in range(4):
        hands_str.append(deck52.hand_to_str(deal[(start_i + i) % 4, :]))
    print(' '.join(hands_str) + ' ' + (str(weight)))

def pmf_remove_outliers(pmf, min_mass):
    pmf0 = pmf * (pmf > min_mass)
    return pmf0 / pmf0.sum(axis=1, keepdims=True)
