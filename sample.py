import time

import numpy as np

import binary
import bidding


def distr_vec(x):
    xpos = np.maximum(x, 0) + 0.1
    pvals = xpos / np.sum(xpos, axis=1, keepdims=True)

    p_cumul = np.cumsum(pvals, axis=1)

    indexes = np.zeros(pvals.shape[0], dtype=np.int32)
    rnd = np.random.rand(pvals.shape[0])

    for k in range(p_cumul.shape[1]):
        indexes = indexes + (rnd > p_cumul[:, k])
    
    return indexes

def distr2_vec(x1, x2):
    x1pos = np.maximum(x1, 0) + 0.1
    x2pos = np.maximum(x2, 0) + 0.1
    
    pvals1 = x1pos / np.sum(x1pos, axis=1, keepdims=True)
    pvals2 = x2pos / np.sum(x2pos, axis=1, keepdims=True)
    
    pvals = pvals1 * pvals2
    pvals = pvals / np.sum(pvals, axis=1, keepdims=True)
    
    return distr_vec(pvals)


def get_small_out_i(small_out):
    x = small_out.copy()
    dec = np.minimum(1, x)
    
    result = []
    while np.max(x) > 0:
        result.extend(np.nonzero(x)[0])
        x = x - dec
        dec = np.minimum(1, x)
        
    return result


def sample_cards_vec(n_samples, p_hcp, p_shp, my_hand):
    deck = np.ones(52)

    # unseen A K
    ak = np.zeros(52, dtype=int)
    ak[[0,1,13,14,26,27,39,40]] = 1

    ak_out = ak - ak * my_hand
    ak_out_i_list = list(np.nonzero(ak_out)[0])
    ak_out_i = np.zeros((n_samples, len(ak_out_i_list)), dtype=int)
    ak_out_i[:, :] = np.array(ak_out_i_list)

    my_hand_small = my_hand * (1 - ak)

    small = deck * (1 - ak)

    small_out = small - my_hand_small
    small_out_i_list = get_small_out_i(small_out)
    small_out_i = np.zeros((n_samples, len(small_out_i_list)), dtype=int)
    small_out_i[:, :] = np.array(small_out_i_list)

    c_hcp = p_hcp.copy()
    c_shp = p_shp.copy().reshape((3, 4))

    r_hcp = np.zeros((n_samples, 3)) + c_hcp
    r_shp = np.zeros((n_samples, 3, 4)) + c_shp

    lho_pard_rho = np.zeros((n_samples, 3, 52), dtype=int)
    cards_received = np.zeros((n_samples, 3), dtype=int)

    ak_out_i = np.vectorize(np.random.permutation, signature='(n)->(n)')(ak_out_i)
    small_out_i = np.vectorize(np.random.permutation, signature='(n)->(n)')(small_out_i)
        
    s_all = np.arange(n_samples)

    # distribute A and K
    js = np.zeros(n_samples, dtype=int)
    while np.min(js) < ak_out_i.shape[1]:
        cards = ak_out_i[s_all, js]
        receivers = distr2_vec(r_shp[s_all,:,cards//13], r_hcp)

        can_receive_cards = cards_received[s_all, receivers] < 13

        cards_received[s_all[can_receive_cards], receivers[can_receive_cards]] += 1
        lho_pard_rho[s_all[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards]] += 1
        r_hcp[s_all[can_receive_cards], receivers[can_receive_cards]] -= 3
        r_shp[s_all[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards] // 13] -= 0.5
        js[can_receive_cards] += 1

    # distribute small cards
    js = np.zeros(n_samples, dtype=int)
    while True:
        s_all_r = s_all[js < small_out_i.shape[1]]
        if len(s_all_r) == 0:
            break

        js_r = js[s_all_r]

        cards = small_out_i[s_all_r, js_r]
        receivers = distr_vec(r_shp[s_all_r,:,cards//13])

        can_receive_cards = cards_received[s_all_r, receivers] < 13

        cards_received[s_all_r[can_receive_cards], receivers[can_receive_cards]] += 1
        lho_pard_rho[s_all_r[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards]] += 1
        r_shp[s_all_r[can_receive_cards], receivers[can_receive_cards], cards[can_receive_cards] // 13] -= 0.5
        js[s_all_r[can_receive_cards]] += 1

    # re-apply constraints
    accept_hcp = np.ones(n_samples).astype(bool)

    for i in range(3):
        if np.round(c_hcp[i]) >= 11:
            accept_hcp &= binary.get_hcp(lho_pard_rho[:,i,:]) >= np.round(c_hcp[i]) - 5
        
    accept_shp = np.ones(n_samples).astype(bool)

    for i in range(3):
        for j in range(4):
            if np.round(c_shp[i,j] >= 5):
                accept_shp &= np.sum(lho_pard_rho[:,i,(j*8):((j+1)*8)], axis=1) >= np.round(c_shp[i,j]) - 1

    accept = accept_hcp & accept_shp

    if np.sum(accept) > 10:
        return lho_pard_rho[accept]
    else:
        return lho_pard_rho


def sample_cards_auction(n_samples, auction, nesw_i, hand, vuln, bidder_model, binfo_model):
    n_steps = 1 + len(auction) // 4

    A = binary.get_auction_binary_4(n_steps, auction, nesw_i, hand, vuln)
    A_lho = binary.get_auction_binary_4(n_steps, auction, (nesw_i + 1) % 4, hand, vuln)
    A_pard = binary.get_auction_binary_4(n_steps, auction, (nesw_i + 2) % 4, hand, vuln)
    A_rho = binary.get_auction_binary_4(n_steps, auction, (nesw_i + 3) % 4, hand, vuln)

    p_hcp, p_shp = binfo_model.model(A)

    p_hcp = p_hcp.reshape((-1, n_steps, 3))[:,-1,:]
    p_shp = p_shp.reshape((-1, n_steps, 12))[:,-1,:]

    print(f'p_hcp={p_hcp}')
    print(f'p_shp={p_shp}')

    lho_pard_rho = sample_cards_vec(n_samples, p_hcp[0], p_shp[0], hand.reshape(52))

    n_samples = lho_pard_rho.shape[0]

    X_lho = np.zeros((n_samples, n_steps, A_lho.shape[-1]))
    X_pard = np.zeros((n_samples, n_steps, A_pard.shape[-1]))
    X_rho = np.zeros((n_samples, n_steps, A_rho.shape[-1]))

    X_lho[:,:,:] = A_lho
    X_lho[:,:,2:6] = binary.get_shape(lho_pard_rho[:,0,:]).reshape((-1, 1, 4)) / 4
    X_lho[:,:,6] = np.sum(binary.get_points(lho_pard_rho[:,0,:]), axis=1, keepdims=True) / 10
    X_lho[:,:,7] = np.sum(binary.get_controls(lho_pard_rho[:,0,:]), axis=1, keepdims=True) / 4
    X_lho[:,:,8:12] = binary.get_points(lho_pard_rho[:,0,:]).reshape((-1, 1, 4)) / 4
    X_lho[:,:,12:16] = binary.get_controls(lho_pard_rho[:,0,:]).reshape((-1, 1, 4))
    lho_actual_bids = bidding.get_bid_ids(auction, (nesw_i + 1) % 4, n_steps)
    lho_sample_bids = bidder_model.model_seq(X_lho).reshape((n_samples, n_steps, -1))

    X_pard[:,:,:] = A_pard
    X_pard[:,:,2:6] = binary.get_shape(lho_pard_rho[:,1,:]).reshape((-1, 1, 4)) / 4
    X_pard[:,:,6] = np.sum(binary.get_points(lho_pard_rho[:,1,:]), axis=1, keepdims=True) / 10
    X_pard[:,:,7] = np.sum(binary.get_controls(lho_pard_rho[:,1,:]), axis=1, keepdims=True) / 4
    X_pard[:,:,8:12] = binary.get_points(lho_pard_rho[:,1,:]).reshape((-1, 1, 4)) / 4
    X_pard[:,:,12:16] = binary.get_controls(lho_pard_rho[:,1,:]).reshape((-1, 1, 4))
    pard_actual_bids = bidding.get_bid_ids(auction, (nesw_i + 2) % 4, n_steps)
    pard_sample_bids = bidder_model.model_seq(X_pard).reshape((n_samples, n_steps, -1))

    X_rho[:,:,:] = A_rho
    X_rho[:,:,2:6] = binary.get_shape(lho_pard_rho[:,2,:]).reshape((-1, 1, 4)) / 4
    X_rho[:,:,6] = np.sum(binary.get_points(lho_pard_rho[:,2,:]), axis=1, keepdims=True) / 10
    X_rho[:,:,7] = np.sum(binary.get_controls(lho_pard_rho[:,2,:]), axis=1, keepdims=True) / 4
    X_rho[:,:,8:12] = binary.get_points(lho_pard_rho[:,2,:]).reshape((-1, 1, 4)) / 4
    X_rho[:,:,12:16] = binary.get_controls(lho_pard_rho[:,2,:]).reshape((-1, 1, 4))
    rho_actual_bids = bidding.get_bid_ids(auction, (nesw_i + 3) % 4, n_steps)
    rho_sample_bids = bidder_model.model_seq(X_rho).reshape((n_samples, n_steps, -1))

    min_scores = np.ones(n_samples)

    for i in range(n_steps):
        if lho_actual_bids[i] not in (bidding.BID2ID['PAD_START'], bidding.BID2ID['PAD_END']):
            min_scores = np.minimum(min_scores, lho_sample_bids[:,i,lho_actual_bids[i]])
        if pard_actual_bids[i] not in (bidding.BID2ID['PAD_START'], bidding.BID2ID['PAD_END']):
            min_scores = np.minimum(min_scores, pard_sample_bids[:,i,pard_actual_bids[i]])
        if rho_actual_bids[i] not in (bidding.BID2ID['PAD_START'], bidding.BID2ID['PAD_END']):
            min_scores = np.minimum(min_scores, rho_sample_bids[:,i,rho_actual_bids[i]])

    accept_threshold = 0.1

    accepted_samples = lho_pard_rho[min_scores > accept_threshold]

    i_try = 0
    while accepted_samples.shape[0] < 10 and i_try <= 100:
        accept_threshold *= 0.9
        accepted_samples = lho_pard_rho[min_scores > accept_threshold]
        i_try += 1
    
    if i_try >= 100:
        accepted_samples = lho_pard_rho

    print(f'accept_threshold={accept_threshold}')

    return accepted_samples
