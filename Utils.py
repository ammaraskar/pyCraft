import array

def stringToByteArray(string):
    return array.array('B', string.decode("hex"))

def TwosCompliment(hash):
    hash = array.array('B', hash.decode("hex"))
    carry = True
    for i in range((hash.__len__() - 1), 0, -1):
        if(carry):
            carry = hash[i] == 0xFF
            hash[i] += 1
    return hash

def trimStart(string, character):
    for c in string:
        if (c == character):
            string = string[1:]
        else:
            break
    return string
            