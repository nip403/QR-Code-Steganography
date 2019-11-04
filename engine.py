import qrcode 
from PIL import Image
import numpy as np
import os.path
import sys

# encodes by least significant bit (x % 2 == 1, white; x % 2 == 0, black)
# currently only supports rgb images

class Encoder:
    default = "default.png"
    _length_data_line = 0

    def __init__(self, img=None):
        self._init_file_info(img)
        self.img = img if img else self.default
        self._init_img()

    @property
    def image(self):
        return self.img

    @image.setter
    def image(self, new):
        self.img = new
        self._init_file_info(self.img)
        self._init_img()

    @image.deleter
    def image(self):
        self.img = self.default

    def _init_file_info(self, img):
        try:
            self._name, self._ext = os.path.splitext(img if img else self.default)
        except:
            raise Exception("Path invalid.")

    def _init_img(self):
        try:
            self.img = Image.open(self.img)
        except:
            raise FileNotFoundError(f"'{self._name+self._ext}' was not found in {sys.path}.\nPlease check if the file exists.")

    def fetch_qr(self, data, show=False):
        try:
            _qr = qrcode.QRCode(
                box_size=1,
                border=1
            )

            _qr.add_data(data)
            _qr.make(fit=True)
            qr = _qr.make_image(fill_color="black", back_color="white")
        
        except Exception as e:
            raise ValueError(e)

        if show:
            qr.show()

        return qr

    def _validate_size(self, qr):
        if any(self.img.size[i] < qr.size[i] for i in range(2)):
            raise ValueError("QR code holds too much data. Input a larger image file or compress the input data.")
        
        return qr

    def _convert_bin(self, n):
        out = ""

        while n:
            out += str(n % 2)
            n //= 2

        return list(map(int, out[::-1]))

    def _encode_pix(self, val, pix):
        if val: # data = 1
            if not (pix[0] % 2): # check if even
                pix[0] += 1
        else: # data = 0
            if pix[0] % 2: # check if odd
                pix[0] -= 1

        return tuple(pix)

    def _encode_dim(self, qr, img_data):
        # top row encodes size of qr code
        # only 1 val needed as qr codes are always square
        top = self._convert_bin(qr.shape[0])
        top = [0]*(img_data.shape[1] - len(top)) + top

        # convert first line into binary which encodes qrcode length
        actual_top = np.reshape(np.array(self.img.crop((0, self._length_data_line, self.img.size[0], self._length_data_line+1))), (img_data.shape[1], 3))

        # encode binary into red channel
        new_top = tuple(self._encode_pix(top[i], actual_top[i]) for i in range(img_data.shape[1]))

        # create new image, overwrite top line with formatted line
        img_top = Image.new(self.img.mode, (self.img.size[0], 1))
        img_top.putdata(new_top)
        self.img.paste(img_top, (0, 0))

    def encode(self, data, show_input=False, show_qr=False, show_result=False):
        if show_input:
            self.img.show()

        qr = np.array(self._validate_size(self.fetch_qr(data, show=show_qr)))
        img_data = np.array(self.img)
        self._encode_dim(qr, img_data)


        ##### NOTE: use image.eval

        # encodes qr code, topleft=(0,0)
        qr_img = np.array(self.img.crop((0, 0, *qr.shape)))
        for y in range(qr_img.shape[0]):
            for x in range(qr_img.shape[1]):
                qr_img[y, x] = self._encode_pix(qr[y, x], qr_img[y, x])
        #qr_img = np.apply_along_axis(self._encode_dim, 2, np.reshape(qr, (list(qr.shape) + [1]), qr_img))
        #qr_img = np.apply_over_axes(self._encode_dim, np.reshape(qr, (list(qr.shape) + [1]), qr_img), [1, 3])

        qr_cover = Image.fromarray(qr_img[1:])
        self.img.paste(qr_cover, (0, 1))
        self.img.save(f"{self._name}-hidden.png")

        if show_result:
            self.img.show()

        return self.img, f"{self._name}-hidden.png"

##### NOTE: np.array % 2 returns everything i needdddddd, replace existing method soon

class Decoder:
    default = "default-hidden.png"

    def _init_file_info(self):
        try:
            self._name, self._ext = os.path.splitext(self.img if self.img else self.default)
        except:
            raise Exception("Path invalid.")

    def _init_img(self):
        try:
            self.img = Image.open(self.img)
        except:
            raise FileNotFoundError(f"'{self._name+self._ext}' was not found in {sys.path}.\nPlease check if the file exists.")
 
    def _decode_pix_to_bin(self, pix):
        return pix[0] % 2

    def _decode_pix(self, pix):
        return (pix[0] % 2) * 255

    def _convert_dec(self, arr):
        b = int("".join(map(str, arr)))
        out = 0
        power = 0

        while b:
            rem = b % 10
            out += 2**power * rem
            b //= 10
            power += 1

        return out

    def decode(self, img=None, show=False):
        # initialisations
        self.img = img
        self._init_file_info()
        self._init_img()

        # scrapes top line of pixels form input, converts to binary from least significant bit to find dimensions of qr code
        qr_dim = self._convert_dec(list(map(self._decode_pix_to_bin, np.reshape(np.array(self.img.crop((0, 0, self.img.size[0], 1))), (self.img.size[0], 3)))))
        ###NOTE: delete above function when below is fixed

        # get qr code, and parse for lsb
        qr_raw = np.insert(np.array(self.img.crop((0, 0, qr_dim, qr_dim)))[1:], 0, np.ones((1, qr_dim, 3)), 0)
        qr_img = np.apply_along_axis(self._decode_pix, 2, qr_raw)
        print(qr_img, qr_img.shape)
        #NOTE: fix this for 1 bit numbers (mode="1")
        qr = Image.fromarray(qr_img.astype("uint8"), mode="L")

        if show:
            qr.show()

        return qr

def test_qr():
    e = Encoder()
    d = Decoder()
    image, filename = e.encode("http://www.google.com")[1]
    qr = d.decode(name, show=True)

if __name__ == "__main__":
    test_qr()
