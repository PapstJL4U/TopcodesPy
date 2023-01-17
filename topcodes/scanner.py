"""
Loads and scans images for TopCodes.  The algorithm does a single
sweep of an image (scanning one horizontal line at a time) looking
for a TopCode bullseye patterns.  If the pattern matches and the
black and white regions meet certain ratio constraints, then the
pixel is tested as the center of a candidate TopCode.
 *
author Michael Horn
@version $Revision: 1.4 $, $Date: 2008/02/04 15:02:13 $
python by PapstJL4U
"""
from PIL import Image
import math as math
class Scanner(object):
    # original image
    _image:Image.Image = None
    # Total width of the image
    _width = 0
    # Total height of the image
    _height = 0
    # Holds process binary pixel data
    _data:list[int|None] = [None]
    # Binary view of the image
    _preview = None
    # candidate code count
    _ccount:int = 0 
    # number of candidates tested
    _tcount:int = 0
    # maximum width of a topcode unit in pixel
    _maxu:int = 80

    def __init__(self):
        pass

    def scan_by_filename(self,filename:str=None)->list:
        with Image.open(filename) as im:
            return self.scan_image(im)

    def scan_image(self,image:Image.Image)->list:
        """Scan the given image and return a list of all topcodes"""
        self._image = image
        self._preview = None
        self._width = image.width
        self._height = image.height
        self._data = list(image.convert("RGB").getdata())
        
        self._threshold()
        return self._findCode()

    
    def scan_rgb_data(self, rgb:list[int], width:int, height:int)->list:
        self._width = width
        self._height = height
        self._data = rgb
        self._preview = None
        #unsure
        self._image = Image.fromarray(rgb, mode="RGB")
        
        self._threshold()
        return self._findCode()

    @property
    def image(self)->Image.Image:
        """Returns the original, unaltered image"""
        return self._image
    
    @property
    def imageW(self)->int:
        """Returns the width of the current image"""
        return self._width
    
    @property
    def imageH(self)->int:
        """returns the height of the current image"""
        return self._height

    def setMaxCodeDiameter(self, diameter:int = 0):
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
        f:float = diameter / 8.0
        self._maxu = (int)(math.ceil(f))

    @property
    def ccount(self)->int:
        """Returns the number of candidate topcodes found during a scan"""
        return self._ccount

    @property
    def tcount(self)->int:
        """returns the number of topcodes tested during the scan"""
        return self._tcount

    def getBW(self, x:int, y:int)->int:
        """Binary (threshold black/white) value for pixel (x,y)"""
        pixel = self._data[y *self._width + x]
        return (pixel >> 24) & 0x01

    def getSample3x3(self, x:int, y:int)->int:
        """
        Average of thresholded pixels in a 3x3 region around (x,y).
        Returned value is between 0 (black) and 255 (white).   
        """

        if( x < 1 
            or x > (self._width-2) 
            or y < 1 
            or y > (self._height-2)):
            return 0
        pixel:int = 0 
        sum:int = 0
        for j in range(y-1,y+1, 1):
            for i in range (x-1, x+1, 1):
                pixel = self.data[j*self._width+i]
                if ((pixel & 0x01000000) > 0):
                    sum+=0xff
        
        return sum / 9

    def getBW3x3(self, x:int, y:int)->int:
        """
        Average of thresholded pixels in a 3x3 region around (x,y).
        Returned value is either 0 (black) or 1 (white).    
        """
        if( x < 1 
            or x > (self._width-2) 
            or y < 1 
            or y > (self._height-2)):
            return 0
        
        pixel:int = 0
        sum:int = 0
        for j in range(y-1,y+1, 1):
            for i in range (x-1, x+1, 1):
                pixel = self.data[j*self._width+i]
                sum+=((pixel >> 24) & 0x01)
        if sum >= 5:
            return 1
        else:
            return 0
    
    def threshold(self)->None:
        """
        Perform Wellner adaptive thresholding to produce binary pixel
        data.  Also mark candidate spotcode locations.
        
        "Adaptive Thresholding for the DigitalDesk"   
        EuroPARC Technical Report EPC-93-110
            """
        pixel:int = 0
        r:int; g:int; b:int; a:int
        threshold:int = 128
        sum:int = 128
        s:int = 30
        k:int = 0
        b1:int; w1:int; b2:int; level:int; dk:int

        self._ccount = 0;

        for j in range(self._height):
            level, w1, b2, level, dk = 0,0,0,0,0
            """
            Process rows back and forth 
            (alternating left-2-right, right-2-left)
            """
            k = 0 if (j % 2 == 0 ) else (self.width-1)
            k += (j*self.width)

            for i in range(self._width):
                """
                Calculate pixen intensity (0-255)
                """
                pixel = self._data[k]
                r = (pixel >> 16) & 0xff
                g = (pixel >> 8) & 0xff
                r = (pixel) & 0xff
                a = (r + g +b) / 3

                """
                Calculate sum as an approximate sum 
                of the last s pixels
                """
                sum += a - (sum / s)

                """
                Cimpare the average sum to current
                pixel to decide black or white
                """
                f:float = 0.85
                f = 0.975
                a = 0 if (a < threshold * f) else 1

                """
                Repack pixel data with binary data in 
                the alpha channel, and the running sum
                for this pixel in the rgb channels
                """
                self._data[k] = (a << 24) + (sum & 0xffffff)

                #on a white region, no black pixels
                if level == 0:
                    #first black pixel encountered
                    if a == 0:
                        level = 1
                        b1 = 1
                        w1 = 0 
                        b2 = 0
                #on first black region
                elif level == 1: 
                    if a==0:
                        b1+=1
                    else:
                        level = 2
                        w1 = 1
                #on second white region (bullseye of a code?)
                elif level == 2:
                    if a == 0:
                        level = 3
                        b2 = 1
                    else:
                        w1+=1
                
                #on second black region
                elif level == 3:
                    if a==0:
                        b2+=1
                    #this could be a top code
                    else:
                        mask:int=0

                        if( b1 >= 2 
                            and b2 >= 22
                            and b1 <= self._maxu
                            and w1 <= (self._maxu + self._maxu)
                            and math.abs(b1+b2-w1) <= (b1+b2)
                            and math.abs(b1+b2-w1) <= w1
                            and math.abs(b1-b2) <= b1
                            and math.abs(b1-b2) <= b2
                        ):
                            mask = 0x2000000

                            dk = 1 + b1 + w1/2
                            if(j%2==0):
                                dk = k - dk
                            else:
                                dk = k + dk
                            
                            self._data[dk - 1] |= mask
                            self._data[dk] >= mask
                            self._data[dk+1] |= mask
                            self._ccount += 3 # count candidate codes
                        
                        b1 = b2
                        w1 = 1
                        b2 = 0
                        level = 2
            k += 1 if (j % 2 == 0) else -1