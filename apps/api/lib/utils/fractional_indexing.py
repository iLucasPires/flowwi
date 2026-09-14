"""
Fractional Indexing — port fiel da implementação de referência da Rocicorp.

Fonte: https://github.com/rocicorp/fractional-indexing (JavaScript)
Port Python oficial: https://github.com/httpie/fractional-indexing-python
Licença: CC0 1.0 Universal

O algoritmo usa chaves de ordenação compostas por:
  - INTEGER PART: define a magnitude. Começa com um caractere head (a-z para
    comprimentos positivos, A-Z para negativos) seguido de dígitos. O head
    determina quantos dígitos seguem: 'a' = 1 dígito (ex: "a0"), 'b' = 2
    dígitos (ex: "b00"), 'Z' = 1 dígito (ex: "Zz"), 'Y' = 2 dígitos, etc.
  - FRACTION PART: string de dígitos sem trailing zeros, usada para gerar
    midpoints entre dois inteiros iguais.

Invariantes:
  - Todas as chaves geradas satisfazem a < result < b (quando a e b não são None).
  - Comparação lexicográfica simples (< > ==) é suficiente para ordenação.
  - Chaves nunca terminam com o dígito zero (sem trailing zeros na fração).
  - Compatível byte-for-byte com as implementações JS, Go, Kotlin e Ruby.
"""

from decimal import ROUND_HALF_UP, Decimal
from math import floor

BASE_62_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class FractionalIndexingError(Exception):
    pass


def _round_half_up(n: float) -> int:
    return int(Decimal(str(n)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _get_integer_length(head: str) -> int:
    if "a" <= head <= "z":
        return ord(head) - ord("a") + 2

    elif "A" <= head <= "Z":
        return ord("Z") - ord(head) + 2

    raise FractionalIndexingError(f"invalid order key head: {head}")


def _validate_integer(x: str) -> None:
    if len(x) != _get_integer_length(x[0]):
        raise FractionalIndexingError(f"invalid integer part of order key: {x}")


def _get_integer_part(key: str) -> str:
    integer_part_length = _get_integer_length(key[0])

    if integer_part_length > len(key):
        raise FractionalIndexingError(f"invalid order key: {key}")

    return key[:integer_part_length]


def _validate_order_key(key: str, digits: str) -> None:
    zero = digits[0]
    smallest = "A" + (zero * 26)

    if key == smallest:
        raise FractionalIndexingError(f"invalid order key: {key}")

    i = _get_integer_part(key)
    f = key[len(i) :]

    if f and f[-1] == zero:
        raise FractionalIndexingError(f"invalid order key: {key}")


def _increment_integer(x: str, digits: str) -> str | None:
    zero = digits[0]
    _validate_integer(x)
    head = x[0]
    digs = list(x[1:])
    carry = True
    for i in reversed(range(len(digs))):
        d = digits.index(digs[i]) + 1
        if d == len(digits):
            digs[i] = zero
        else:
            digs[i] = digits[d]
            carry = False
            break
    if carry:
        if head == "Z":
            return "a" + zero
        if head == "z":
            return None
        h = chr(ord(head) + 1)
        if h > "a":
            digs.append(zero)
        else:
            digs.pop()
        return h + "".join(digs)
    return head + "".join(digs)


def _decrement_integer(x: str, digits: str) -> str | None:
    _validate_integer(x)
    head = x[0]
    digs = list(x[1:])
    borrow = True
    for i in reversed(range(len(digs))):
        d = digits.index(digs[i]) - 1
        if d == -1:
            digs[i] = digits[-1]
        else:
            digs[i] = digits[d]
            borrow = False
            break
    if borrow:
        if head == "a":
            return "Z" + digits[-1]
        if head == "A":
            return None
        h = chr(ord(head) - 1)
        if h < "Z":
            digs.append(digits[-1])
        else:
            digs.pop()
        return h + "".join(digs)

    return head + "".join(digs)


def _midpoint(a: str, b: str | None, digits: str) -> str:
    """
    Gera string entre a e b.
    - `a` pode ser string vazia, `b` é None ou string não-vazia.
    - `a < b` lexicograficamente se `b` não é None.
    - Sem trailing zeros permitidos.
    """
    zero = digits[0]
    if b is not None and a >= b:
        raise FractionalIndexingError(f"{a} >= {b}")
    if (a and a[-1] == zero) or (b is not None and b[-1] == zero):
        raise FractionalIndexingError("trailing zero")
    if b:
        # Remove longest common prefix. Pad `a` com zeros conforme avançamos.
        n = 0
        for x, y in zip(a.ljust(len(b), zero), b):
            if x == y:
                n += 1
            else:
                break
        if n > 0:
            return b[:n] + _midpoint(a[n:], b[n:], digits)
    # First digits (or lack of) are different
    digit_a = digits.index(a[0]) if a else 0
    digit_b = digits.index(b[0]) if b is not None else len(digits)

    if digit_b - digit_a > 1:
        mid_digit = _round_half_up(0.5 * (digit_a + digit_b))
        return digits[mid_digit]
    # First digits are consecutive
    if b is not None and len(b) > 1:
        return b[:1]
    # `b` is None or single digit
    return digits[digit_a] + _midpoint(a[1:], None, digits)


def generate_key_between(
    a: str | None,
    b: str | None,
    digits: str = BASE_62_DIGITS,
) -> str:
    """
    Gera uma chave de ordenação entre `a` e `b`.

    - a=None, b=None → primeira chave ("a0")
    - a=chave, b=None → chave após a
    - a=None, b=chave → chave antes de b
    - a=chave, b=chave → chave entre a e b
    """
    zero = digits[0]

    if a is not None:
        _validate_order_key(a, digits)

    if b is not None:
        _validate_order_key(b, digits)

    if a is not None and b is not None and a >= b:
        raise FractionalIndexingError(f"{a} >= {b}")

    if a is None:
        if b is None:
            return "a" + zero

        ib = _get_integer_part(b)
        fb = b[len(ib) :]

        if ib == "A" + (zero * 26):
            return ib + _midpoint("", fb, digits)

        if ib < b:
            return ib

        res = _decrement_integer(ib, digits)

        if res is None:
            raise FractionalIndexingError("cannot decrement any more")

        return res

    if b is None:
        ia = _get_integer_part(a)
        fa = a[len(ia) :]
        i = _increment_integer(ia, digits)
        return ia + _midpoint(fa, None, digits) if i is None else i

    ia = _get_integer_part(a)
    fa = a[len(ia) :]
    ib = _get_integer_part(b)
    fb = b[len(ib) :]

    if ia == ib:
        return ia + _midpoint(fa, fb, digits)

    i = _increment_integer(ia, digits)

    if i is None:
        raise FractionalIndexingError("cannot increment any more")

    if i < b:
        return i

    return ia + _midpoint(fa, None, digits)


def generate_n_keys_between(
    a: str | None,
    b: str | None,
    n: int,
    digits: str = BASE_62_DIGITS,
) -> list[str]:
    """
    Gera n chaves distintas e ordenadas entre a e b.
    Distribui as chaves de forma uniforme para minimizar o comprimento.
    """
    if n == 0:
        return []
    if n == 1:
        return [generate_key_between(a, b, digits)]

    if b is None:
        c = generate_key_between(a, b, digits)
        result = [c]

        for _ in range(n - 1):
            c = generate_key_between(c, b, digits)
            result.append(c)

        return result

    if a is None:
        c = generate_key_between(a, b, digits)
        result = [c]

        for _ in range(n - 1):
            c = generate_key_between(a, c, digits)
            result.append(c)

        return list(reversed(result))

    mid = floor(n / 2)
    c = generate_key_between(a, b, digits)

    return [
        *generate_n_keys_between(a, c, mid, digits),
        c,
        *generate_n_keys_between(c, b, n - mid - 1, digits),
    ]


def validate_order_key(key: str, digits: str = BASE_62_DIGITS) -> None:
    """Valida uma chave de ordenação. Levanta FractionalIndexingError se inválida."""
    _validate_order_key(key, digits)
