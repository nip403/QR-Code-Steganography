# Steganography-QR
Image Steganography using QR-codes encoded with LSB in red pixel channel written in Python 3.7.

Program encodes data in a qrcode first before hiding it in the source image.

# steg.py usage
```
usage: steg.py [-h] [-d DATA] [--image FILE] [--dest FILE]

py steg.py [options]

optional arguments:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  Data to be encoded; can be alphanumeric or URIs

Additional options:
  --image FILE, --img FILE
                        Path to source image
  --dest FILE           Destination directory

ADDENDUM:
    - if no image is provided for the encoding process a default image will be used
    - if no destination directory is provided the original directory for the source image will be used
    - encoded images will be saved as: "[filename]-hidden.[ext]"
    - decoded images will be saved as: "[filename]-revealed.[ext]"
    - program will encode/decode depending on whether data flag is provided
```

# Requirements
- Qrcode (`pip install qrcode[pil]`)
- Pillow (`pip install pillow`)
- Numpy (`pip install numpy`)

# Todo
- improve "engine.py" @ NOTEs
- add functionality to store up to 3 qrcodes/support memory overflow 
- add support for b&w images
- add support for alpha channels
- github pages (transcribe to js)

### Most useless error message of the year award
`"could be decompression bomb DOS attack."`
