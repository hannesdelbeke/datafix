from datafix.core.session import Session
from datafix.core.node import Node, NodeState
from datafix.core.collector import Collector
from datafix.core.validator import Validator
from datafix.core.resultnode import ResultNode
from datafix.core.datanode import DataNode
# from datafix.action import Action
# from datafix.logic import Adapter

# create a default session
active_session: "Session" = Session()