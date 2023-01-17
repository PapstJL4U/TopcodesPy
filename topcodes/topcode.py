"""Describes the TopCodes"""
import math

_author = "PapstJL4U"
_version = "0.1"


class TopCode(object):
    # Number of sectors in the data ring
    _sectors: int = 13
    # Width of the code in units (ring widths)
    _width: int = 8
    # Pi :)
    _PI: float = math.Pi
    # Span of a data sector in radians
    _ARC: float = 2 * _PI / _sectors

    def __init__(self):
        # The symbol's code, or -1 if invalid.
        self._code: int = -1
        # The width of a single ring.
        self._unit: float = 72.0 / self._width
        # The angular orientation of the symbol (in radians)
        self._orientation: float = 0.0
        # Horizontal center of a symbol
        self._x: float = 0.0
        # Vertical center of a symbol
        self._y: float = 0.0
        # Buffer used to decode sectors
        self._core = []

    def by_value(self, code: int = 0):
        """
        Create a TopCode with the given id number.
        """
        self.__init__()
        self.code = code

    @property
    def code(self) -> int:
        """
        Returns the ID number for this symbol.  Calling the decode()
        function will set this value automatically.
        """
        return self._code

    @code.setter
    def code(self, code: int = 0):
        """
        Sets the ID number for this symbol.
        """
        self._code = code

    @property
    def orientation(self) -> float:
        """
        Returns the orientation of this code in radians and accurate
        to about plus or minus one degree.  This value gets set
        automatically by the decode() function.
        """
        return self._orientation

    @orientation.setter
    def orientation(self, ori: float):
        """
        Sets the angular orientation of this code in radians.
        """
        self._orientation = ori

    @property
    def diameter(self) -> float:
        """
        Returns the diameter of this code in pixels.  This value
        will be set automatically by the decode() function.
        """
        return self._unit * self._width

    @diameter.setter
    def diameter(self, dia: float):
        """
        Sets the diameter of this code in pixels.
        """
        self._unit = dia / self._width

    @property
    def x(self) -> float:
        """
        Returns the x-coordinate for the center point of the symbol.
        This gets set automatically by the decode() function.
        """
        return self._x

    @property
    def y(self) -> float:
        """
        Returns the y-coordinate for the center point of the symbol.
        This gets set automatically by the decode() function.
        """
        return self._y

    def setLocation(self, x: float, y: float):
        """Sets the x and y coordinates for the center point of the symbol"""
        self._x = x
        self._y = y

    @property
    def isValid(self) -> bool:
        """returns if code was decoded succesfully"""
        return self._code > 0

    def decode(scanner: Scanner, cx: int, cy: int) -> int:
        pass
