#!/usr/bin/env python
import requests, base64, hashlib
from functools import reduce
from fastreq import fastreq

REMOTE_PORT = 18080  # 根据实际服务器地址修改

def download_cases(group_id: int, group_size: int):
    return fastreq.get([f"/{group_id}/{i}" for i in range(group_size)], REMOTE_PORT)

def run_group(group_id: int, group_size: int) -> list[list[list[bytes]]]:
    print("Running on group", group_id)
    # 1. download charms
    charms = download_cases(group_id, group_size)

    # 2. divide by price
    charms_by_price = [[] for _ in range(256)]
    for charm in charms:
        charms_by_price[charm[-1]].append(charm)
        
    for price in range(256):
        # 3. filter by checksum
        charms=charms_by_price[price]
        xor_filter = lambda c: reduce(lambda a,b:a^b, c[:-1], 0) == c[-1]
        charms = list(filter(xor_filter, charms))
        # 4. dedup
        dedup_charms = []
        for i, c in enumerate(charms):
            dup = False
            for j in range(i):
                charm_same = lambda ch1,ch2: (
                    len(ch1) == len(ch2) and ch1[-16:] == ch2[-16:] and
                    sum(c1 != c2 for c1, c2 in zip(ch1[:-16], ch2[:-16])) <= 3 
                )
                if charm_same(c[:-1], charms[j][:-1]): # dup
                    dup = True
                    break
            if not dup:
                dedup_charms.append(c)
        charms_by_price[price] = dedup_charms

    # 5. level
    levels = [[[] for _ in range(17)] for _ in range(256)]
    for price in range(256):
        for c in charms_by_price[price]:
            b64 = base64.b64encode(c[:-1]).decode('ascii').replace("=", "") # remove padding
            level = next((n for n in range(1,16) if b64[-1] != b64[-(n+1)]), 16)
            levels[price][level].append(c)
    
    return levels

def main():
    # group meta
    groups = requests.get(f"http://localhost:{REMOTE_PORT}/").json()
    # groups = groups[:1] # uncomment this line to run on one group
    charms_by_group = list(map(lambda t: run_group(t[0],t[1]), enumerate(groups)))
    
    # 6. hash
    concatenated = b''.join(ch[:-1] for g in charms_by_group for l in g for chs in l for ch in chs)
    sha1_hash = hashlib.sha1(concatenated).hexdigest()
    print(sha1_hash)

if __name__ == "__main__":
    main()