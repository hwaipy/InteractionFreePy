# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/hwaipy/InteractionFreePy/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                 |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------- | -------: | -------: | ------: | --------: |
| interactionfreepy/\_\_init\_\_.py    |       10 |        1 |     90% |        13 |
| interactionfreepy/broker.py          |      206 |       76 |     63% |29, 34-38, 51-61, 69, 79-81, 103, 105-107, 112-114, 145, 147, 203, 222-249, 274-284, 308-310, 312, 322-326, 330-334, 337, 340-345, 348-350, 353, 356, 361-373 |
| interactionfreepy/core.py            |      273 |       38 |     86% |51-60, 83, 162, 189-191, 243, 255, 269-275, 315-317, 359, 379, 389, 399, 412, 423, 489, 492-493, 514, 566, 576 |
| interactionfreepy/worker.py          |      238 |       24 |     90% |39, 44-45, 55-57, 85, 88, 105, 159, 184, 217, 249, 286, 318, 324, 333, 341-342, 349, 358-361 |
| tests/\_\_init\_\_.py                |        9 |        1 |     89% |        11 |
| tests/defines.py                     |        2 |        0 |    100% |           |
| tests/experimental/\_\_init\_\_.py   |        9 |        1 |     89% |        11 |
| tests/experimental/testRSocket.py    |        0 |        0 |    100% |           |
| tests/testIFWorkerAsync.py           |       39 |        2 |     95% |    35, 51 |
| tests/testInitBrokerAndWorker.py     |       42 |        1 |     98% |        51 |
| tests/testInvocation.py              |       51 |        1 |     98% |        91 |
| tests/testInvocationSerialization.py |      109 |        1 |     99% |       137 |
| tests/testMessageTransport.py        |      211 |        7 |     97% |125, 130, 136, 141, 160, 238, 284 |
|                            **TOTAL** | **1199** |  **153** | **87%** |           |


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