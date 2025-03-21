import bidding
import robot
import conf
import xml.etree.ElementTree as ET
import xml.sax.saxutils

from nn.models import Models
from ben import Ben
from util import parse_history
from robot import step_through_cardplay

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

models = Models.from_conf(conf.load('default.conf'))

MIN_CAND_SCORE = 0.05

bots_conf = {
    'advanced': Ben(
        robot.Bidder(models, n_samples=8, search=False, min_candidate_score=MIN_CAND_SCORE),
        robot.Player(models, search=True, dd_analysis=False, n_samples=16),
    ),
}


app = FastAPI()

# curl 'localhost:8000/robot.php?pov=E&d=S&v=-&n=aj8532.at82.8.k4&e=t6.kj765.932.qj5&s=97.q93.ak6.97632&w=kq4.4.qjt754.at8&h=p'

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return Response(content=ERROR_XML, media_type='application/xml')

@app.get('/u_bm/robot.php')
async def robot(pov: str, d: str, v: str, n: str, e: str, s: str, w: str, h: str, sc: str = 'MP', botstyle: str = 'advanced'):
    pov = pov.upper()
    dealer = d.upper()
    v = v.upper()
    sc = sc.upper()
    botstyle = botstyle.lower()
    ben_bot = bots_conf.get(botstyle, bots_conf['advanced'])
    print(sc)
    auction_padded, played_cards = parse_history(dealer, h)

    hands_str_nesw = [n.upper(), e.upper(), s.upper(), w.upper()]

    move = None
    if not bidding.auction_over(auction_padded):
        move = ben_bot.call(pov, dealer, v, hands_str_nesw, auction_padded, played_cards, sc)
        bid = move.replace('PASS', 'P')
        meaning = '?'

        return Response(
            content=BID_XML.format(pov=pov, d=d, v=v, n=n, e=e, s=s, w=w, h=h, bid=bid, meaning=xml.sax.saxutils.escape(meaning)),
            media_type='application/xml',
            headers={'Access-Control-Allow-Origin': '*'}
        )

    if not move:
        move = ben_bot.call(pov, dealer, v, hands_str_nesw, auction_padded, played_cards, sc)

    return Response(
        content=PLAY_XML.format(pov=pov, d=d, v=v, n=n, e=e, s=s, w=w, h=h, card=move),
        media_type='application/xml',
        headers={'Access-Control-Allow-Origin': '*'}
    )


@app.get('/health')
async def health():
    return 'OK'


# python -m uvicorn main:app --host=0.0.0.0 --port=8000 --reload

PLAY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" v="{v}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="play" card="{card}"/>
</sc_bm>
'''

BID_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" v="{v}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="bid" bid="{bid}" meaning="{meaning}"/>
</sc_bm>
'''

ERROR_XML ='''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="" d="" v="" n="" e="" s="" w="" h="" rc="7" />
'''

'''
<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="E" d="N" v="-" n="97.q93.ak6.97632" s="aj8532.at82.8.k4" e="kq4.4.qjt754.at8" w="t6.kj765.932.qj5" h="p-1d-1s-x-1n-2d-2s-p-p-p-D2-DK-D5-D8-DA-D7-C4-D3-S9-SQ-SA-S6-S2-ST-S7-S4-D9-D6-DT-S3-HA-H5-H3-H4-H2-HK-H9-C8-H7-HQ-SK-H8-DQ-S5-C5-C2-SJ-H6-C3-DJ-CK-CQ-C6-CA-D4-S8-CJ-C7-HT-HJ-C9" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="play" card="CT"/>
  <r type="result" result="N/S +110" lin="2SS="/>
</sc_bm>
'''

# https://gibrest.bridgebase.com/u_bm/u_bm.php?ios13hack=w02&t=g&s=P-P-1S-3C-4S-P-*
# u_bm/robot.php?sc=tp&pov=W&d=N&v=N&s=k.a93.qj752.kt98&w=at963.qt8.943.52&n=74.j762.ak6.a643&e=qj852.k54.t8.qj7&h=1c-1s-x-3s-p-p-p-CT-C2-CA-C7-DK-D8-x0


claim_reject_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" v="{v}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="claim" ok="n"/>
</sc_bm>
'''

claim_accept_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" v="{v}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="claim" ok="y"/>
  <r type="result" result="{score}" lin="{contract}"/>
</sc_bm>
'''
