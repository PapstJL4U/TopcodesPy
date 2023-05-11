"""
Loads and scans images for TopCodes.  The algorithm does a single
sweep of an image (scanning one horizontal line at a time) looking
for a TopCode bullseye patterns.  If the pattern matches and the
black and white regions meet certain ratio constraints, then the
pixel is tested as the center of a candidate TopCode.
 *
author Michael Horn
@version $Revision: 1.4 $, $Date: 2008/02/04 15:02:13 $

python version by PapstJL4U
"""
from typing import no_type_check
from PIL import Image
from itertools import count, islice
from topcode import TopCode
import math as math
import time as T


class Scanner(object):
    # original image
    _image: Image.Image
    # Total width of the image
    _width = 0
    # Total height of the image
    _height = 0
    # Holds process binary pixel data
    _data: list[int] = []
    # Binary view of the image
    _preview: Image.Image
    # reduce processing if done already via check
    _preview_exists = False
    # candidate code count
    _ccount: int = 0
    # number of candidates tested
    _tcount: int = 0
    # maximum width of a topcode unit in pixel
    # very important to find codes
    _maxu: int = 80

    def __init__(self):
        pass

    def scan_by_filename(self, filename: str = "") -> list[TopCode]:
        with Image.open(filename) as im:
            return self.scan_image(im)

    def scan_image(self, image: Image.Image) -> list[TopCode]:
        """Scan the given image and return a list of all topcodes"""
        self._image = image
        # self._preview = None
        self._width = image.width
        self._height = image.height
        LOP = list(image.convert("RGBA").getdata())
        self._data = [0] * len(LOP)

        start: float = T.time()
        for i in islice(count(start=0, step=1), len(LOP)):
            r, g, b, alpha = LOP[i]
            # rgb = 256*256*256 * alpha + 65536 * r + 256 * g + b
            # https://stackoverflow.com/questions/4801366/convert-rgb-values-to-integer
            # the original java algorithm expects alpha + rgb, not rgb + alpha as the byte order
            pixel: int = 0x1000000 * alpha + 0x10000 * r + 0x100 * g + b
            self._data[i] = pixel

        end: float = T.time()
        print("RGBA->ARGB time: " + str(1000 * (end - start)))

        start = T.time()
        self._threshold()
        end = T.time()
        print("threshold time: " + str(1000 * (end - start)))

        """
        # debugging
        with open("tops_adapt_py.int", "w") as f:
            for pixel in self._data:
                f.write(format(pixel, "b") + "\n")
        """
        start = T.time()
        fc = self._findCodes()
        end = T.time()
        print("_findCodes() time: " + str(1000 * (end - start)))

        return fc

    def scan_rgb_data(self, rgb: list[int], width: int, height: int) -> list[TopCode]:
        """untested java -> python image->pillow"""
        raise NotImplementedError
        self._width = width
        self._height = height
        self._data = rgb
        # unsure
        # should be wrong, see above
        self._image = Image.fromarray(rgb, mode="RGBA")

        self._threshold()
        return self._findCodes()

    @property
    def image(self) -> Image.Image:
        """Returns the original, unaltered image"""
        return self._image

    @property
    def imageW(self) -> int:
        """Returns the width of the current image"""
        return self._width

    @property
    def imageH(self) -> int:
        """returns the height of the current image"""
        return self._height

    def setMaxCodeDiameter(self, diameter: int = 0) -> None:
        """
        Sets the maximum allowable diameter (in pixels) for a TopCode
        identified by the scanner.  Setting this to a reasonable value for
        your application will reduce false positives (recognizing codes that
        aren't actually there) and improve performance (because fewer
        candidate codes will be tested).  Setting this value to as low as 50
        or 60 pixels could be advisable for some applications.  However,
        setting the maximum diameter too low will prevent valid codes from
        being recognized.  The default value is 640 pixels.
        """
        f: float = diameter / 8.0
        self._maxu = (int)(math.ceil(f))

    @property
    def ccount(self) -> int:
        """Returns the number of candidate topcodes found during a scan"""
        return self._ccount

    @property
    def tcount(self) -> int:
        """returns the number of topcodes tested during the scan"""
        return self._tcount

    def getBW(self, x: int, y: int) -> int:
        """Binary (threshold black/white) value for pixel (x,y)"""
        pixel = self._data[y * self._width + x]
        return (pixel >> 24) & 0x01

    def getSample3x3(self, x: int, y: int) -> int:
        """
        Average of thresholded pixels in a 3x3 region around (x,y).
        Returned value is between 0 (black) and 255 (white).
        """

        if x < 1 or x > (self._width - 2) or y < 1 or y > (self._height - 2):
            return 0
        pixel: int = 0
        summ: int = 0
        for j in range(y - 1, y + 2, 1):
            for i in range(x - 1, x + 2, 1):
                pixel = self._data[j * self._width + i]
                if (pixel & 0x01000000) > 0:
                    summ += 0xFF

        return summ // 9

    def getBW3x3(self, x: int, y: int) -> int:
        """
        Average of thresholded pixels in a 3x3 region around (x,y).
        Returned value is either 0 (black) or 1 (white).
        """
        if x < 1 or x > (self._width - 2) or y < 1 or y > (self._height - 2):
            return 0

        summ: int = 0
        for j in range(y - 1, y + 2, 1):
            for i in range(x - 1, x + 2, 1):
                pixel: int = self._data[j * self._width + i]
                summ += (pixel >> 24) & 0x01
        if summ >= 5:
            return 1
        else:
            return 0

    def _threshold(self) -> None:
        """
        Perform Wellner adaptive thresholding to produce binary pixel
        data.  Also mark candidate spotcode locations.

        "Adaptive Thresholding for the DigitalDesk"
        EuroPARC Technical Report EPC-93-110
        """
        pixel: int = 0
        r: int = 0
        g: int = 0
        b: int = 0
        a: int = 0
        threshold: int = 128
        summ: int = 128
        s: int = 30
        k: int = 0
        b1: int = 0
        w1: int = 0
        b2: int = 0
        level: int = 0
        dk: int = 0

        self._ccount = 0

        for j in islice(count(start=0, step=1), self._height):
            level, b1, b2, w1 = 0, 0, 0, 0
            """
            Process rows back and forth 
            (alternating left-2-right, right-2-left)
            """
            k = 0 if (j % 2 == 0) else (self._width - 1)
            k += j * self._width

            for _ in islice(count(start=0, step=1), self._width):
                """
                Calculate pixen intensity (0-255)
                """
                pixel = self._data[k]
                r = (pixel >> 16) & 0xFF
                g = (pixel >> 8) & 0xFF
                b = pixel & 0xFF
                a = (r + g + b) // 3

                """
                Calculate sum as an approximate sum 
                of the last s pixels
                """
                summ += a - (summ // s)

                """
                Factor in sum from the previous row
                """
                if k >= self._width:
                    threshold = (summ + (self._data[k - self._width] & 0xFFFFFF)) // (2 * s)
                else:
                    threshold = summ // s
                """
                Compare the average sum to current
                pixel to decide black or white
                """
                f: float = 0.975
                a = 0 if (a < threshold * f) else 1

                """
                Repack pixel data with binary data in 
                the alpha channel, and the running sum
                for this pixel in the rgb channels
                """
                self._data[k] = (a << 24) + (summ & 0xFFFFFF)

                # on a white region, no black pixels
                if level == 0:
                    # first black pixel encountered
                    if a == 0:
                        level = 1
                        b1 = 1
                        w1 = 0
                        b2 = 0
                # on first black region
                elif level == 1:
                    if a == 0:
                        b1 += 1
                    else:
                        level = 2
                        w1 = 1
                # on second white region (bullseye of a code?)
                elif level == 2:
                    if a == 0:
                        level = 3
                        b2 = 1
                    else:
                        w1 += 1
                # on second black region
                elif level == 3:
                    if a == 0:
                        b2 += 1
                    # this could be a top code
                    else:
                        if (
                            b1 >= 2
                            and b2 >= 2
                            and b1 <= self._maxu
                            and b2 <= self._maxu
                            and w1 <= (self._maxu + self._maxu)
                            and abs(b1 + b2 - w1) <= (b1 + b2)
                            and abs(b1 + b2 - w1) <= w1
                            and abs(b1 - b2) <= b1
                            and abs(b1 - b2) <= b2
                        ):
                            mask: int = 0x2000000

                            dk = 1 + b1 + w1 // 2
                            if j % 2 == 0:
                                dk = k - dk
                            else:
                                dk = k + dk

                            self._data[dk - 1] |= mask
                            self._data[dk] |= mask
                            self._data[dk + 1] |= mask
                            self._ccount += 3  # count candidate codes

                        b1 = b2
                        w1 = 1
                        b2 = 0
                        level = 2

                k += 1 if (j % 2 == 0) else -1

    def _findCodes(self) -> list[TopCode]:
        self._tcount = 0
        spots: list[TopCode] = []
        spot: TopCode = TopCode()
        k: int = self._width * 2
        starto = T.time()
        for j in islice(count(start=2, step=1), self._height - 2):
            for i in islice(count(start=0, step=1), self._width):
                if (self._data[k] & 0x2000000) > 0:
                    if (
                        (self._data[k - 1] & 0x2000000) > 0
                        and (self._data[k + 1] & 0x2000000) > 0
                        and (self._data[k - self._width] & 0x2000000) > 0
                        and (self._data[k + self._width] & 0x2000000) > 0
                    ):
                        if not self.overlaps(spots, i, j):
                            self._tcount += 1
                            start = T.time()
                            self.decode(spot, i, j)
                            end = T.time()
                            print("decode time(" + str(self._tcount) + "): " + str(1000 * (end - start)))
                            print("======================================")
                            if spot.isValid:
                                spots.append(spot)
                                spot = TopCode()
                k += 1
        endo = T.time()
        print("findCode Loop time: " + str(1000 * (endo - starto)))
        return spots

    def overlaps(self, spots: list[TopCode], x: int, y: int) -> bool:
        """
        Returns true if point(x,y) is in an exissting TopCode bullseye
        """
        for topcode in spots:
            if topcode.inBullsEye(x, y):
                return True
        return False

    def ydist(self, x: int, y: int, d: int) -> int:
        """
        Counts the number of vertical pixels from (x,y)
        until a color change is perceived
        """
        start: int = self.getBW3x3(x, y)
        for j in count(y + d, d):

            sample: int = self.getBW3x3(x, j)
            if start + sample == 1:
                value = (j - y) if d > 0 else (y - j)
                return value
            if j <= 1 or j > self._height:
                break
        return -1

    def xdist(self, x: int, y: int, d: int) -> int:
        """
        Counts the number of horizontal pixel from (x,y)
        until a color change is perceived
        Return = -1: error

        """
        start: int = self.getBW3x3(x, y)
        for i in count(x + d, d):

            sample: int = self.getBW3x3(i, y)
            if start + sample == 1:
                value = (i - x) if d > 0 else (x - i)
                return value
            if i <= 1 or i > self._width - 1:
                break
        return -1

    def getPreview(self) -> Image.Image:
        """
        For debugging purposes, create a black and white image
        that shows the result of adaptive thresholding
        """
        if self._preview_exists == True:
            return self._preview
        self._preview = Image.new(mode="RGBA", size=(self._width, self._height))
        self._preview_exists = True

        pixel: int = 0
        k: int = 0
        for j in range(self._height):
            for i in range(self._width):
                pixel = self._data[k] >> 24
                if pixel == 0:
                    pixel == 0xFF000000
                elif pixel == 1:
                    pixel == 0xFFFFFFFF
                elif pixel == 3:
                    pixel == 0xFF00FF00
                elif pixel == 7:
                    pixel == 0xFFFF0000

                b: int = pixel & 0xFF
                g: int = (pixel >> 8) & 0xFF
                r: int = (pixel >> 16) & 0xFF
                a: int = (pixel >> 24) & 0xFF

                self._preview.putpixel(xy=(i, j), value=(r, g, b, a))
                k += 1

        return self._preview

    @no_type_check
    def annotate(self, g: object, topcode: TopCode) -> None:
        """drawing method not yet python conform"""

        dx: float = 0.0
        dy: float = 0.0
        dist: float = 0.0
        sx: float = 0.0
        sy: float = 0.0
        bits: int = 0
        for sector in range(topcode.SECTORS - 1, -1, -1):
            dx = math.cos(topcode.ARC * sector + topcode.orientation)
            dy = math.sin(topcode.ARC * sector + topcode.orientation)

            # take 8 samples across the diameter of the symbol

            sample: int = 0
            for i in range(3, topcode._width):
                dist = ((float)(i - 3.5)) * self._unit

                sx = round(topcode.x + dx * dist)
                sy = round(topcode.y + dy * dist)
                sample = self.getBW3x3(sx, sy)

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

    def readUnit(self, topcode: TopCode) -> float:
        """
        Determines the symbol's unit length by counting the number
        of pixels between  the outer edges of the first black ring.
        North, sount, east and west readins are taken and the average is returned
        """
        sx: int = round(topcode.x)
        sy: int = round(topcode.y)
        iwidth: int = self.imageW
        iheight: int = self.imageH

        whiteL: bool = True
        whiteR: bool = True
        whiteU: bool = True
        whiteD: bool = True
        sample: int = 0
        distL: int = 0
        distR: int = 0
        distU: int = 0
        distD: int = 0

        for i in count(start=1):
            if (sx - i < 1) or (sx + i >= iwidth - 1) or (sy - i < 1) or (sy + i >= iheight - 1) or (i > 100):
                return -1

            # Left sample
            sample = self.getBW3x3(sx - i, sy)
            if distL <= 0:
                if whiteL and (sample == 0):
                    whiteL = False
                elif (not whiteL) and (sample == 1):
                    distL = i

            # Right sample
            sample = self.getBW3x3(sx + i, sy)
            if distR <= 0:
                if whiteR and (sample == 0):
                    whiteR = False
                elif (not whiteR) and (sample == 1):
                    distR = i

            # Up sample
            sample = self.getBW3x3(sx, sy - i)
            if distU <= 0:
                if whiteU and (sample == 0):
                    whiteU = False
                elif (not whiteU) and (sample == 1):
                    distU = i

            # Down sample
            sample = self.getBW3x3(sx, sy + i)
            if distD <= 0:
                if whiteD and (sample == 0):
                    whiteD = False
                elif (not whiteD) and (sample == 1):
                    distD = i

            if distR > 0 and distL > 0 and distU > 0 and distD > 0:
                u: float = (distR + distL + distU + distD) / 8.0
                if abs(distR + distL - distU - distD) > u:
                    return -1.0
                else:
                    return u
        return -1.0

    def readCode(self, topcode: TopCode, unit: float, arca: float) -> int:
        """
        Attempts to decode the binary pixels of an image into a code

        topcode - topcode to read
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
        topcode.code = -1

        topcore = topcode.get_core()

        # count down from Sectors down to 0
        for sector in range(topcode.SECTORS - 1, -1, -1):
            dx = math.cos(topcode.ARC * sector + arca)
            dy = math.sin(topcode.ARC * sector + arca)

            # Take 8 samples across the diameter of the symbol
            for i in range(topcode.WIDTH):
                dist = (i - 3.5) * unit
                sx = round(topcode.x + dx * dist)
                sy = round(topcode.y + dy * dist)
                topcore[i] = self.getSample3x3(sx, sy)

            # white rings
            if (topcore[1] <= 128) or (topcore[3] <= 128) or (topcore[4] <= 128) or (topcore[6] <= 128):
                return 0

            # black ring
            if (topcore[2] > 128) or (topcore[5] > 128):
                return 0

            # compute confidence in core sample
            c += topcore[1] + topcore[3] + topcore[4] + topcore[6] + (0xFF - topcore[2]) + (0xFF - topcore[5])

            # data rings
            c += abs(topcore[7] * 2 - 0xFF)

            # opposite data ring
            c += 0xFF - abs(topcore[0] * 2 - 0xFF)

            bit = 1 if topcore[7] > 128 else 0
            bits <<= 1
            bits += bit

        if topcode.checksum(bits):
            topcode.code = bits
            return c
        else:
            return 0

    def decode(self, topcode: TopCode, cx: int, cy: int) -> int:
        
        start = T.time()
        up: int = self.ydist(cx, cy, -1) + self.ydist(cx - 1, cy, -1) + self.ydist(cx + 1, cy, -1)
        down: int = self.ydist(cx, cy, 1) + self.ydist(cx - 1, cy, 1) + self.ydist(cx + 1, cy, 1)
        left: int = self.xdist(cx, cy, -1) + self.xdist(cx, cy - 1, -1) + self.xdist(cx, cy + 1, 1)
        right: int = self.xdist(cx, cy, 1) + self.xdist(cx, cy - 1, 1) + self.xdist(cx, cy + 1, 1)

        end = T.time()
        print("decode(y/xdist) time: " + str(1000 * (end - start)))

        topcode.x = cx
        topcode.x += (right - left) / 6.0
        topcode.y = cy
        topcode.y += (down - up) / 6.0
        start = T.time()
        topcode.unit = self.readUnit(topcode)
        end = T.time()
        print("decode(readunit()) time: " + str(1000 * (end - start)))
        topcode.code = -1
        if topcode.unit < 0:
            return -1

        c: int = 0
        maxc: int = 0
        arca: float = 0
        maxa: float = 0
        maxu: float = 0
        """
        Try different unit and arc adjustments, 
        save the one that produces a maximum confidence reading...
        """
        start = T.time()
        topcode.unit = self.readUnit(topcode)
        for u in range(-2, 3):
            for a in range(10):
                arca = a * topcode.ARC * 0.1
                c = self.readCode(topcode, topcode.unit + (topcode.unit * 0.05 * u), arca)
                if c > maxc:
                    maxc = c
                    maxa = arca
                    maxu = topcode.unit + (topcode.unit * 0.05 * u)
        end = T.time()
        print("decode(readcode()) time: " + str(1000 * (end - start)))
        """
        One last call to readCode to reset orientation and code
        """
        if maxc > 0:
            topcode.unit = maxu
            self.readCode(topcode, topcode.unit, maxa)
            topcode.code = topcode.rotateLowest(topcode.code, maxa)

        return topcode.code
