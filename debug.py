import bidding
import robot
import conf

from nn.models import Models

models = Models.from_conf(conf.load('default.conf'))

bidder = robot.Bidder(models, min_candidate_score=0.001)


def test_1c1dxp():
    vuln_ns_ew = [True, False]
    hands_str_nesw = [None, None, 'K42.Q76.952.AKQ6', None]
    auction_padded = ['PAD_START', 'PAD_START', '1C', '1D', 'X', 'PASS']

    bid = bidder.bid(vuln_ns_ew, hands_str_nesw, auction_padded)

    import pdb; pdb.set_trace()

def test_bw1():
    vuln_ns_ew = [False, False]
    hands_str_nesw = [None, None, 'T63.AJT8.Q3.A532', None]
    auction_padded = ['PAD_START', '3S', 'PASS', '4S', '4N', 'PASS']

    bid = bidder.bid(vuln_ns_ew, hands_str_nesw, auction_padded)

    import pdb; pdb.set_trace()

def test_2dopen():
    vuln_ns_ew = [True, False]
    hands_str_nesw = [None, None, '32.7.KJ8543.QJ62', None]
    auction_padded = ['PAD_START', 'PAD_START']

    bid = bidder.bid(vuln_ns_ew, hands_str_nesw, auction_padded)


def test_3n_overcall():
    vuln_ns_ew = [True, True]
    hands_str_nesw = [None, None, 'AJ973.AT.KQ5.874', None]
    auction_padded = ['PAD_START', '3C']

    bid = bidder.bid(vuln_ns_ew, hands_str_nesw, auction_padded)
    # 3N suggested as overcall

def test_1d_open():
    vuln_ns_ew = [True, True]
    hands_str_nesw = ['K4.Q942.Q984.KQ4', None, None, None]
    auction_padded = []

    bid = bidder.bid(vuln_ns_ew, hands_str_nesw, auction_padded)



# hangs
# /robot.php?pov=x&d=S&v=E&n=J83.K83.KJ83.T86&e=K95.A42.A5.J9752&s=AT64..T9762.AKQ4&w=Q72.QJT9765.Q4.3&h=1D-2H-3D-3H-5D-P-P-P-HQ-HK-HA-D2-D6-D4-DJ-DA-H4-D7-H5-H3-DT-DQ-DK-D5-C6-C2-CA-C3-CK-H6-C8-C5-CQ-H7-CT-C7-C4-H9-D3
#
# /robot.php?pov=x&d=E&v=-&n=KJT98.Q974.3.KQJ&e=73.AJT52.Q852.73&s=Q5.8.AK97.AT9654&w=A642.K63.JT64.82&h=P-1C-P-1S-P-2C-P-4D-P-4N-P-5C-P-6C-P-P
#
# /robot.php?pov=x&d=S&v=E&n=AT872.KQT6.KQ.97&e=J3.J7432.42.JT32&s=Q964.8.A873.AKQ4&w=K5.A95.JT965.865&h=1D-P-1S-P-3S-P-4N-P-5S-P-6S-P-P-P-CJ-CA-C5-C7-S4-S5-SA-S3-S2-SJ-SQ-SK-DJ-DQ-D2-D3-C9-C2-CK-C6-CQ-C8-H6-C3-D7-D5-DK-D4-HK-H2-H8-HA-DT-HT-H3-DA-C4-D6-S7
#
# /robot.php?pov=x&d=E&v=B&n=QJ8.7432.KJ.Q982&e=A73.K6.654.AK765&s=T.AQT98.AQ732.T3&w=K96542.J5.T98.J4&h=1C-2N-P-4H-P-P-P-CA-C3-C4-C2-CK-CT-CJ-C8-C5-ST-H5-S8-S2-SJ

# crashes
# /robot.php?sc=tp&pov=E&d=N&v=-&s=kq98.a65.t853.a5&w=t54.k84.kqj97.64&n=62.qj.a42.kqjt32&e=aj73.t9732.6.987&h=1c-p-6h-p-p-p-DK-DA

# generated wrong handviewer
# https://www.bridgebase.com/tools/handviewer.html?d=N&v=B&a=P1NRDP2CP2DPPDP2SPPP&n=s862hJ543d62cJT72&e=sQJ954hAQ2dA73cK9&s=sAKT7hK96dKQJcQ65&w=s3hT87dT9854cA843&p=DADJD4D2D3DQD5D6DKD8H3D7C5C3CJCKC9C6CAC2C4C7S4CQHAH6H7H4H2HKH8H5SAS3S2S5SKD9S6S9H9HTHJHQSQS7C8S8SJSTDTCT

# gives up trick by cashing HA
# /robot.php?pov=x&d=S&v=E&n=KJ983.A5.93.AKQ2&e=Q654.KQ7.7542.53&s=.JT84.KQJT86.986&w=AT72.9632.A.JT74&h=P-P-1S-P-1N-P-2N-P-3D-P-3H-P-3N-P-P-P-CJ-CA-C3-C6-D9-D2-DK-DA-H2-H5-HQ-H4-D4-DQ-H3-D3-DJ-H6-S3-D5-DT-S2-S8-D7-D8-H9-S9-C5-D6-S7-SJ-S4-C9-CT-CK-S5

# strange play - actually it's quite an interesting endplay :)
# /robot.php?pov=x&d=N&v=-&n=974.K763.T752.J2&e=KQJ83.Q952.8.K94&s=5.JT.KQ963.T8753&w=AT62.A84.AJ4.AQ6&h=P-1S-P-2N-P-3D-X-6S-P-P-P-DK-DA-D2-D8-S2-S4-SK-S5-SQ-D3-SA-S7-D4-D5-S3-D6-C4-C7-CA-C2-DJ-D7-S8-D9-CK-C3-C6-CJ

# strange play. flying in with the SQ
# /robot.php?pov=x&d=N&v=-&n=Q4.964.AJ9432.98&e=KJ2.KJT73.Q87.A6&s=98.AQ85.KT5.K742&w=AT7653.2.6.QJT53&h=2D-2H-3D-3S-P-4S-P-P-P-DA-D7-D5-D6-C9-CA-C2-C3-D8-DT-S3-D2-S5
# constructed
# https://www.bridgebase.com/tools/handviewer.html?d=N&v=-&a=2D2H3D3SP4SPPP&n=sQ4h964dAJ9432c98&e=sKJ2hKJT73dQ87cA6&s=shQ852dKT5cKQJT72&p=DAD7D5D6C9CAC2C3D8DTS3D2S5
# original
# https://www.bridgebase.com/tools/handviewer.html?d=N&v=-&a=2D2H3D3SP4SPPP&n=sQ4h964dAJ9432c98&e=sKJ2hKJT73dQ87cA6&s=s98hAQ85dKT5cK742&w=sAT7653h2d6cQJT53&p=DAD7D5D6C9CAC2C3D8DTS3D2S5SQSKS8DQDKSTD3SAS4S2S9CQC8C6CKC4CTD4H3CJD9H7C7C5H4HTHQH2H6HJHAH5S6H9HKS7DJSJH8


# play_search crashes
# /u_bm/robot.php?pov=x&d=N&v=N&n=T65.QJ7.AQ72.AQ6&e=QJ9..KJT985.K875&s=42.A96432.6.JT93&w=AK873.KT85.43.42&h=1N-2C-2D-P-2H-P-P-P-SQ-S2-S3-S5-SJ-S4-S7-S6-S9-H2-S8-ST-H3-H5-HJ-D5-DA-D8-D6-D3-D2-D9-H4-D4-CJ-C2-C6-CK-C5-C9-C4-CQ-CA-C7-C3-H8-SA-H7-C8-H9-CT-HT-HQ-DT-D7-DJ-HA-SK

# redoubles
# /u_bm/robot.php?pov=S&d=N&v=-&n=AKJ32.J2.K32.432&e=4.AQT3.AQ54.K765&s=5.K654.JT96.AQJT&w=QT9876.987.87.98&h=1S-X


if __name__ == '__main__':
    test_1d_open()
