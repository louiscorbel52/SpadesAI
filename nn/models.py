import os
import os.path

from configparser import ConfigParser

from nn.bidder import Bidder
from nn.bid_info import BidInfo
from nn.lead_singledummy import LeadSingleDummy
from nn.peekplay import Peekplay
from nn.poseval import Poseval


class Models:

    def __init__(self, bidder_model, binfo, sd_model, peekplay, poseval, lead):
        self.bidder_model = bidder_model
        self.binfo = binfo
        self.sd_model = sd_model
        self.peekplay = peekplay
        self.poseval = poseval
        self.lead = lead
    
    @classmethod
    def from_conf(cls, conf: ConfigParser) -> "Models":
        base_path = os.getenv('BEN_HOME') or '.'
        return cls(
            bidder_model=Bidder('bidder', os.path.join(base_path, conf['bidding']['bidder'])),
            binfo=BidInfo(os.path.join(base_path, conf['bidding']['info'])),
            sd_model=LeadSingleDummy(os.path.join(base_path, conf['eval']['lead_single_dummy'])),
            peekplay=Peekplay(os.path.join(base_path, conf['peekplay']['peekplay'])),
            poseval=Poseval(os.path.join(base_path, conf['poseval']['poseval'])),
            lead=Peekplay(os.path.join(base_path, conf['lead']['peekplay']))
        )
