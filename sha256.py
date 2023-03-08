import textwrap
import copy

#Not clean.

true = True
false = False

def hex8(number):
    return number & 0xffffffff

def hextobinary(hexdata):
    scale = 16 ## equals to hexadecimal
    num_of_bits = 8
    return bin(int(hexdata, scale))[2:].zfill(num_of_bits)

def stringtobinary(st):
    return ' '.join(format(ord(x), 'b').zfill(8) for x in st)

def rotr(x, n): #Stealing code mwhahaha
    return hex8((x >> n) | (x << (32 - n)))
    
def shr(x,n):
    return hex8(x>>n)

class Sha256():
    def __init__(self, s_input): #Types are way off: self.constants: string of hex, self.words: integers, self.working_vars: string of hex
        with open("constants.txt", 'r') as f:
            self.constants = [x.strip() for x in f.readlines()]
        self.s_input = s_input
        self.b_input = stringtobinary(s_input).split()
        padding = (448 - len(self.b_input)*8)//8
        self.b_input.append("10000000")
        for i in range(padding-1):
            self.b_input.append("00000000")
        self.b_input.extend(textwrap.wrap(bin(len(self.s_input)*8)[2:].zfill(64),8))
        self.words = [self.b_input[i:i+4] for i in range(0, len(self.b_input), 4)] #hex()[2:].zfill(8)
        self.words = [int(self.words[i][0]+self.words[i][1]+self.words[i][2]+self.words[i][3],2) for i in range(len(self.words))]
        with open("init.txt", 'r') as f:
            readlines = f.readlines()
            self.working_vars_old = [x.strip() for x in readlines]
            self.working_vars = [x.strip() for x in readlines]
            self.working_vars_new = ["" for _ in range(8)]
        
    def mod_add(self, i1, i2):
        return (i1 + i2) % 4294967296
        
    def mod_add_list(self, i_list):
        curr = self.mod_add(i_list[0],i_list[1])
        for i in range(2, len(i_list)):
            curr = self.mod_add(curr,i_list[i])
        return curr
    
    def sigma_0(self, bin_i):
        return rotr(int(bin_i),7) ^ rotr(int(bin_i),18) ^ shr(int(bin_i),3)
        
    def sigma_1(self, bin_i):
        return rotr(int(bin_i),17) ^ rotr(int(bin_i),19) ^ shr(int(bin_i),10)
        
    def maj(self, i1, i2, i3):
        return (int(i1,16) & int(i2,16)) ^ (int(i1,16) & int(i3,16)) ^ (int(i2,16) & int(i3,16))
        
    def csigma_0(self, hex_i):
        int_i = int(hex_i,16)
        return rotr(int_i,2) ^ rotr(int_i,13) ^ rotr(int_i,22)
    
    def csigma_1(self, hex_i):
        int_i = int(hex_i,16)
        return rotr(int_i,6) ^ rotr(int_i,11) ^ rotr(int_i,25)
        
    def ch(self, i1, i2, i3):
        return (int(i1,16) & int(i2,16)) ^ ((~int(i1,16) & int(i3,16)))
    
    def newWord(self, pos):
        return self.mod_add_list([self.sigma_1(self.words[pos-2]), self.words[pos-7], self.sigma_0(self.words[pos-15]), self.words[pos-16]])
        
    def makeNewWords(self):
        for i in range(16,64):
            self.words.append(self.newWord(i))
            
    def run_iteration(self, itera):
        curr_vars = self.working_vars
        cs_0 = self.csigma_0(curr_vars[0])
        #print(hex(cs_0)) #Is right
        maj = self.maj(curr_vars[0],curr_vars[1],curr_vars[2])
        #print(hex(maj)) #Is right
        cs_1 = self.csigma_1(curr_vars[4])
        ch = self.ch(curr_vars[4],curr_vars[5],curr_vars[6])
        right_var = self.mod_add_list([int(curr_vars[7],16),ch,cs_1,self.words[itera],int(self.constants[itera],16)])
        for i in range(1,8):
            if i != 4:
                self.working_vars_new[i] = curr_vars[i-1]
        #print(hex(right_var))
        #print(hex(self.mod_add(cs_0,maj)))
        self.working_vars_new[4] = hex(self.mod_add(int(curr_vars[3],16),right_var))[2:]
        #self.working_vars_new[0] = hex(self.mod_add_list([cs_0,maj,int(self.working_vars_new[4],16)]))[2:] #Is wrong?????
        self.working_vars_new[0] = hex(self.mod_add_list([cs_0,maj,right_var]))[2:]
        
        
    
    def run(self):
        self.makeNewWords()
        #print(self.words)
        for i in range(64):
            self.run_iteration(i)
            self.working_vars = copy.copy(self.working_vars_new)
            #print(self.working_vars[0],self.working_vars[4])
        for i in range(8):
            self.working_vars[i] = hex(self.mod_add(int(self.working_vars[i],16),int(self.working_vars_old[i],16)))[2:]
        answer = "".join(self.working_vars)
        print(answer)
        return answer
        
    def runsdf(self): #Working on larger inputs, do run, and change above to run block
        len(self.b_input)
    
#hash_input = "hashing is complicated"
hash_input = "password"
with open("binary.txt",'r') as f:
    input_binary_test = f.readline().strip().split()
hash_output = "7a3f5294571e4cb47de29855d1339fdfaa891eb01fb2ddea5e2c8740e09a686d" #This is what it should be


sha256 = Sha256(hash_input)
answer = sha256.run()
print(hash_output.strip() == answer.strip())


