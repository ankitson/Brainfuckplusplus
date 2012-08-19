import sys

#Returns index of matching ] in a string, given the index of the starting [
def matching_right(string,i):
    c = 1
    while c:
        i += 1
        if i >= len(string): raise Exception("No matching ']'")
        if string[i] == ']':   c -= 1
        elif string[i] == '[': c += 1
    return i

#Returns index of matching [ in a string, given the index of the starting ]
def matching_left(string,i):
    c = 1
    while c:
        i -= 1
        if i < 0: raise Exception("No matching '['")
        if string[i] == '[':   c -= 1
        elif string[i] == ']': c += 1
    return i

#Does the instruction at ip, given the current memp
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

    elif cur_instr == '!':
        sync[thread_i] = 0
        ip -= 1

    ip += 1
    return (ip,memp)

#Checks for dirtyness. Horrible function, should probably redo it
def check_dirty(instr,memp):
    global dirty
    is_dirty    = dirty.get(memp,False)
    read_dirty  = dirty.get("read",False)
    write_dirty = dirty.get("write",False)

    #Read from mem to stdout
    if instr == '.':
        if is_dirty:
            raise Exception("Conclict at memp "+str(memp)+" for command: "+instr+"\nTwo threads cannot read/write to the same location at the same time")
        elif read_dirty:
            raise Exception("Reading conclict for command: "+instr+"\nTwo threads cannot write to stdout at the same time")
        else:
            dirty["read"] = True

    #Write from stdin to mem
    elif instr == ',':
        if is_dirty:
            raise Exception("Conclict at memp "+str(memp)+" for command: "+instr+"\nTwo threads cannot read/write to the same location at the same time")
        elif write_dirty:
            raise Exception("Writing conclict for command: "+instr+"\nTwo threads cannot read from stdin at the same time")
        else:
            dirty["write"] = True
            dirty[memp] = True

    #Incrementing a mem location
    elif instr == '+' or instr == '-':
        if is_dirty:
            raise Exception("Conclict at memp "+str(memp)+" for command: "+instr+"\nTwo threads cannot read/write to the same location at the same time")
        else:
            dirty[memp] = True

    #Comparison to 0
    elif instr == '[' or instr == ']':
        if is_dirty:
            raise Exception("Conclict at memp "+str(memp)+" for command: "+instr+"\nTwo threads cannot read/write to the same location at the same time")
        
    return True
    

#Initialize 30000 buckets
mem = [0]*30000

#Initialize dirty command tracker. Each iteration the commands all "threads"
#are about to run are checked if they are going to change a value in mem, if
#one is then that memp is set to True in this dict. If another thread is reading
#or writing that memp then an error is thrown
dirty = {}

threads = []

#Will always be a list of ones, when a thread hits a sync command it will make
#it's thread index in sync be 0 and make its ip not increment. At the end of a tick
#if sync is all 0's then we know that all threads are blocking on sync, we increment
#all their ip's by one and reset sync
sync = []

#Initialize threads metadata
for filename in sys.argv[1:]:
    f = {"ip":0, "memp":0, "f":filename}
    with open(filename) as x: 
        f["instr"] = ''.join(filter(lambda x: x in "><+-.,[]_!", x.read()))
    f["instr_len"] = len(f["instr"])
    threads.append(f)

#Initialize the sync list
sync = [1]*len(threads)

do_loop = True
while do_loop:
    do_loop = False
    
    #Reset dirty before every tick
    dirty = {}

    #Check all dirty commands. check_dirty raises exceptions if something is wrong, so we don't really need to check its output
    for meta in threads:
        if meta["ip"] < meta["instr_len"]:
            do_loop = True
            #print("checking "+meta["instr"][meta["ip"]]+" from "+meta["f"])
            check_dirty(meta["instr"][meta["ip"]],meta["memp"])
        
    #do_instr for each thread. do_instr has side-effects, edits mem
    for thread_i in range(0,len(threads)):
        meta = threads[thread_i]
        if meta["ip"] < meta["instr_len"]:
            #print("running "+meta["instr"][meta["ip"]]+" for "+meta["f"])
            (newip,newmemp) = do_instr(meta["instr"],meta["ip"],meta["memp"],thread_i)
            meta["ip"]   = newip
            meta["memp"] = newmemp

    #Check if threads are blocking on sync, if so unblock them and reset sync
    if not 1 in sync:
        for meta in threads: meta["ip"] += 1
        sync = [1]*len(threads)
