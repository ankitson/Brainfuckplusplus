import sys

def matching_right(string,i):
    c = 1
    while c:
        i += 1
        if i >= len(string): raise Exception("No matching ']'")
        if string[i] == ']':   c -= 1
        elif string[i] == '[': c += 1
    return i

def matching_left(string,i):
    c = 1
    while c:
        i -= 1
        if i >= len(string): raise Exception("No matching '['")
        if string[i] == '[':   c -= 1
        elif string[i] == ']': c += 1
    return i

def do_instr(instrs, ip, memp, thread_i):
    global mem
    global sync
    cur_instr = instrs[ip]

    if cur_instr == '>':
        memp += 1

    elif cur_instr == '<':
        memp -= 1

    elif cur_instr == '+':
        mem[memp] += 1

    elif cur_instr == '-':
        mem[memp] -= 1

    elif cur_instr == '.':
        sys.stdout.write(chr(mem[memp]))

    elif cur_instr == ',':
        mem[memp] = ord(sys.stdin.read(1))

    elif cur_instr == '[' and mem[memp] == 0:
        ip = matching_right(instrs,ip)

    elif cur_instr == ']' and mem[memp] != 0:
        ip = matching_left(instrs,ip)

    elif cur_instr == '_':
        pass

    ip += 1
    return (ip,memp)

def check_dirty(instr,memp):
    global dirty
    is_dirty = dirty.get(memp,False)
    read_dirty = dirty.get("read",False)
    if instr == ',':
        if is_dirty:
            raise Exception("Conclict at memp "+str(memp)+" for command: "+instr+"\nCannot read from a memory location that is also being written to")
        elif read_dirty:
            raise Exception("Reading conclict for command: "+instr+"\nTwo threads cannot read from stdin at the same time")
        else:
            dirty["read"] = True
    elif instr == '.' or instr == '+' or instr == '-':
        if is_dirty:
            raise Exception("Conclict at memp "+str(memp)+" for command: "+instr+"\nTwo threads cannot write to the same location at the same time")
        else:
            dirty[memp] = True

    return True
    

#Initialize 30000 buckets
mem = [0]*30000

#Initialize dirty command tracker. Each iteration the commands all "threads"
#are about to run are checked if they are going to change a value in mem, if
#one is then that memp is set to True in this dict. If another thread is reading
#or writing that memp then an error is thrown
dirty = {}
threads = []

for filename in sys.argv[1:]:
    f = {"ip":0, "memp":0, "f":filename}
    with open(filename) as x: 
        f["instr"] = ''.join(filter(lambda x: x in "><+-.,[]_!", x.read()))
    f["instr_len"] = len(f["instr"])
    threads.append(f)

do_loop = True
while do_loop:
    do_loop = False
    dirty = {}
    for meta in threads:
        if meta["ip"] < meta["instr_len"]:
            do_loop = True
            #print("checking "+meta["instr"][meta["ip"]]+" from "+meta["f"])
            check_dirty(meta["instr"][meta["ip"]],meta["memp"])
        
    for thread_i in range(0,len(threads)):
        meta = threads[thread_i]
        if meta["ip"] < meta["instr_len"]:
            #print("running "+meta["instr"][meta["ip"]]+" for "+meta["f"])
            (newip,newmemp) = do_instr(meta["instr"],meta["ip"],meta["memp"],thread_i)
            meta["ip"]   = newip
            meta["memp"] = newmemp
