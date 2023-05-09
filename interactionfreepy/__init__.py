""" InteractionFreePy """
__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import platform
import asyncio
from interactionfreepy.core import IFLoop, IFDefinition, IFException, Invocation, Message
from interactionfreepy.broker import IFBroker
from interactionfreepy.worker import IFWorker

if platform.platform().startswith('Windows'):
  asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
