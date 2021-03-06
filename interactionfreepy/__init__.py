from interactionfreepy.core import IFLoop, IFDefinition, IFException, Invocation, Message, IFLoop
from interactionfreepy.broker import IFBroker
from interactionfreepy.worker import IFWorker

import platform, asyncio
if (platform.platform().startswith('Windows')):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
