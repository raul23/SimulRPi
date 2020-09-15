"""Module that defines a database for storing information about GPIO pins.

The database is created as a dictionary mapping channel numbers to objects
representing GPIO pins.

The :class:`PinDB` class provides an API for accessing this database with
such functions as retrieving or setting pins' attributes.

"""
# NOTE: on Python 3.5 and 3.6, can't use ``import SimulRPi.GPIO as GPIO``
# AttributeError: module 'SimulRPi' has no attribute 'GPIO
# if circular import
import SimulRPi.GPIO


# TODO: change to Channel?
class Pin:
    """Class that represents a GPIO pin.

    Parameters
    ----------
    channel_number : int
        GPIO channel number based on the numbering system you have specified
        (`BOARD` or `BCM`).
    channel_id : str
        Unique identifier.
    gpio_type : int
        Type of a GPIO channel: e.g. 1 (`GPIO.IN`) or 0 (`GPIO.OUT`).
    channel_name : str, optional
        It will be displayed in the terminal along with the LED symbol if it is
        available. Otherwise, the ``channel_number`` is shown. By default, its
        value is :obj:`None`.
    key : str or None, optional
        Keyboard key associated with the GPIO channel, e.g. `cmd_r`.
    led_symbols : dict, optional
        It should only be defined for output channels. It is a dictionary
        defining the symbols to be used when the LED is turned ON and OFF. If
        not found for an ouput channel, then the default LED symbols will be
        used as specified in :class:`SimulRPi.manager.Manager`.

        **Example**::

            {
                "ON": "🔵",
                "OFF": "⚪ "
            }

    pull_up_down : int or None, optional
        Initial value of an input channel, e.g. `GPIO.PUP_UP`. Default value is
        :obj:`None`.
    initial : int or None, optional
        Initial value of an output channel, e.g. `GPIO.HIGH`. Default value is
        :obj:`None`.

    Attributes
    ----------
    state : int
        State of the GPIO channel: 1 (`HIGH`) or 0 (`LOW`).

    """
    def __init__(self, channel_number, channel_id, channel_type,
                 channel_name=None, key=None, led_symbols=None,
                 pull_up_down=None, initial=None):
        self.channel_number = channel_number
        self.channel_id = channel_id
        self.channel_type = channel_type
        self.channel_name = channel_name
        self.key = key
        self.pull_up_down = pull_up_down
        self.initial = initial
        self.led_symbols = led_symbols
        # TODO: check if setting of state is good
        if self.channel_type == SimulRPi.GPIO.IN:
            # Input channel (e.g. push button)
            self.state = self.initial if self.initial else SimulRPi.GPIO.HIGH
        else:
            # Output channel (e.g. LED)
            self.state = self.initial if self.initial else SimulRPi.GPIO.LOW


# TODO: change to ChannelDB?
class PinDB:
    """Class for storing and modifying :class:`Pin`\s.

    Each instance of :class:`Pin` is saved in a dictionary that maps its
    channel number to the :class:`Pin` object.

    Attributes
    ----------
    output_pins : list
        List containing :class:`Pin` objects that are **output** channels.


    .. note::

        The dictionary (a "database" of :class:`Pin`\s) must be accessed
        through the different methods available in :class:`PinDB`, e.g.
        :meth:`get_pin_from_channel`.

    """
    def __init__(self):
        # Maps channel numbers to Pin objects
        self._pins = {}
        # TODO: explain more
        # Maps keyboard keys to Pin objects
        # NOTE: this dict is only for INPUT channels with an associated key
        self._key_to_pin_map = {}
        # List only for OUTPUT channels
        self.output_pins = []

    def create_pin(self, channel_number, channel_id, channel_type, **kwargs):
        """Create an instance of :class:`Pin` and save it in a dictionary.

        Based on the given arguments, an instance of :class:`Pin` is
        created and added to a dictionary that acts like a database of pins
        with the key being the pin's channel number and the value is an
        instance of :class:`Pin`.

        Parameters
        ----------
        channel_number : int
            GPIO channel number based on the numbering system you have specified
            (`BOARD` or `BCM`).
        channel_id : str
            Unique identifier.
        channel_type : int
            Type of a GPIO channel: e.g. 1 (`GPIO.IN`) or 0 (`GPIO.OUT`).
        kwargs : dict, optional
            These are the (optional) keyword arguments for ``Pin.__init__()``.
            See :class:`Pin` for a list of its parameters which can be included
            in ``kwargs``.

        Raises
        ------
        KeyError
            Raised if two channels are using the same channel number.

        """
        if self._pins.get(channel_number):
            # TODO: error or warning? Overwrite?
            raise KeyError("Duplicate channel numbers: {}".format(channel_number))
        self._pins[channel_number] = Pin(channel_number, channel_id,
                                         channel_type, **kwargs)
        if channel_type == SimulRPi.GPIO.OUT:
            # Output channel (e.g. LED)
            # Save the output pin so the thread that displays LEDs knows what
            # pins are OUTPUT and therefore connected to LEDs.
            self.output_pins.append(self._pins[channel_number])
        # Update the other internal dict if key is given
        if kwargs['key']:
            # Input channel (e.g. push button)
            # TODO: assert on channel_type which should be IN?
            self._key_to_pin_map[kwargs['key']] = self._pins[channel_number]

    def get_pin_from_channel(self, channel_number):
        """Get a :class:`Pin` from a given channel.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` to be
            retrieved.

        Returns
        -------
        Pin : :class:`Pin` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given channel,
            :obj:`None` is returned. Otherwise, a :class:`Pin` object is
            returned.

        """
        return self._pins.get(channel_number)

    def get_pin_from_key(self, key):
        """Get a :class:`Pin` from a given pressed/released key.

        Parameters
        ----------
        key : str
            The pressed/released key that is associated with the :class:`Pin`
            to be retrieved.

        Returns
        -------
        Pin : :class:`Pin` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given key,
            :obj:`None` is returned. Otherwise, a :class:`Pin` object is
            returned.

        """
        return self._key_to_pin_map.get(key)

    def get_pin_state(self, channel_number):
        """Get a :class:`Pin`\'s state from a given channel.

        The state associated with a :class:`Pin` can either be 1 (`HIGH`) or 0
        (`LOW`).

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose state is
            to be returned.

        Returns
        -------
        state : :obj:`int` or :obj:`None`
            If no :class:`Pin` could be retrieved based on the given channel
            number, then :obj:`None` is returned. Otherwise, the
            :class:`Pin`\'s state is returned: 1 (`HIGH`) or 0 (`LOW`).

        """
        pin = self._pins.get(channel_number)
        if pin:
            return pin.state
        else:
            return None

    def set_pin_key_from_channel(self, channel_number, key):
        """Set a :class:`Pin`\'s key from a given channel.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``key`` is set.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose key will
            be set.
        key : str
            The new keyboard key that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with `key`.
            Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            old_key = pin.key
            pin.key = key
            # TODO: only update dict if the key is different from the actual
            # pin's key but then return True or False if no update?
            # if key != old_key:
            del self._key_to_pin_map[old_key]
            self._key_to_pin_map[key] = pin
            return True
        else:
            return False

    def set_pin_name_from_channel(self, channel_number, channel_name):
        """Set a :class:`Pin`\'s channel name from a given channel number.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``channel_name`` is set.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose channel
            name will be set.
        channel_name : str
            The new channel name that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `channel_name`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update name if the name is different from the actual
            pin.channel_name = channel_name
            return True
        else:
            return False

    def set_pin_id_from_channel(self, channel_number, channel_id):
        """Set a :class:`Pin`\'s channel id from a given channel number.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``channel_id`` is set.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose channel
            id will be set.
        channel_id : str
            The new channel id that a :class:`Pin` will be updated with.

        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `channel_id`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update id if the id is different from the actual
            pin.channel_id = channel_id
            return True
        else:
            return False

    def set_pin_state_from_channel(self, channel_number, state):
        """Set a :class:`Pin`\'s state from a given channel.

        A :class:`Pin` is retrieved based on a given channel, then its
        ``state`` is set.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose state
            will be set.
        state : int
            State the GPIO channel should take: 1 (`HIGH`) or 0 (`LOW`).
        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `state`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update state if the state is different from the actual
            pin.state = state
            return True
        else:
            return False

    def set_pin_state_from_key(self, key, state):
        """Set a :class:`Pin`\'s state from a given key.

        A :class:`Pin` is retrieved based on a given key, then its
        ``state`` is set.

        Parameters
        ----------
        key : str
            The keyboard key associated with the :class:`Pin` whose state will
            be set.
        state : int
            State the GPIO channel should take: 1 (`HIGH`) or 0 (`LOW`).
        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `state`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_key(key)
        if pin:
            # TODO: only update state if the state is different from the actual
            pin.state = state
            return True
        else:
            return False

    def set_pin_symbols_from_channel(self, channel_number, led_symbols):
        """Set a :class:`Pin`\'s led symbols from a given channel.

        A :class:`Pin` is retrieved based on a given key, then its
        ``led_symbols`` is set.

        Parameters
        ----------
        channel_number : int
            GPIO channel number associated with the :class:`Pin` whose state
            will be set.
        led_symbols : dict
            It is a dictionary defining the symbols to be used when the LED is
            turned ON and OFF. See :class:`Pin` for more info about this
            attribute.
        Returns
        -------
        retval : bool
            Returns `True` if the :class:`Pin` was successfully set with
            `led_symbols`. Otherwise, it returns `False`.

        """
        pin = self.get_pin_from_channel(channel_number)
        if pin:
            # TODO: only update symbols if the symbols is different from the actual
            pin.led_symbols = led_symbols
            return True
        else:
            return False
