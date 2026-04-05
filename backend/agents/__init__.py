"""HAKIX Agent Module"""
from agents.base import Agent
from agents.jasiri.agent import JasiriAgent
from agents.rift.agent import RiftAgent
from agents.sphinx.agent import SphinxAgent
from agents.shield.agent import ShieldAgent
from agents.herald.agent import HeraldAgent
from agents.kazi.agent import KaziAgent
from agents.vigil.agent import VigilAgent
from agents.atlas.agent import AtlasAgent
from agents.ledger.agent import LedgerAgent
from agents.election.poll_witness.agent import PollWitnessAgent
from agents.election.verify.agent import VerifyAgent
from agents.election.count.agent import CountAgent
from agents.election.alert.agent import AlertAgent

ALL_AGENTS = {
    "JASIRI": JasiriAgent,
    "RIFT": RiftAgent,
    "SPHINX": SphinxAgent,
    "SHIELD": ShieldAgent,
    "HERALD": HeraldAgent,
    "KAZI": KaziAgent,
    "VIGIL": VigilAgent,
    "ATLAS": AtlasAgent,
    "LEDGER": LedgerAgent,
    # Election sub-agents
    "POLL_WITNESS": PollWitnessAgent,
    "VERIFY": VerifyAgent,
    "COUNT": CountAgent,
    "ALERT": AlertAgent,
}


def get_agent(name: str, **kwargs) -> Agent:
    """Get an agent instance by name."""
    agent_cls = ALL_AGENTS.get(name.upper())
    if not agent_cls:
        raise ValueError(f"Unknown agent: {name}. Available: {list(ALL_AGENTS.keys())}")
    return agent_cls(**kwargs)
