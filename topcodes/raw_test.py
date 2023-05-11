from scanner import Scanner
import multiprocessing as mp
import os

if __name__ == "__main__":
    mp.set_start_method("spawn")
    file = r"topcodes/test_img/341.png"
    print(os.getcwd())
    myScanner = Scanner()
    tc_list = myScanner.scan_by_filename(file)
    for tc in tc_list:
        print(tc)