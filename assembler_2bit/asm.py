#! /usr/bin/env python3

p =  {
"eax" : "00",
"ebx" : "01",
"acc" : "00",
"sti" : "0010",
"st" : "0011",
"ld" : "0001",
"add" : "0100",
"and" : "0110",
"or" : "1000",
"sub" : "1010",
"nop" : "1100",
"halt" : "1110"
}

def linesplitter(l):
    res = None
    l = l.strip().replace(","," ")
    ll = l.split()
    
    ln = len(ll)
    if ln ==1:
        res = (ln, ll[0])
    elif ln == 3:
        lop = ll[0]
        li0 = ll[1]
        li1 = ll[2]
        res = (ln, (lop, li0, li1))
    else:
        print(f"Error, Invalid asm: {l}")
        exit(1)
   
    return res

def parse_2ins(l):
    rstr = "0b"
    (ln,sp) = linesplitter(l)
    success = True if ln == 3  else False
    if not success:
        return (False, ())

    (lop,li0,li1) = sp
    
    if lop in ["sti"]:
       rstr += f"{p[lop]}{int(li0):02b}{int(li1):02b}"
    elif lop in ["ld", "st"]:
       rstr += f"{p[lop]}{p[li0]}{int(li1):02b}"
    else:
        print("Error: unsupport 2 input instruction: {l}")
        exit(1)

    res = rstr
    return (success, res)

def parse_0ins(l):
    rstr = "0b"
    (ln,sp) = linesplitter(l)
    success = True if ln == 1  else False
    if not success:
        return (False, ())
    lop=sp 
    rstr += f"{p[lop]}0000"

    res = rstr

    return (success,res)

fname = "./asm.txt"
lines = []
with open(fname, "r") as fh:
    lines = fh.readlines()


records = []
addr = 0

# --- Step 1: Parse all lines into byte values ---
for l in lines:
    success, result = parse_2ins(l)
    if not success:
        success, result = parse_0ins(l)
    if not success:
        print(f"your assembly sucks!! -> {l.strip()}")
        continue

    if result is not None:
        byte_val = int(result, 2)   # convert binary "0b...." to integer
        records.append(byte_val)

# --- Step 2: Function to create Intel HEX record lines ---
def make_record(address, data):
    """Create a valid Intel HEX record line."""
    length = len(data)
    record_type = 0  # 00 = data record
    checksum = (-(length + (address >> 8) + (address & 0xFF) + record_type + sum(data))) & 0xFF
    return f":{length:02X}{address:04X}{record_type:02X}{''.join(f'{b:02X}' for b in data)}{checksum:02X}"

# --- Step 3: Write all records into loader.hex ---
outfname = "loader.hex"
with open(outfname, "w") as f:
    # Write data records (16 bytes per line)
    for i in range(0, len(records), 16):
        data_chunk = records[i:i+16]
        rec = make_record(i, data_chunk)
        f.write(rec + "\n")

    # Write EOF record
    f.write(":00000001FF\n")

print(f"Intel HEX written to {outfname}")
