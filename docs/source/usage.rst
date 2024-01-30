Usage
=====

.. _installation:

Installation
------------

To use Lumache, first install it using pip:

.. code-block:: console

   (.venv) $ pip install lumache

Creating recipes
----------------

To retrieve a list of random ingredients,
you can use the ``lumache.get_random_ingredients()`` function:

.. py:function:: lumache.get_random_ingredients(kind=None)

   Return a list of random ingredients as strings.

   :param kind: Optional "kind" of ingredients.
   :type kind: list[str] or None
   :return: The ingredients list.
   :raise lumache.InvalidKindError: If the kind is invalid.
   :rtype: list[str]

The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

.. py:exception:: lumache.InvalidKindError

   Raised if the kind is invalid.

.. >>> from interactionfreepy import IFWork
.. >>> worker = IFWorker('http://localhost:5000')
>>> import time
>>> from interactionfreepy import IFWorker

you can use the ``IFWorker.send()`` function:

.. autofunction:: interactionfreepy.worker.IFWorker.send

or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
will raise an exception.

.. autoexception:: interactionfreepy.core.IFException