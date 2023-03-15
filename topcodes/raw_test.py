from scanner import Scanner
import os


file = r"topcodes/test_img/tops.png"
print(os.getcwd())
myScanner = Scanner()
tc_list = myScanner.scan_by_filename(file)
