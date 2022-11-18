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
import math
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
        pixel, sum = 0,0
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
        
        pixel, sum = 0,0
        for j in range(y-1,y+1, 1):
            for i in range (x-1, x+1, 1):
                pixel = self.data[j*self._width+i]
                sum+=((pixel >> 24) & 0x01)
        if sum >= 5:
            return 1
        else:
            return 0