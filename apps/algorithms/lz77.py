import os
import re
import numpy as np
from PIL import Image
from io import StringIO


class LZ77:
    def __init__(self, file=None, path=None, searchWindowSize=6, previewWindowSize=7):
        self.path = path
        if file != None:
            # self.file = StringIO(file.getvalue().decode("utf-8"))
            self.file = str(file.read())[2:]

        # if path != None:
        #     self.original_file_size = os.path.getsize(path)
        self.data = None
        self.searchWindowSize = searchWindowSize
        self.previewWindowSize = previewWindowSize

    def longest_common_substring(self, s1, s2):
        maxLongest = 0
        offset = 0
        for i in range(0, len(s1)): 
            longest = 0
            if ((i == len(s1) - len(s2) - 0)):
                break
            for j in range(0, len(s2)):
                if (i+j < len(s1)):
                    if s1[i+j] == s2[j]:
                        longest = longest + 1
                        if (maxLongest < longest):
                            maxLongest = longest
                            offset = i
                    else:
                        break
                else:
                    break
        return maxLongest, offset

    def encode_lz77(self, text, opt=0):
        encodedNumbers = []
        encodedSizes = []
        encodedLetters = []
        encodeStr = ""
        print(text[:30])
        i = 0
        while i < len(text):
            if i < self.previewWindowSize:
                encodedNumbers.append(0)
                encodedSizes.append(0)
                encodedLetters.append(text[i])
                if opt == 0:
                    encodeStr += f'0`0`{text[i]}`'
                else:
                    encodeStr += f'0`0`{int(text[i][0])}`'

                i = i + 1
            else:
                previewString = text[i:i+self.previewWindowSize]
                searchWindowOffset = 0
                if (i < self.searchWindowSize):
                    searchWindowOffset = i
                else:
                    searchWindowOffset = self.searchWindowSize
                searchString = text[i - searchWindowOffset:i]
                result = self.longest_common_substring(searchString + previewString, previewString) # searchString + prevString, prevString
                nextLetter = ''
                if (result[0] == len(previewString)):
                    if (i + result[0] == len(text)):
                        nextLetter = ''
                    else:
                        nextLetter = text[i+self.previewWindowSize]
                else:
                    nextLetter = previewString[result[0]]
                
                if opt == 1:
                    nextLetter = int(nextLetter[0])

                if (result[0] == 0):
                    encodedNumbers.append(0)
                    encodedSizes.append(0)
                    encodedLetters.append(nextLetter)
                    encodeStr += f'0`0`{nextLetter}`'
                else:
                    encodedNumbers.append(searchWindowOffset - result[1])
                    encodedSizes.append(result[0])
                    encodedLetters.append(nextLetter)
                    encodeStr += f'{searchWindowOffset - result[1]}`{result[0]}`{nextLetter}`'
                i = i + result[0] + 1

        return encodeStr

    def decode_lz77(self, encodeStr, opt=0):
        i = 0
        print(encodeStr[:10])
        list_data = encodeStr.split('`')
        print(list_data[-10:])
        decodedString = ""
        if opt == 1:
            decodedString = []
            shape = list_data[-2:]
            list_data = list_data[:-2]
        list_data = list_data[:-1]
        while i < len(list_data)/3:
            character = (list_data[i*3 + 2])
            if opt == 1:
                if character != "":
                    character = int(character)
                
            try:
                a = int(list_data[i*3 + 0])
            except:
                print("_________________________",list_data[i*3 -2:i*3+2],"___________")
            if (int(list_data[i*3 + 0]) == 0):
                if opt == 1:
                    decodedString.append(character)
                else:
                    decodedString += (character)
            else:
                currentSize = len(decodedString)
                for j in range(0, int(list_data[i*3 + 1])):
                    if opt == 1:
                        decodedString.append(decodedString[currentSize-int(list_data[i*3 + 0])+j])
                    else:
                        decodedString += (decodedString[currentSize-int(list_data[i*3 + 0])+j])
                if opt == 1:
                    decodedString.append(character)
                else:
                    decodedString += (character)
            i = i+1

        if opt == 1:
            return decodedString, shape
        
        return decodedString



    def compress(self):
        my_string = np.asarray(Image.open(self.path),np.uint8)
        shape = my_string.shape
        stringToEncode = (my_string.reshape(-1, 1).tolist())
        print(stringToEncode[0][0])
        print(my_string.reshape(1, -1).shape)

        self.shape = my_string.shape
        self.string = my_string
        compressed_data = self.encode_lz77(stringToEncode, opt = 1)
        print("Compressed file generated as compressed.txt")
        filesplit = str(os.path.basename(self.path)).split('.')
        filename = filesplit[0] + '_LZ77Compressed.txt'
        savingDirectory = os.path.join(os.getcwd(),'CompressedFiles')

        # if not os.path.isdir(savingDirectory):
        #     os.makedirs(savingDirectory)
        # with open(os.path.join(savingDirectory,filename),'w+', encoding="utf-8") as file:
        #     file.write(str(compressed_data))

        # self.compressed_file_size = os.path.getsize(os.path.join(savingDirectory,filename))
        return compressed_data+","+str(shape[0])+","+str(shape[1])

        
    def decompress(self):
        data_comp = self.file

        decodedString, shape = self.decode_lz77(data_comp, opt = 1)
        if decodedString[-1] == '':
            decodedString = decodedString[:-1]
        digitImageflaten = np.array(decodedString, dtype=np.uint8)
        print("_____",decodedString[-10:])


        print(shape)
        if len(digitImageflaten) == int(shape[0]) * int(shape[1][:-1]):
            digitImage = digitImageflaten.reshape(int(shape[0]),int(shape[1][:-1]))
        else:
            digitImage = digitImageflaten.reshape(int(shape[0]),int(shape[1][:-1]),3)

        image = Image.fromarray(digitImage.astype(np.uint8))
        # image.save('_LZ77Decompressed.jpg')
        # self.saveImage(image)
        # if self.string.all() == res.all():
        #     print("Success")
        return image


    def saveImage(self, image):
        print("Saving Decompressed File...")
        filesplit = str(os.path.basename(self.path)).split('_LZ77Compressed.txt')
        filename = filesplit[0] + "_LZ77Decompressed.jpg"
        savingDirectory = os.path.join(os.getcwd(),'DecompressedFiles')
        if not os.path.isdir(savingDirectory):
            os.makedirs(savingDirectory)

        image.save(os.path.join(savingDirectory,filename))


