from engine import Encoder, Decoder
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Action
import os.path
import sys

#add support fror input of qr codes

def get_parser():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description="IMPORTANT: currently, only png images are supported",
        epilog="""
ADDENDUM: 
    - if no image is provided for the encoding process a default image will be used
    - if no destination directory is provided the original directory for the source image will be used
    - encoded images will be saved as: "[filename]-hidden.[ext]"
    - decoded images will be saved as: "[filename]-revealed.[ext]"
    - program will encode/decode depending on whether data flag is provided
    """)

    parser.add_argument(
        "-d",
        "--data",
        dest="data",
        default=None,
        help="Data to be encoded; can be alphanumeric or URIs"
    )

    general = parser.add_argument_group("Additional options")
    general.add_argument(
        "--image",
        "--img",
        dest="img",
        default="./default.png",
        metavar="FILE",
        help="Path to source image"
    )
    general.add_argument(
        "--dest",
        dest="dest",
        default=".",
        metavar="FILE",
        help="Destination directory"
    )

    return parser

def parse_args(*args):
    parser = get_parser()
    args = parser.parse_args()

    if args.data is None and args.img == "./default.png":
        args.img = None
    
    if args.data is None:
        return 0, args.img, args.dest

    return 1, args.data, args.img, args.dest

def _encode(data, img, dest):
    e = Encoder(img=img)
    return e.encode(data=data, dest_dir=dest)
    
def _decode(img, dest):
    d = Decoder(img=img)
    return d.decode(dest_dir=dest)

if __name__ == "__main__":
    result, *args = parse_args(sys.argv)
    [_decode, _encode][result](*args)[0].show()
    print("SUCCESS")
