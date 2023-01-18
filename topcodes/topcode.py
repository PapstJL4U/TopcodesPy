"""Describes the TopCodes"""
import math as math
from scanner import Scanner
from itertools import count
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

    def __init__(self)->None:
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
        self._core : list[int] = [] * TopCode._width

    def by_value(self, code: int = 0):
        """
        Create a TopCode with the given id number.
        """
        TopCode.__init__(self)
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

    def decode(self, scanner: Scanner, cx: int, cy: int) -> int:
        up: int = (
            scanner.ydist(cx, cy, -1)
            + scanner.ydist(cx - 1, cy, -1)
            + scanner.ydist(cx + 1, cy, -1)
        )
        down: int = (
            scanner.ydist(cx, cy, 1)
            + scanner.ydist(cx - 1, cy, 1)
            + scanner.ydist(cx + 1, cy, 1)
        )
        left: int = (
            scanner.xdist(cx, cy, - 1)
            + scanner.xdist(cx, cy - 1, -1)
            + scanner.xdist(cx, cy + 1, 1)
        )
        right: int = (
            scanner.xdist(cx, cy, 1)
            + scanner.xdist(cx, cy - 1, 1)
            + scanner.xdist(cx, cy + 1, 1)
        )

        self._x = cx
        self._x += (right - left) / 6.0
        self._y = cy
        self._y += (down - up) / 6.0
        self._unit = self.readUnit(scanner)
        self._code = -1
        if self._unit < 0:
            return -1

        c: int = 0
        maxc: int = 0
        arca: float = 0
        maxa: float = 0
        maxu: float = 0
        """
        Try different uit and arc adjustments, 
        save the one that produces a maximum confidence reading...
        """
        for u in range(-2, 3):
            for a in range(10):
                arca = a * TopCode._ARC * 1.0
                c = self.readCode(scanner, self._unit + (self._unit * 0.05 * u), arca)
                if c > maxc:
                    maxc = c
                    maxa = arca
                    maxu = self._unit + (self._unit * 0.05 * u)

        if maxc > 0:
            self._unit = maxu
            self.readCode(scanner, self._unit, maxa)
            self.code = self.rotateLowest(self.code, maxa)

        return self.code

    def readCode(self, scanner: Scanner, unit: float, arca: float) -> int:
        """
        Attempts to decode the binary pixels of an image into a code

        scanner - image scanner
        unit - width of single ring (codes are 8 units wide)
        arca - arc adjustment. rotation correction delta value
        """
        dx: float = 0.0
        dy: float = 0.0
        dist: float = 0.0
        c: int = 0
        sx: int = 0
        sy: int = 0
        bit: int = 0
        bits: int = 0
        self._code = -1

        # count down from Sectors down to 0
        for sector in range(TopCode._sectors - 1, -1, -1):
            dx = math.cos(TopCode._ARC * sector + arca)
            dy = math.sin(TopCode._ARC * sector + arca)

            # Take 8 samples across the diameter of the symbol
            for i in range(self._width):
                dist = (i - 3.5) * self._unit
                sx = round(self.x + dx * dist)
                sy = round(self.y + dy * dist)
                self._core[i] = scanner.getSample3x3(sx, sy)

            # white rings
            if (
                (self._core[1] <= 128)
                or (self._core[3] <= 128)
                or (self._core[4] <= 128)
                or (self._core[6] <= 128)
            ):
                return 0

            # black ring
            if (self._core[2] > 128) or (self._core[5] > 128):
                return 0

            # compute confidence in core sample
            c += (
                self._core[1]
                + self._core[3]
                + self._core[4]
                + self._core[6]
                + (0xFF - self._core[2])
                + (0xFF - self._core[5])
            )

            # data rings
            c += abs(self._core[7] * 2 - 0xFF)

            # opposite data ring
            c += 0xFF - abs(self._core[0] * 2 - 0xFF)

            bit = 1 if self._core[7] > 128 else 0
            bits <<= 1
            bits += bit

        if self.checksum(bits):
            self._code = bits
            return c
        else:
            return 0

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

    def readUnit(self, scanner: Scanner) -> float:
        """
        Determines the symbol's unit length by counting the number
        of pixels between  the outer edges of the first black ring.
        North, sount, east and west readins are taken and the average is returned
        """
        sx: int = round(self.x)
        sy: int = round(self.y)
        iwidth: int = scanner.imageW
        iheight: int = scanner.imageH

        whiteL: bool = True
        whiteR: bool = True
        whiteU: bool = True
        whiteD = bool = True
        sample: int = 0
        distL: int = 0
        distR: int = 0
        distU: int = 0
        distD: int = 0

        for i in count(start=1):
            if (
                (sx - i < 1)
                or (sx + i >= iwidth - 1)
                or (sy - i < 1)
                or (sy + i >= iheight - 1)
                or (i > 100)
            ):
                return -1

            # Left sample
            sample = scanner.getBW3x3(sx - i, sy)
            if distL <= 0:
                if whiteL and (sample == 00):
                    whiteL = False
                elif (not whiteL) and (sample == 1):
                    distL = i

            # Right sample
            sample = scanner.getBW3x3(sx + 1, sy)
            if distR <= 0:
                if whiteR and (sample == 0):
                    whiteR = False
            elif (not whiteR) and (sample == 1):
                distR = i

            # Up sample
            sample = scanner.getBW3x3(sx, sy - i)
            if distU <= 0:
                if whiteU and (sample == 0):
                    whiteU = False
                elif (not whiteU) and (sample == 1):
                    distU = i

            # Down sample
            sample = scanner.getBW3x3(sx, sy + i)
            if distD <= 0:
                if whiteD and (sample == 0):
                    whiteD = False
                elif (not whiteD) and (sample == 1):
                    distD = i

            if distR > 0 and distL > 0 and distU > 0 and distD > 0:
                u: float = (distR + distL + distU + distD) / 8.0
                if abs(distR + distL - distU - distD) > u:
                    return -1
                else:
                    return u
        return -1

    @no_type_check
    def annotate(self, g: object, scanner: Scanner) -> None:
        """drawing method"""
        dx: float = 0.0
        dy: float = 0.0
        dist: float = 0.0
        sx: float = 0.0
        sy: float = 0.0
        bits: int = 0
        for sector in range(self._sectors - 1, -1, -1):
            dx = math.cos(self._ARC * sector + self._orientation)
            dy = math.sin(self._ARC * sector + self._orientation)

            # take 8 samples across the diameter of the symbol

            sample: int = 0
            for i in range(3, self._width):
                dist = ((float)(i - 3.5)) * self._unit

                sx = round(self.x + dx * dist)
                sy = round(self.y + dy * dist)
                sample = scanner.getBW3x3(sx, sy)

                #
                # PSEUDO CODE
                # Look up JAVA components for this
                color = "black" if sample == 0 else "white"
                g.setColor(color)
                rect: Rectangle2d = Rectangle.byFloat(sx - 0.6, sy - 0.6, 1.2, 1.2)
                g.fill(rect)
                g.setColor("red")
                g.setStrike(Basicstroke(0.25))
                g.draw(rect)

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

        circ = Ellipsis2D = Ellipsis2D.fromFloat(x - r, y - r, r * 2, r * 2)
        g.setColor("white")
        g.fill(circ)

        for i in range(self._sectors, -1, -1):
            arc.setArc(x - r, y - r, r * 2, r * 2, i * sweep + sweep, sweep, Arc2D.PIE)
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
