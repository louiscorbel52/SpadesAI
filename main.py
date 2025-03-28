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

# curl 'localhost:8000/robot.php?pov=E&d=S&n=aj8532.at82.8.k4&e=t6.kj765.932.qj5&s=97.q93.ak6.97632&w=kq4.4.qjt754.at8&h=p'

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return Response(content=ERROR_XML, media_type='application/xml')

@app.get('/u_bm/robot.php')
async def robot(pov: str, d: str, n: str, e: str, s: str, w: str, h: str, b: str, dumb: str, risky: str, sc: str = 'MP', botstyle: str = 'advanced'):
    pov = pov.upper()
    dealer = d.upper()
    sc = sc.upper()
    botstyle = botstyle.lower()
    ben_bot = bots_conf.get(botstyle, bots_conf['advanced'])
    print(sc)
    auction_padded, played_cards = parse_history(dealer, h)
    is_sandbag_on = b.upper()
    is_dumb = dumb.upper()
    is_risky = risky.upper()

    hands_str_nesw = [n.upper(), e.upper(), s.upper(), w.upper()]
    
    move = None
    if not bidding.auction_over(auction_padded):
        move = ben_bot.call(pov, dealer, hands_str_nesw, auction_padded, played_cards, is_sandbag_on, is_dumb, is_risky, sc)
        bid = move.replace('PASS', 'P')
        meaning = '?'

        return Response(
            content=BID_XML.format(pov=pov, d=d, n=n, e=e, s=s, w=w, h=h, bid=bid, meaning=xml.sax.saxutils.escape(meaning)),
            media_type='application/xml',
            headers={'Access-Control-Allow-Origin': '*'}
        )

    if not move:
        move = ben_bot.call(pov, dealer, hands_str_nesw, auction_padded, played_cards, is_sandbag_on, is_dumb, is_risky, sc)

    return Response(
        content=PLAY_XML.format(pov=pov, d=d, n=n, e=e, s=s, w=w, h=h, card=move),
        media_type='application/xml',
        headers={'Access-Control-Allow-Origin': '*'}
    )


@app.get('/health')
async def health():
    return 'OK'


# python -m uvicorn main:app --host=0.0.0.0 --port=8000 --reload

PLAY_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="play" card="{card}"/>
</sc_bm>
'''

BID_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="bid" bid="{bid}" meaning="{meaning}"/>
</sc_bm>
'''

ERROR_XML ='''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="" d="" n="" e="" s="" w="" h="" rc="7" />
'''

claim_reject_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="claim" ok="n"/>
</sc_bm>
'''

claim_accept_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<sc_bm pov="{pov}" d="{d}" n="{n}" s="{s}" e="{e}" w="{w}" h="{h}" o="" bm="n" ac="n" rc="0" c="n" gv="40">
  <r type="claim" ok="y"/>
  <r type="result" result="{score}" lin="{contract}"/>
</sc_bm>
'''
