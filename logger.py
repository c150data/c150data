from datetime import datetime

def eprint(description):
    currentTimestamp = datetime.now().time()
    print("[ERROR] {} {}", currentTimestamp, description)


def iprint(description):
    currentTimestamp = datetime.now().time()
    print("[INFO] {} {}", currentTimestamp, description)


def wprint(description):
    currentTimestamp = datetime.now().time()
    print("[WARN] {} {}", currentTimestamp, description)