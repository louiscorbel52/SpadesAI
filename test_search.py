import binary
import numpy as np
import time
import conf

from nn.models import Models
from robot import play_search, plot_sample_hand
from search import Searcher

models = Models.from_conf(conf.load('default.conf'))

# TODO: turn this into a proper unittest suit

def test_1():
    hands_str_nesw = [
        'Q.A954..7',
        '4.Q8.AJT.',
        'JT98.73..',
        '.K.985.JT',
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 3
    strain_i = 3
    current_trick = [42, 46,]
    on_play_i = 1

    sample[3, 42] = 0
    sample[0, 46] = 0

    plot_sample_hand(sample, 0)

    search_for = (1, 3)
    n_decl_tricks = 7
    depth=2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=[],
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), [10, 19], on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_2():
    hands_str_nesw = [
        'J6432.75.J95.JT5',
        'AK9.KJ63.Q76.KQ9',
        '5.AT42.KT843.876',
        'QT87.Q98.A2.A432',
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 1
    strain_i = 0
    current_trick = [36, ]
    on_play_i = 3
    candidates = [26, 38]

    sample[2, 36] = 0

    plot_sample_hand(sample, 0)

    search_for = (1, 3,)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=2,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_3():
    hands_str_nesw = [
        'J9.KT..',
        'T.5.72.',
        'K72..6.',
        'AQ.Q9..',
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 1
    strain_i = 0
    current_trick = [33, 34]
    on_play_i = 3
    candidates = [2, 18]

    sample[1, 33] = 0
    sample[2, 34] = 0

    plot_sample_hand(sample, 0)

    search_for = (1, 3,)
    n_decl_tricks = 4
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_4():
    hands_str_nesw = [
        'Q..KJ864.',
        '.JT8.T.T3',
        '..952.J87',
        'T8.9.AQ7.',
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 1
    strain_i = 2
    current_trick = [30, 38]
    on_play_i = 3
    candidates = [26, 28]

    sample[1, 30] = 0
    sample[2, 38] = 0

    plot_sample_hand(sample, 0)

    search_for = (1, 3,)
    n_decl_tricks = 7
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_4_5():
    hands_str_nesw = [
        'K97.JT.63.A743',
        'A8652..KT42.K8',
        'T43.Q65.98.QT2',
        'QJ..AQJ75.J965',
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 1
    strain_i = 1
    current_trick = []
    on_play_i = 0
    candidates = [39, 16, 7, 37, 34, 50]

    # sample[1, 30] = 0
    # sample[2, 38] = 0

    plot_sample_hand(sample, 0)

    search_for = (0, )
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_5():
    hands_str_nesw = [
        'J6.Q3.96.AQJ7',
        '85.J98.4.K654',
        'Q.KT752.5.982',
        'K974.A64.K.T3'
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 3
    strain_i = 1
    current_trick = []
    on_play_i = 3
    candidates = [1, 27]

    # sample[1, 30] = 0
    # sample[2, 38] = 0

    plot_sample_hand(sample, 0)

    search_for = (3, 1)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_6():
    hands_str_nesw = [
        '97...KJ7',
        '.T.T96.9',
        '8..875.T',
        'Q...Q86'
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 0
    strain_i = 1
    current_trick = [43, 49]
    on_play_i = 0
    candidates = [40, 42, 46]

    sample[2, 43] = 0
    sample[3, 49] = 0

    plot_sample_hand(sample, 0)

    search_for = (0, 2)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_7():
    hands_str_nesw = [
        'J8..J94.AKQ85',
        'T652.QJ93..76',
        'AKQ97..6.T932',
        '4.AT7.KT83.J4'
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 0
    strain_i = 1
    current_trick = []
    on_play_i = 0
    candidates = [3, 6]

    # sample[2, 43] = 0
    # sample[3, 49] = 0

    plot_sample_hand(sample, 0)

    search_for = (0, 2)
    n_decl_tricks = 0
    depth = 4

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_8():
    hands_str_nesw = [
        '.JT62..K53',
        'Q98..JT5.6',
        '.8.KQ6.JT9',
        '32..743.Q8'
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 0
    strain_i = 2
    current_trick = []
    on_play_i = 0
    candidates = [16, 40, 50]

    # sample[2, 43] = 0
    # sample[3, 49] = 0

    plot_sample_hand(sample, 0)

    search_for = (0, 2)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_9():
    hands_str_nesw = [
        '.K..Q',
        '.Q..K',
        '.J..J',
        '...A9'
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 3
    strain_i = 0
    current_trick = []
    on_play_i = 3
    candidates = [39, 44]

    # sample[2, 43] = 0
    # sample[3, 49] = 0

    plot_sample_hand(sample, 0)

    search_for = (1, 3)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_10():
    hands_str_nesw = [
        '7654.8.Q9765.9',
        'Q3.AQ754.832.Q',
        'AKJ2.T9832.T.7',
        'T98.KJ.AKJ4.J8'
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 3
    strain_i = 0
    current_trick = []
    on_play_i = 3
    candidates = [14, 42, 45]

    # sample[2, 43] = 0
    # sample[3, 49] = 0

    plot_sample_hand(sample, 0)

    search_for = (1, 3)
    n_decl_tricks = 1
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_11():
    hands_str_nesw = [
        '953.AKQJ65.73.64', 
        'KJ2.83.AKJ65.AK7',
        'QT87.T4.Q.JT983',
        'A64.9.T9842.Q52',
    ]
    sample = np.zeros((4, 52), dtype=np.uint8)
    for i in range(4):
        sample[i, :] = binary.parse_hand_f(52)(hands_str_nesw[i])
    decl_i = 1
    strain_i = 3
    current_trick = [25, 20]
    on_play_i = 0
    candidates = [13, 14, 16]

    # sample[2, 43] = 0
    # sample[3, 49] = 0

    plot_sample_hand(sample, 0)

    search_for = (0,)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    result = play_search(
        playmodel=models.peekplay,
        evalmodel=models.poseval,
        sample=sample,
        candidates=candidates,
        current_trick=current_trick,
        on_play_i=on_play_i,
        decl_i=decl_i,
        strain_i=strain_i,
        search_for=search_for,
        n_decl_tricks=n_decl_tricks,
        depth=depth,
        alpha=0,
        beta=13,
    )

    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    result = searcher.search(sample.reshape((1, 4, 52)), candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(result)
    print(f'search rtook {time.time() - t_start} seconds')

def test_12():
    samples_str = [
        '953.AKQJ65.73.64 K7.T4.AKQ65.AKJ3 QJT82.83.J.T987 A64.9.T9842.Q52',
        '953.AKQJ65.73.64 KJ2.83.AKJ65.AK7 QT87.T4.Q.JT983 A64.9.T9842.Q52',
    ] * 100
    samples = np.zeros((len(samples_str), 4, 52), dtype=np.uint8)
    for i, hand_str in enumerate(samples_str):
        hands_str_nesw = hand_str.split()
        for j in range(4):
            samples[i, j, :] = binary.parse_hand_f(52)(hands_str_nesw[j])
    
    for i in range(samples.shape[0]):
        plot_sample_hand(samples[i], 0)

    decl_i = 1
    strain_i = 3
    current_trick = [25, 20]
    on_play_i = 0
    candidates = [13, 14, 16]

    search_for = (0,)
    n_decl_tricks = 0
    depth = 2

    t_start = time.time()
    search_results_regular = []
    for sample in samples:
        result = play_search(
            playmodel=models.peekplay,
            evalmodel=models.poseval,
            sample=sample,
            candidates=candidates,
            current_trick=current_trick,
            on_play_i=on_play_i,
            decl_i=decl_i,
            strain_i=strain_i,
            search_for=search_for,
            n_decl_tricks=n_decl_tricks,
            depth=depth,
            alpha=0,
            beta=13,
        )
        search_results_regular.append(result)
    print(f'regular took {time.time() - t_start} seconds')

    t_start = time.time()
    searcher = Searcher(models.peekplay, models.poseval, decl_i, strain_i)
    search_results_vec = searcher.search(samples, candidates, on_play_i, current_trick, n_decl_tricks, depth, search_for)
    print(f'vectorized took {time.time() - t_start} seconds')

    print(search_results_regular)
    print(search_results_vec)

    

if __name__ == '__main__':
    test_12()


# practice finesse
# /u_bm/robot.php?pov=E&d=N&v=N&n=QJ32.Q4.J98643.Q&e=K7.JT8753.T.AKT3&s=96.62.K52.J87652&w=AT854.AK9.AQ7.94&h=P-1H-P-2S-P-4H-P-7H-P-P-P-C5-C4-CQ-CA-H3-H2-HA-H4-HK-HQ-H5-H6-C9-D3-CK-C2-SK-S6-S4-S2-S7-S9-SA-S3-S5-SJ-H7-C6-DT-D2

# two interesting hands
# https://www.bridgebase.com/tools/handviewer.html?d=W&v=N&a=P1SP2DP2SP3SP4SPPP&n=sK9763hAQ7d3cKJ73&e=sA5hJT43dJT962c95&s=s842hK62dAQ875cAT&w=sQJTh985dK4cQ8642&p=HJH2H5HAD3D2DAD4S2STS3S5H9HQH3H6H7H4HKH8S4SJSKSADJDQDKS6C3C5CAC2CTC4CKC9C7D6S8C6D5C8S7D9S9HTD7SQCQCJDTD8
# https://www.bridgebase.com/tools/handviewer.html?d=W&v=N&a=P1HP1SP1NP2CP3SP4HPPP&n=sJ42hAKT52dK82cKT&e=sT53h964dAT43cQ92&s=sKQ976hJ73d5cAJ85&w=sA8hQ8dQJ976c7643&p=S3S6SAS2DQDKDAD5D3H3D6D2HJHQHAH4HKH6H7H8HTH9C5D7SJS5S7S8S4STSKC3SQC4D8D4S9C6CTDTC8C7CKC2H5C9CJD9H2CQCADJ


# misplay these hands with me
# https://www.bridgebase.com/tools/handviewer.html?d=E&v=B&a=2NP3CP3SP4HP4NP5HP5NP6DP6SPPP&n=sh87532d72cK87654&e=sAQJ4hK4dAJ9cAJT2&s=sT8532hQJT6dQ4cQ3&w=sK976hA9dKT8653c9&p=S3S6C8S4S7H2SJS8DAD4D3D7DJDQDKD2HAH7H4H6C9C5CAC3D9S5D5C7HQH9H8HKC2CQS9C6DTH5CTSTS2SKC4SQD8H3CJHJD6CKSAHT
# https://www.bridgebase.com/tools/handviewer.html?d=W&v=E&a=1SP1NP2C2D3C3DPP4CPPP&n=s754hKQJdQJ872cK2&e=sAThT832dAcQT8764&s=sJ92hA954d9653cJ3&w=sKQ863h76dKT4cA95&p=HKH2H5H6HQH3HAH7H4C5HJH8S3S7SAS2STS9SKS5SQS4HTSJS8D2C4CJH9S6D7C6DAD9D4D8C7C3CAC2DKDQC8D6CTD5C9CKDJCQD3DT 
