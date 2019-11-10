import qrcode 
from PIL import Image
import numpy as np
import os.path
import sys

# NOTE: add compatibility for other image formats

class Encoder:
    default = "default.png"
    default_dir = "."
    _length_data_line = 0

    def __init__(self, img=None):
        self.img = img if (img is not None and not os.path.isfile(img)) else self.default
        self._init_file_info()
        self._init_img()

    @property
    def image(self):
        return self.img

    @image.setter
    def image(self, new):
        self.img = new
        self._init_file_info()
        self._init_img()

    @image.deleter
    def image(self):
        self.img = self.default

    def _init_file_info(self):
        try:
            self.img = self.default if self.img is None else self.img
            self._name, self._ext = os.path.splitext(self.img)
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
            if not (pix % 2): # check if even
                pix += 1
        else: # data = 0
            if pix % 2: # check if odd
                pix -= 1

        return pix

    def _encode_dim(self, qr, img_data):
        # top row encodes size of qr code
        # only 1 val needed as qr codes are always square
        top = self._convert_bin(qr.shape[0])
        top = np.array([0]*(img_data.shape[1] - len(top)) + top)

        # convert first line into binary which encodes qrcode length
        actual_top = np.reshape(np.array(self.img.crop((0, self._length_data_line, self.img.size[0], self._length_data_line+1))), (img_data.shape[1], 3))

        # encode binary into red channel
        new_top = np.concatenate((np.reshape(np.vectorize(self._encode_pix)(top, actual_top[:, 0]), (len(top), 1)), actual_top[:, 1:]), axis=1)

        # create new image, overwrite top line with formatted line
        img_top = Image.new(self.img.mode, (self.img.size[0], 1))
        img_top.putdata([tuple(i) for i in new_top])
        self.img.paste(img_top, (0, 0))

    def encode(self, data, dest_dir=".", save=None, show_input=False, show_qr=False, show_result=False):
        if show_input:
            self.img.show()

        if not os.path.isdir(dest_dir):
            dest_dir = self.default_dir

        qr = np.array(self._validate_size(self.fetch_qr(data, show=show_qr)))
        img_data = np.array(self.img)
        self._encode_dim(qr, img_data)

        # encodes qr code, topleft=(0,0)
        qr_img = np.array(self.img.crop((0, 0, *qr.shape)))
        qr_cover = Image.fromarray(np.concatenate((np.reshape(np.vectorize(self._encode_pix)(qr, qr_img[:, :, 0]), (*qr.shape, 1)), qr_img[:, :, 1:]), axis=2))

        full = f"{dest_dir}\{self._name if save is None else save}{'-hidden' * bool(save)}{self._ext}"
        self.img.paste(qr_cover, (0, 1))
        self.img.save(full)

        if show_result:
            self.img.show()

        return self.img, full

class Decoder:
    default = "default-hidden.png"
    default_dir = "."
    _min_out_size = 500

    def __init__(self, img=None):
        self.img = img if (img is not None and not os.path.isfile(img)) else self.default
        self._init_file_info()
        self._init_img()

    @property
    def image(self):
        return self.img

    @image.setter
    def image(self, new):
        self.img = new
        self._init_file_info()
        self._init_img()

    @image.deleter
    def image(self):
        self.img = self.default

    def _init_file_info(self):
        try:
            self.img = self.default if self.img is None else self.img
            self._name, self._ext = os.path.splitext(self.img)
        except:
            raise Exception("Path invalid.")

    def _init_img(self):
        try:
            self.img = Image.open(self.img)
        except:
            raise FileNotFoundError(f"'{self._name+self._ext}' was not found in {sys.path}.\nPlease check if the file exists.")

    def decode(self, dest_dir=".", save=None, show=False):
        if not os.path.isdir(dest_dir):
            dest_dir = self.default_dir

        # scrapes top line of pixels form input, converts to binary from least significant bit to find dimensions of qr code
        qr_dim = int("".join((np.array(self.img.crop((0, 0, self.img.size[0], 1)))[:, :, 0][0] % 2).astype(str)), 2)

        # min size of qr = 500 (defined as base attr)
        # if qr_dim > 500, scale_factor will always be 1
        scale_factor = int(np.ceil(self._min_out_size/qr_dim))

        # get qr code, and parse for lsb
        try:
            qr = Image.fromarray((np.insert(np.array(self.img.crop((0, 0, qr_dim, qr_dim)))[1:], 0, np.ones((1, qr_dim, 3)), 0)[:, :, 0] % 2 * 255).astype("uint8"), mode="L")
        except:
            raise ValueError("Unformatted file, retry with encoded file.")

        # NOTE: update to use python 3.8 walrus operator
        # resize to min size (as defined in base attrs)
        if qr.size[0] < 500:
            qr = qr.resize(list(map(lambda i: int(np.ceil(self._min_out_size/i)) * i, qr.size)))

        full = f"{dest_dir}\{self._name if save is None else save}{'-qr' * bool(save)}{self._ext}"
        qr.save(full)

        if show:
            qr.show()

        return qr, full

def test_qr():
    e = Encoder()
    image, filename = e.encode("http://www.google.com")
    d = Decoder(filename)
    qr = d.decode(show=True)[0]

if __name__ == "__main__":
    test_qr()
