ALPHABET = "0123456789ABCDEFGHJKMNPQRSUVWXYZ"
CHARSMAP = {c: i for i, c in enumerate(ALPHABET)}

L = 7      # ID length

P = 65497  # near 2**16
Q = 32803  # near 2**15
N = P * Q
F = (P - 1) * (Q - 1)  # EulerPhi(N)
E = 127                # Coprime with EulerPhi(N)
D = pow(E, -1, F)      # Inverse of E modulo EulerPhi(N)


def encode(n: int) -> str:
    s = [""] * L
    for i in range(L):
        r = n & 31  # mod 32
        n = n >> 5  # div 32
        s[i] = ALPHABET[r]
    return "".join(s)


def decode(s: str) -> int:
    n = 0
    for i, c in enumerate(s):
        d = CHARSMAP[c]
        n += d << (i * 5)
    return n


def encrypt(n: int) -> int:
    return pow(n, E, N)


def decrypt(n: int) -> int:
    return pow(n, D, N)


if __name__ == "__main__":
    for i in range(1, 2**31):
        print(encode(encrypt(i)))
