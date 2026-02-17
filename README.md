# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/hwaipy/InteractionFreePy/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------- | -------: | -------: | ------: | --------: |
| interactionfreepy/\_\_init\_\_.py    |       10 |        1 |     90% |        13 |
| interactionfreepy/broker.py          |      210 |       79 |     62% |38-39, 44-48, 61-71, 79, 89-91, 113, 115-117, 122-124, 159, 161, 217, 236-263, 266, 291-301, 325-327, 329, 339-343, 347-351, 354, 357-362, 365-367, 370, 373, 378-390 |
| interactionfreepy/core.py            |      279 |       38 |     86% |60-69, 92, 171, 198-200, 252, 264, 278-284, 324-326, 368, 388, 398, 408, 421, 432, 498, 501-502, 523, 575, 585 |
| interactionfreepy/worker.py          |      251 |       30 |     88% |43, 49-59, 69-71, 100, 103, 120, 174, 232, 264, 301, 333, 339, 348, 356-357, 364, 373-376 |
| tests/\_\_init\_\_.py                |        9 |        1 |     89% |        11 |
| tests/defines.py                     |        2 |        0 |    100% |           |
| tests/experimental/\_\_init\_\_.py   |        9 |        1 |     89% |        11 |
| tests/experimental/testRSocket.py    |        0 |        0 |    100% |           |
| tests/testDocExamples.py             |        0 |        0 |    100% |           |
| tests/testIFWorkerAsync.py           |       39 |        3 |     92% |35, 37, 51 |
| tests/testInitBrokerAndWorker.py     |       42 |        1 |     98% |        51 |
| tests/testInvocation.py              |       51 |        1 |     98% |        91 |
| tests/testInvocationSerialization.py |      109 |        1 |     99% |       137 |
| tests/testMessageTransport.py        |      241 |        7 |     97% |126, 131, 137, 142, 161, 274, 320 |
| **TOTAL**                            | **1252** |  **163** | **87%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/hwaipy/InteractionFreePy/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/hwaipy/InteractionFreePy/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/hwaipy/InteractionFreePy/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/hwaipy/InteractionFreePy/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fhwaipy%2FInteractionFreePy%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/hwaipy/InteractionFreePy/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.