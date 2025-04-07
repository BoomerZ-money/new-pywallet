"""
Recovery functions for PyWallet
"""

import os
import re
import time
from pywallet.utils import readpartfile

class RecovCkey(object):
    """Class for recovered encrypted private keys"""
    def __init__(self, epk, pk):
        self.encrypted_pk = epk
        self.public_key = pk
        self.mkey = None
        self.privkey = None

class RecovMkey(object):
    """Class for recovered master keys"""
    def __init__(self, ekey, salt, nditer, ndmethod, nid):
        self.encrypted_key = ekey
        self.salt = salt
        self.iterations = nditer
        self.method = ndmethod
        self.id = nid

def find_patterns(device, size, patternlist):
    """Find patterns in a device or file"""
    tzero = time.time()
    try:
        fd = os.open(device, os.O_RDONLY)
    except Exception as e:
        print(f"Can't open device {device}: {e}")
        return {}

    i = 0
    BlocksToInspect = {}
    
    # Read the device in chunks
    while i < size:
        readsize = min(size - i, 1024 * 1024)
        
        try:
            data = os.read(fd, readsize)
            if len(data) == 0:
                print(f"Reached EOF at {i}")
                break
                
            for pattern in patternlist:
                found_positions = [m.start() for m in re.finditer(pattern, data)]
                
                for pos in found_positions:
                    datakept = data[max(0, pos - 16):min(len(data), pos + len(pattern) + 16)]
                    
                    if pattern not in BlocksToInspect:
                        BlocksToInspect[pattern] = []
                    
                    BlocksToInspect[pattern].append((i + pos, datakept, len(datakept)))
            
            i += len(data)
            
        except Exception as exc:
            lendataloaded = min(size - i, 1024 * 1024)
            os.lseek(fd, lendataloaded, os.SEEK_CUR)
            print(str(exc))
            i += lendataloaded
            continue
            
    os.close(fd)

    # Process found patterns
    AllOffsets = dict(map(lambda x: [repr(x), []], patternlist))
    for text, blocks in BlocksToInspect.items():
        for offset, data, ldk in blocks:  # ldk = len(datakept)
            offsetslist = [offset + m.start() for m in re.finditer(text, data)]
            AllOffsets[repr(text)].extend(offsetslist)

    AllOffsets['PRFdevice'] = device
    AllOffsets['PRFdt'] = time.time() - tzero
    AllOffsets['PRFsize'] = i
    return AllOffsets
