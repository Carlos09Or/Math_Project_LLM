"""Aritmética y generadores DETERMINISTAS de errores del estudiante (dataset v0.1).

Cada respuesta errónea se produce con una regla conocida, no se adivina. Así, la descripción
del error (`gold_error_observable`) es verdadera por construcción.
La taxonomía de tipos de error es una HIPÓTESIS pendiente de validación docente.
"""

COLS = ['unidades', 'decenas', 'centenas', 'unidades de millar', 'decenas de millar']


def _digits(n, width=None):
    s = str(n).zfill(width) if width else str(n)
    return [int(c) for c in reversed(s)]  # de unidades hacia la izquierda


def _from_digits(ds):
    return int(''.join(str(d) for d in reversed(ds)))


# ---------------------------------------------------------------- respuesta correcta
def solve(op, a, b):
    """Respuesta correcta como estructura. op: 'sub' (a-b), 'mul' (a*b), 'div' (a/b con residuo)."""
    if op == 'sub':
        if a <= b:
            raise ValueError('sub requiere a > b')
        return {'value': a - b}
    if op == 'mul':
        return {'value': a * b}
    if op == 'div':
        q, r = divmod(a, b)
        return {'quotient': q, 'remainder': r}
    raise ValueError('op desconocida: ' + str(op))


def fmt(struct):
    """Texto de la respuesta a partir de su estructura."""
    if 'value' in struct:
        return str(struct['value'])
    return f"cociente {struct['quotient']}, residuo {struct['remainder']}"


# ---------------------------------------------------------------- dificultad (criterios objetivos)
def borrow_count(a, b):
    w = len(str(a))
    borrow, n = 0, 0
    for x, y in zip(_digits(a, w), _digits(b, w)):
        x -= borrow
        if x < y:
            borrow, n = 1, n + 1
        else:
            borrow = 0
    return n


def borrows_through_zero(a, b):
    """True si algún préstamo debe pasar por una columna (no la de unidades) cuya cifra del minuendo es 0."""
    w = len(str(a))
    borrow = 0
    for i, (x, y) in enumerate(zip(_digits(a, w), _digits(b, w))):
        if i > 0 and x == 0 and borrow:
            return True
        x -= borrow
        borrow = 1 if x < y else 0
    return False


def difficulty(op, a, b):
    """1-3 con reglas fijas.
    sub: 3 si hay 3+ préstamos o un préstamo pasa por un cero; 2 si hay 2 préstamos; si no, 1.
    mul: por cifras totales (<=3 -> 1, 4 -> 2, >=5 -> 3). div: divisor de 2 cifras -> 3; dividendo de 3 cifras -> 2; si no, 1."""
    if op == 'sub':
        n = borrow_count(a, b)
        if n >= 3 or borrows_through_zero(a, b):
            return 3
        return 2 if n == 2 else 1
    if op == 'mul':
        total = len(str(a)) + len(str(b))
        return 1 if total <= 3 else (2 if total == 4 else 3)
    if op == 'div':
        if b >= 10:
            return 3
        return 2 if a >= 100 else 1
    raise ValueError(op)


# ---------------------------------------------------------------- errores del estudiante (sustracción)
def sub_col_min_from_max(a, b):
    w = len(str(a))
    da, db = _digits(a, w), _digits(b, w)
    res, det = [], []
    for i, (x, y) in enumerate(zip(da, db)):
        res.append(abs(x - y))
        if x < y:
            det.append(f'{COLS[i]}: |{x}−{y}| = {abs(x - y)}')
    return {'value': _from_digits(res)}, {'columns': det}


def sub_borrow_no_decrement(a, b):
    w = len(str(a))
    da, db = _digits(a, w), _digits(b, w)
    res, cols = [], []
    for i, (x, y) in enumerate(zip(da, db)):
        if x < y:
            x += 10
            cols.append(COLS[i])
        res.append(x - y)  # error: nunca se reduce la cifra de la que se prestó
    return {'value': _from_digits(res)}, {'columns': cols}


def sub_add_instead(a, b):
    return {'value': a + b}, {}


# ---------------------------------------------------------------- errores del estudiante (multiplicación)
def mul_omit_carry(a, b):
    total, carries = 0, []
    for k, d in enumerate(_digits(b)):
        partial = 0
        for i, x in enumerate(_digits(a)):
            p = x * d
            if p >= 10:
                carries.append(f'{x} × {d} = {p}')
            partial += (p % 10) * 10 ** i  # error: se escribe solo la cifra de las unidades
        total += partial * 10 ** k
    return {'value': total}, {'carries': carries}


def mul_forget_shift(a, b):
    if len(str(b)) != 2:
        raise ValueError('mul_forget_shift requiere un multiplicador de 2 cifras')
    p0, p1 = a * (b % 10), a * (b // 10)  # error: p1 no se corre un lugar a la izquierda
    return {'value': p0 + p1}, {'p0': p0, 'p1': p1}


def mul_add_instead(a, b):
    return {'value': a + b}, {}


# ---------------------------------------------------------------- errores del estudiante (división)
def div_stop_early(n, d):
    q, r = divmod(n, d)
    if q < 1:
        raise ValueError('div_stop_early requiere cociente >= 1')
    return {'quotient': q - 1, 'remainder': r + d}, {}


def div_ignore_remainder(n, d):
    q, r = divmod(n, d)
    if r == 0:
        raise ValueError('div_ignore_remainder requiere residuo > 0')
    return {'quotient': q, 'remainder': 0}, {'lost': r}


def div_subtract_instead(n, d):
    return {'value': n - d}, {}


# ---------------------------------------------------------------- observables (texto verificable)
def _obs_sub_col(a, b, t, s, det):
    return (f"{fmt(s)} ≠ {fmt(t)}. Donde la cifra de arriba era menor que la de abajo se restó la cifra menor "
            f"de la mayor, sin pedir prestado ({'; '.join(det['columns'])}).")


def _obs_sub_nodec(a, b, t, s, det):
    return (f"{fmt(s)} ≠ {fmt(t)}. Al pedir prestado ({', '.join(det['columns'])}) no se redujo en 1 "
            f"la cifra de la columna de la que se prestó.")


def _obs_add(verb):
    def f(a, b, t, s, det):
        return f"{fmt(s)} ≠ {fmt(t)}. {fmt(s)} = {a} + {b}: se sumó en lugar de {verb}."
    return f


def _obs_mul_carry(a, b, t, s, det):
    return (f"{fmt(s)} ≠ {fmt(t)}. En cada producto parcial se escribió solo la cifra de las unidades "
            f"y no se sumó lo que se lleva ({'; '.join(det['carries'])}).")


def _obs_mul_shift(a, b, t, s, det):
    return (f"{fmt(s)} ≠ {fmt(t)}. El producto parcial de las decenas no se corrió un lugar a la izquierda: "
            f"{det['p0']} + {det['p1']} = {fmt(s)}.")


def _obs_div_early(n, d, t, s, det):
    return (f"{fmt(s)} ≠ {fmt(t)}. El residuo ({s['remainder']}) es mayor o igual que el divisor ({d}): "
            f"el reparto no ha terminado.")


def _obs_div_ignore(n, d, t, s, det):
    return (f"{fmt(s)} ≠ {fmt(t)}. Se dio residuo 0, pero {s['quotient']} × {d} = {s['quotient'] * d} ≠ {n}: "
            f"sobran {det['lost']} que no se tuvieron en cuenta.")


def _obs_div_sub(n, d, t, s, det):
    return f"{fmt(s)} ≠ {fmt(t)}. {fmt(s)} = {n} − {d}: se restó en lugar de dividir."


# nombre -> (operación, función, texto observable, etiqueta de tipo [HIPÓTESIS])
ERRORS = {
    'sub_col_min_from_max': ('sub', sub_col_min_from_max, _obs_sub_col, 'resta_menor_de_mayor'),
    'sub_borrow_no_decrement': ('sub', sub_borrow_no_decrement, _obs_sub_nodec, 'prestamo_sin_reducir'),
    'sub_add_instead': ('sub', sub_add_instead, _obs_add('restar'), 'suma_en_lugar_de_resta'),
    'mul_omit_carry': ('mul', mul_omit_carry, _obs_mul_carry, 'omision_de_llevada'),
    'mul_forget_shift': ('mul', mul_forget_shift, _obs_mul_shift, 'producto_parcial_sin_desplazar'),
    'mul_add_instead': ('mul', mul_add_instead, _obs_add('multiplicar'), 'suma_en_lugar_de_multiplicacion'),
    'div_stop_early': ('div', div_stop_early, _obs_div_early, 'residuo_mayor_o_igual_que_divisor'),
    'div_ignore_remainder': ('div', div_ignore_remainder, _obs_div_ignore, 'residuo_omitido'),
    'div_subtract_instead': ('div', div_subtract_instead, _obs_div_sub, 'resta_en_lugar_de_division'),
}


def make_error(generator, op, a, b):
    """Devuelve (estructura errónea, texto observable, etiqueta de tipo). Falla si no hay error real."""
    gen_op, fn, obs, label = ERRORS[generator]
    if gen_op != op:
        raise ValueError(f'{generator} no aplica a la operación {op}')
    truth = solve(op, a, b)
    wrong, det = fn(a, b)
    if wrong == truth:
        raise ValueError(f'{generator}({a},{b}) no produce un error: coincide con la respuesta correcta')
    if 'value' in wrong and wrong['value'] <= 0:
        raise ValueError(f'{generator}({a},{b}) produjo una respuesta no positiva')
    return wrong, obs(a, b, truth, wrong, det), label
