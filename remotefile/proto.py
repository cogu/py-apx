
def readLine(buf, iBegin, iEnd):
    for i in range(iBegin, iEnd):
        if(buf[i] == 10):
            return i
    return iBegin
