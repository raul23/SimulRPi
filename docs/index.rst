.. SimulRPi documentation master file, created by
   sphinx-quickstart on Wed Jul 29 00:28:09 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SimulRPi's documentation
========================

.. raw:: html

   <p align="center"><img src="https://raw.githubusercontent.com/raul23/SimulRPi/master/docs/_static/images/SimulRPi_logo.png">
   <br> 🚧 &nbsp;&nbsp;&nbsp;<b>Work-In-Progress</b>
   </p>

.. toctree::
   :maxdepth: 2
   :caption: Contents

   README_docs
   api_reference

**SimulRPi** is a library that partly fakes
`RPi.GPIO <https://pypi.org/project/RPi.GPIO/>`_ and simulates some I/O devices
on a Raspberry Pi (RPi).

.. raw:: html

   <div align="center">
   <img src="https://raw.githubusercontent.com/raul23/images/master/Darth-Vader-RPi/terminal_leds_active.gif"/>
   <p><b>Simulating LEDs on an RPi via a terminal</b></p>
   </div>

Each circle represents a blinking LED connected to an RPi and the number
between brackets is the associated GPIO channel number. Here the "LED" on
channel 22 toggles between on and off when a key is pressed.

See the `README <README_docs.html>`_ for more info about the library.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
