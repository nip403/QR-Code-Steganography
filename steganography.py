from engine import Encoder, Decoder

def main():
    e = Encoder()
    d = Decoder()

    img, name = e.encode("this is some text.")
    d.decode(name, show=True)

if __name__ == "__main__":
    main()
