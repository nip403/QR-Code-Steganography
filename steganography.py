from engine import Encoder, Decoder

def main():
    e = Encoder()
    d = Decoder()

    e.encode("this is some text.")
    res = d.decode()

    #res.show()

if __name__ == "__main__":
    main()
