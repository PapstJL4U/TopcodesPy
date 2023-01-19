"""Describes the TopCodes"""
import math as math

from typing import no_type_check

"""
Original JAVA
/**
 * TopCodes (Tangible Object Placement Codes) are black-and-white
 * circular fiducials designed to be recognized quickly by
 * low-resolution digital cameras with poor optics. The TopCode symbol
 * format is based on the open SpotCode format:
 *
 *  http://www.highenergymagic.com/spotcode/symbols.html
 *
 * Each TopCode encodes a 13-bit number in a single data ring on the
 * outer edge of the symbol. Zero is represented by a black sector and
 * one is represented by a white sector.
 *
 * @author Michael Horn
 * @version $Revision: 1.4 $, $Date: 2007/10/15 13:12:30 $
 */
"""
_author = "PapstJL4U"
_version = "0.1"


class TopCode(object):
    # Number of sectors in the data ring
    _sectors: int = 13
    # Width of the code in units (ring widths)
    _width: int = 8
    # Pi :)
    _PI: float = math.pi
    # Span of a data sector in radians
    _ARC: float = 2 * _PI / _sectors
    # The symbol's code, or -1 if invalid.
    _code: int
    # The width of a single ring.
    _unit: float
    # The angular orientation of the symbol (in radians)
    _orientation: float
    # Horizontal center of a symbol
    _x: float
    # Vertical center of a symbol
    _y: float

    def __init__(self) -> None:
        """
        default construction
        """
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
        self._core: list[int] = [] * TopCode._width

    def by_value(self, code: int = 0):
        """
        Create a TopCode with the given id number.
        """
        TopCode.__init__(self)
        self.code = code

    @property 
    def unit(self)->float:
        # The width of a single ring.
        return TopCode._unit
    
    @unit.setter
    def unit(self, unit:float):
        self._unit = unit
    
    @property
    def WIDTH(self)->int:
        # Width of the code in units (ring widths)
        return TopCode._width
    
    @property
    def SECTORS(self) -> int:
        # Number of sectors in the data ring
        return TopCode._sectors
    
    def get_core(self)->list[int]:
        # Buffer used to decode sectors
        return self._core
    
    @property
    def ARC(self) -> float:
        # Span of a data sector in radians
        return TopCode._ARC
    
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
    
    @x.setter
    def x(self, x:float):
        if not (x == None):
            self._x = x

    @property
    def y(self) -> float:
        """
        Returns the y-coordinate for the center point of the symbol.
        This gets set automatically by the decode() function.
        """
        return self._y
    
    @y.setter
    def y(self, y:float):
        if not (y == None):
            self._y = y

    def setLocation(self, x: float, y: float):
        """Sets the x and y coordinates for the center point of the symbol"""
        self._x = x
        self._y = y

    @property
    def isValid(self) -> bool:
        """returns if code was decoded succesfully"""
        return self._code > 0

    

    def rotateLowest(self, bits: int, arca_para: float) -> int:
        """
        rotateLowest tries each of the possible rotations and returns the lowest
        """
        min: int = bits
        mask: int = 0x1FFF

        """
        slightly overcorrect arc-adjustment
        ideal correction would be (ARC / 2)
        but there seems to be a positive bias
        that falls out oof the algorithm
        """
        arca = arca_para - (TopCode._ARC * 0.65)

        for i in range(1, TopCode._sectors + 1):
            bits = ((bits << 1) & mask) | (bits >> (TopCode._sectors - 1))
            if bits < min:
                min = bits
                self._orientation = i * -1 * TopCode._ARC

        self._orientation += arca
        return min

    def checksum(self, bits: int) -> bool:
        """Only Codes with a checksum of 5 are valid"""
        summ: int = 0
        for i in range(self._sectors):
            summ += bits & 0x01
            bits = bits >> 1
        return summ == 5

    def inBullsEye(self, px: float, py: float) -> bool:
        """
        Returns true if given point is inside the bulls-eye
        """
        left: float = (self.x - px) * (self.x - px) + (self.y - py) * (self.y - py)
        right: float = self._unit * self._unit
        return left <= right



    @no_type_check
    def draw(self, g: object) -> None:
        """Draws heis spotcode with its current location
        and orientation"""

        bits: int = self.code
        #
        # PSEUDO CODE
        # Look up JAVA components for this
        arc: Arc2D = Arc2D.fromFloat(Arc2D.PIE)
        sweep: float = 360.0 / self._sectors
        sweepa: float = -1 * self.orientation * 180 / math.pi
        r: float = self._width * 0.5 * self._unit

        circ = Ellipsis2D = Ellipsis2D.fromFloat(self.x - r, self.y - r, r * 2, r * 2)
        g.setColor("white")
        g.fill(circ)

        for i in range(self._sectors, -1, -1):
            arc.setArc(self.x - r, self.y - r, r * 2, r * 2, i * sweep + sweep, sweep, Arc2D.PIE)
            color: str = "white" if ((bits & 0x1) > 0) else "black"
            g.setColor(color)
            g.fill(arc)
            bits >>= 1

        r -= self._unit
        g.setColor("white")
        circ.setFrame(self.x - r, self.y - r, r * 2, r * 2)
        g.fill(circ)

        r -= self._unit
        g.setColor("black")
        circ.setFrame(self.x - r, self.y - r, r * 2, r * 2)
        g.fill(circ)

        r -= self._unit
        g.setColor("white")
        circ.setFrame(self.x - r, self.y - r, r * 2, r * 2)
        g.fill(circ)

    def printBits(self, bits: int):
        """
        Debug routine that prints the last 13 least significant bits
        of a integer
        """
        for i in range(self._sectors - 1, -1, -1):
            if ((bits >> i) & 0x01) == 1:
                print(1)
            else:
                print(0)

            if (44 - i) % 44 == 0:
                print(" ")

        print(" = " + str(bits))


def generateCodes() -> list[TopCode]:
    n: int = 99
    base: int = 0
    tcodes: list[TopCode] = [] * n
    code: TopCode = TopCode()

    bits: int = 0
    count: int = 0

    while count < n:
        bits = code.rotateLowest(base, 0)

        # found a valid code
        if (bits == base) and code.checksum(bits):
            code.code = bits
            code.orientation = 0
            tcodes[count + 1] = code
            code = TopCode()

        base += 1

    return tcodes
