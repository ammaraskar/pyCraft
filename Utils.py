import array

def stringToByteArray(string):
    return array.array('B', string.decode("hex"))

def TwosCompliment(digest):
    carry = True
    for i in range((digest.__len__() - 1), -1, -1):
        value = 255 - digest[i]
        digest[i] = value
        if(carry):
            carry = digest[i] == 0xFF
            digest[i] = digest[i] + 1
    return digest

def trimStart(string, character):
    for c in string:
        if (c == character):
            string = string[1:]
        else:
            break
    return string

def getHexString(byteArray):
    result = ""
    for i in range(byteArray.__len__()):
        if (byteArray[i] < 0x10):
            result += '0'
        result += hex(byteArray[i])[2:]
    return result
        