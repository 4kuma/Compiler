from string import Template
import sys

command_counter = 0
output_list = []
counter = 30
variables = {}
arrays = {}
to_machine = []
output = ""
Generated_Number = 11
Variable_Index = 12
Left_Value = 13
Right_Value = 14
Condition_Value = 15
Index = 21
Size = 22
Start = 23
Place = 24
Pos = 2
Neg = 3
Lef = 4
Rig = 5
Third = 6
Fourth = 7
Fifth = 8


def add_to_output(string):
    global output
    output = output + string
    global output_list
    global command_counter
    ou = string.splitlines()
    for o in ou:
        output_list.append(o)
        command_counter = command_counter + 1


def add_to_variables(key):
    global variables
    global counter
    if key in variables:
        print("{} already declared".format(key))
        sys.exit()
    else:
        variables[key] = counter
        counter += 1


def negate_number() -> str:
    return 'STORE 1' + '\n' + 'SUB 0\nSUB 1' + '\n'


def generate_number(x: int, destination_register) -> str:
    one_register: int = 1
    result: str = f'SUB 0' + '\n' + f'INC' + '\n' + f'STORE {one_register}' + '\n' + 'DEC' + '\n'

    is_negative = x < 0
    x = abs(x)

    for digit in bin(x)[2:-1]:
        if digit == '1':
            result = result + 'INC\n' + f'SHIFT {one_register}' + '\n'
        elif digit == '0':
            result = result + f'SHIFT {one_register}' + '\n'
    if bin(x)[-1] == '1':
        result = result + f'INC' + '\n'

    if is_negative:
        result = result + negate_number()

    if destination_register != 0:
        result = result + f'STORE {destination_register}' + '\n'

    return result


def assign_value_to_cell(index, value):
    result: str = f'LOAD {value}' + '\n' + f'STOREI {index}' + '\n'
    return result


def move_to_cell(start, destination):
    result: str = f'LOAD {start}' + '\n' + f'STORE {destination}' + '\n'
    return result


def pidentifier_expression_case(arr, ind, dest):
    curr_arr = arr
    result: str = generate_number(curr_arr.index, Index) + generate_number(curr_arr.size, Size) + generate_number(
        curr_arr.start, Start) + f'LOAD {ind}' + '\n' + f'STORE {Place}' + '\n' + f'LOAD {Index}' + '\n' + f'ADD ' \
                                                                                                           f'{Place}' \
                  + '\n' + f'SUB {Start}' + '\n' + 'LOADI 0\n' + f'STORE {dest}' + '\n'

    return result


def pidentifier_assignment_case(arr, ind):
    curr_arr = arr
    result: str = generate_number(curr_arr.index, Index) + generate_number(curr_arr.size, Size) + generate_number(
        curr_arr.start, Start) + f'LOAD {ind}' + '\n' + f'STORE {Place}' + '\n' + f'LOAD {Index}' + '\n' + f'ADD ' \
                                                                                                           f'{Place}' \
                  + '\n' + f'SUB {Start}' + '\n' + f'STORE {Variable_Index}' + '\n'
    return result


class ArrayInfo:
    def __init__(self, index, size, start):
        self.index = index
        self.size = size
        self.start = start


class Number:
    def __init__(self, value):
        self.value = value

    def eval(self):
        add_to_output(generate_number(int(self.value), Generated_Number))
        return int(self.value)

    def generate_left_value(self):
        add_to_output(generate_number(int(self.value), Left_Value))

    def generate_right_value(self):
        add_to_output(generate_number(int(self.value), Right_Value))


class IdValue:
    def __init__(self, value):
        self.value = value

    def generate_left_value(self):
        self.value.generate_left_value()

    def generate_right_value(self):
        self.value.generate_right_value()

    def generate_to_assign(self):
        self.value.generate_to_assign()


class Declaration:
    def __init__(self, variable, lineno):
        if variable in variables:
            print(f"Błąd w linii {lineno}: druga deklaracja zmiennej {variable}")
            sys.exit()
        self.variable = variable
        add_to_variables(variable)


class DeclarationArray:
    def __init__(self, variable, start, end, lineno):
        global arrays
        if int(end) - int(start) < 0:
            print(f"Błąd w linii {lineno}: niewlasciwy zakres tablicy {variable}")
            sys.exit()
        if variable in arrays:
            print(f"Błąd w linii {lineno}: druga deklaracja zmiennej tablicowej {variable}")
            sys.exit()
        self.variable = variable
        string = '{}({}:{})'.format(variable, start, end)
        global counter
        arrays[variable] = ArrayInfo(counter, int(end) - int(start), int(start))
        counter += int(end) - int(start) + 1


class Identifier:
    def __init__(self, id):
        self.id = id

    def eval(self):
        return self.id.eval()


class Pidentifier:
    def __init__(self, id, lineno):
        self.id = id
        self.lineno = lineno

    def eval(self):
        if self.id in variables:
            generate_number(variables[self.id], Variable_Index)
        else:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id}")
            sys.exit()

    def getValue(self):
        if self.id not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id}")
            sys.exit()
        return self.id

    def generate_left_value(self):
        if self.id not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id}")
            sys.exit()
        add_to_output(move_to_cell(variables[self.id], Left_Value))

    def generate_right_value(self):
        if self.id not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id}")
            sys.exit()
        add_to_output(move_to_cell(variables[self.id], Right_Value))

    def generate_to_assign(self):
        if self.id not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id}")
            sys.exit()
        add_to_output(generate_number(variables[self.id], Variable_Index))


class PidentifierArrayID:
    def __init__(self, id1, id2, lineno):
        self.id = id1 + id2
        self.id1 = id1
        self.id2 = id2
        self.lineno = lineno

    def eval(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        if self.id2 not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id2}")
            sys.exit()
        index = variables[self.id2]

    def getValue(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        if self.id2 not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id2}")
            sys.exit()
        return self.id

    def generate_left_value(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        if self.id2 not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id2}")
            sys.exit()
        add_to_output(pidentifier_expression_case(arrays[self.id1], variables[self.id2], Left_Value))

    def generate_right_value(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        if self.id2 not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id2}")
            sys.exit()
        add_to_output(pidentifier_expression_case(arrays[self.id1], variables[self.id2], Right_Value))

    def generate_to_assign(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        if self.id2 not in variables:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna {self.id2}")
            sys.exit()
        add_to_output(pidentifier_assignment_case(arrays[self.id1], variables[self.id2]))


class PidentifierArrayNumber:
    def __init__(self, id1, id2, lineno):
        self.id = id1 + id2
        self.id1 = id1
        self.id2 = id2
        self.lineno = lineno

    def eval(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        generate_number(variables[self.id], Variable_Index)

    def getValue(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        return self.id

    def generate_left_value(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        ind = arrays[self.id1].index + (int(self.id2) - arrays[self.id1].start)
        add_to_output(move_to_cell(ind, Left_Value))

    def generate_right_value(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        ind = arrays[self.id1].index + (int(self.id2) - arrays[self.id1].start)
        add_to_output(move_to_cell(ind, Right_Value))

    def generate_to_assign(self):
        if self.id1 not in arrays:
            print(f"Błąd w linii {self.lineno}: niezadeklarowana zmienna tablicowa {self.id1}")
            sys.exit()
        ind = arrays[self.id1].index + (int(self.id2) - arrays[self.id1].start)
        add_to_output(generate_number(ind, Variable_Index))


class Expression:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Condition:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Sum(Expression):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'ADD {Right_Value}' + '\n' + f'STORE {Generated_Number}'
        add_to_output(result)


class Sub(Expression):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Generated_Number}'
        add_to_output(result)


class Mul(Expression):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        add_to_output(generate_number(-1, Neg))
        add_to_output(generate_number(1, Pos))
        global output_list
        output_list.append('SUB 0' + '\n')
        output_list.append(f'STORE {Generated_Number}' + '\n')
        output_list.append(f'LOAD {Right_Value}' + '\n')
        x = len(output_list)
        output_list.append(f'JZERO {x+23}' + '\n')
        output_list.append(f'STORE {Rig}' + '\n')
        output_list.append(f'LOAD {Left_Value}' + '\n')
        y = len(output_list)
        output_list.append(f'JNEG {y+2}' + '\n')
        z = len(output_list)
        output_list.append(f'JUMP {z+3}' + '\n')
        output_list.append('SUB 0' + '\n')
        output_list.append(f'SUB {Left_Value}' + '\n')
        output_list.append(f'STORE {Lef}' + '\n')
        a = len(output_list)
        output_list.append(f'JZERO {a + 15}' + '\n')
        output_list.append(f'SHIFT {Neg}' + '\n')
        output_list.append(f'SHIFT {Pos}' + '\n')
        output_list.append(f'SUB {Lef}' + '\n')
        b = len(output_list)
        output_list.append(f'JZERO {b + 4}' + '\n')
        output_list.append(f'LOAD {Generated_Number}' + '\n')
        output_list.append(f'ADD {Rig}' + '\n')
        output_list.append(f'STORE {Generated_Number}' + '\n')
        output_list.append(f'LOAD {Rig}' + '\n')
        output_list.append(f'SHIFT {Pos}' + '\n')
        output_list.append(f'STORE {Rig}' + '\n')
        output_list.append(f'LOAD {Lef}' + '\n')
        output_list.append(f'SHIFT {Neg}' + '\n')
        output_list.append(f'STORE {Lef}' + '\n')
        c = len(output_list)
        output_list.append(f'JUMP {c-14}' + '\n')
        output_list.append(f'LOAD {Left_Value}' + '\n')
        d = len(output_list)
        output_list.append(f'JPOS {d+4}' + '\n')
        output_list.append(f'SUB 0' + '\n')
        output_list.append(f'SUB {Generated_Number}' + '\n')
        e = len(output_list)
        output_list.append(f'JUMP {e+2}' + '\n')
        output_list.append(f'LOAD {Generated_Number}' + '\n')
        output_list.append(f'STORE {Right_Value}' + '\n')


class Div(Expression):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        add_to_output(generate_number(-1, Neg))
        add_to_output(generate_number(1, Pos))
        global output_list
        output_list.append(f'SUB 0')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'STORE {Third}')
        output_list.append(f'LOAD {Right_Value}')
        x = len(output_list)
        output_list.append(f'JZERO {x + 75}')
        y = len(output_list)
        output_list.append(f'JPOS {y +3}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Right_Value}')
        output_list.append(f'STORE {Rig}')
        output_list.append(f'STORE {Fifth}')
        output_list.append(f'LOAD {Left_Value}')
        z = len(output_list)
        output_list.append(f'JZERO {z + 68}')
        a= len(output_list)
        output_list.append(f'JPOS {a + 3}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Left_Value}')
        output_list.append(f'STORE {Lef}')
        b = len(output_list)
        output_list.append(f'JZERO {b + 8}')
        output_list.append(f'SHIFT {Neg}')
        output_list.append(f'STORE {Fourth}')
        output_list.append(f'LOAD {Third}')
        output_list.append(f'INC')
        output_list.append(f'STORE {Third}')
        output_list.append(f'LOAD {Fourth}')
        c = len(output_list)
        output_list.append(f'JUMP {c -7}')
        output_list.append(f'LOAD {Rig}')
        output_list.append(f'SHIFT {Third}')
        output_list.append(f'STORE {Rig}')
        output_list.append(f'LOAD {Lef}')
        output_list.append(f'SUB {Rig}')
        d = len(output_list)
        output_list.append(f'JNEG {d + 6}')
        output_list.append(f'STORE {Lef}')
        output_list.append(f'LOAD {Pos}')
        output_list.append(f'SHIFT {Third}')
        output_list.append(f'ADD {Generated_Number}')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'LOAD {Rig}')
        output_list.append(f'SHIFT {Neg}')
        output_list.append(f'STORE {Rig}')
        output_list.append(f'LOAD {Third}')
        output_list.append(f'DEC')
        output_list.append(f'STORE {Third}')
        e = len(output_list)
        output_list.append(f'JNEG {e + 5}')
        output_list.append(f'LOAD {Lef}')
        f = len(output_list)
        output_list.append(f'JNEG {f + 3}')
        g = len(output_list)
        output_list.append(f'JZERO {g + 2}')
        h = len(output_list)
        output_list.append(f'JUMP {h - 18}')
        output_list.append(f'LOAD {Neg}')
        output_list.append(f'STORE {Fourth}')
        output_list.append(f'LOAD {Left_Value}')
        i= len(output_list)
        output_list.append(f'JPOS {i + 4}')
        output_list.append(f'LOAD {Fourth}')
        output_list.append(f'INC')
        output_list.append(f'STORE {Fourth}')
        output_list.append(f'LOAD {Right_Value}')
        j = len(output_list)
        output_list.append(f'JPOS {j + 5}')
        output_list.append(f'LOAD {Fourth}')
        output_list.append(f'INC')
        output_list.append(f'STORE {Fourth}')
        k = len(output_list)
        output_list.append(f'JUMP {k + 3}')
        output_list.append(f'LOAD {Left_Value}')
        m = len(output_list)
        output_list.append(f'JNEG {m + 3}')
        n = len(output_list)
        output_list.append(f'JZERO {n + 2}')
        o = len(output_list)
        output_list.append(f'JUMP {o + 12}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Generated_Number}')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'LOAD {Lef}')
        p = len(output_list)
        output_list.append(f'JZERO {p + 7}')
        output_list.append(f'LOAD {Generated_Number}')
        output_list.append(f'DEC')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'LOAD {Fifth}')
        output_list.append(f'SUB {Lef}')
        output_list.append(f'STORE {Lef}')
        output_list.append(f'LOAD {Right_Value}')
        r = len(output_list)
        output_list.append(f'JPOS {r + 4}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Lef}')
        output_list.append(f'STORE {Lef}')


class Mod(Expression):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        add_to_output(generate_number(-1, Neg))
        add_to_output(generate_number(1, Pos))
        global output_list
        output_list.append(f'SUB 0')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'STORE {Third}')
        output_list.append(f'LOAD {Right_Value}')
        x = len(output_list)
        output_list.append(f'JZERO {x + 75}')
        y = len(output_list)
        output_list.append(f'JPOS {y + 3}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Right_Value}')
        output_list.append(f'STORE {Rig}')
        output_list.append(f'STORE {Fifth}')
        output_list.append(f'LOAD {Left_Value}')
        z = len(output_list)
        output_list.append(f'JZERO {z + 68}')
        a = len(output_list)
        output_list.append(f'JPOS {a + 3}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Left_Value}')
        output_list.append(f'STORE {Lef}')
        b = len(output_list)
        output_list.append(f'JZERO {b + 8}')
        output_list.append(f'SHIFT {Neg}')
        output_list.append(f'STORE {Fourth}')
        output_list.append(f'LOAD {Third}')
        output_list.append(f'INC')
        output_list.append(f'STORE {Third}')
        output_list.append(f'LOAD {Fourth}')
        c = len(output_list)
        output_list.append(f'JUMP {c - 7}')
        output_list.append(f'LOAD {Rig}')
        output_list.append(f'SHIFT {Third}')
        output_list.append(f'STORE {Rig}')
        output_list.append(f'LOAD {Lef}')
        output_list.append(f'SUB {Rig}')
        d = len(output_list)
        output_list.append(f'JNEG {d + 6}')
        output_list.append(f'STORE {Lef}')
        output_list.append(f'LOAD {Pos}')
        output_list.append(f'SHIFT {Third}')
        output_list.append(f'ADD {Generated_Number}')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'LOAD {Rig}')
        output_list.append(f'SHIFT {Neg}')
        output_list.append(f'STORE {Rig}')
        output_list.append(f'LOAD {Third}')
        output_list.append(f'DEC')
        output_list.append(f'STORE {Third}')
        e = len(output_list)
        output_list.append(f'JNEG {e + 5}')
        output_list.append(f'LOAD {Lef}')
        f = len(output_list)
        output_list.append(f'JNEG {f + 3}')
        g = len(output_list)
        output_list.append(f'JZERO {g + 2}')
        h = len(output_list)
        output_list.append(f'JUMP {h - 18}')
        output_list.append(f'LOAD {Neg}')
        output_list.append(f'STORE {Fourth}')
        output_list.append(f'LOAD {Left_Value}')
        i = len(output_list)
        output_list.append(f'JPOS {i + 4}')
        output_list.append(f'LOAD {Fourth}')
        output_list.append(f'INC')
        output_list.append(f'STORE {Fourth}')
        output_list.append(f'LOAD {Right_Value}')
        j = len(output_list)
        output_list.append(f'JPOS {j + 5}')
        output_list.append(f'LOAD {Fourth}')
        output_list.append(f'INC')
        output_list.append(f'STORE {Fourth}')
        k = len(output_list)
        output_list.append(f'JUMP {k + 3}')
        output_list.append(f'LOAD {Left_Value}')
        m = len(output_list)
        output_list.append(f'JNEG {m + 3}')
        n = len(output_list)
        output_list.append(f'JZERO {n + 2}')
        o = len(output_list)
        output_list.append(f'JUMP {o + 12}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Generated_Number}')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'LOAD {Lef}')
        p = len(output_list)
        output_list.append(f'JZERO {p + 7}')
        output_list.append(f'LOAD {Generated_Number}')
        output_list.append(f'DEC')
        output_list.append(f'STORE {Generated_Number}')
        output_list.append(f'LOAD {Fifth}')
        output_list.append(f'SUB {Lef}')
        output_list.append(f'STORE {Lef}')
        output_list.append(f'LOAD {Right_Value}')
        r = len(output_list)
        output_list.append(f'JPOS {r + 4}')
        output_list.append(f'SUB 0')
        output_list.append(f'SUB {Lef}')
        output_list.append(f'STORE {Lef}')
        output_list.append(f'LOAD {Lef}')
        output_list.append(f'STORE {Generated_Number}')


class Value(Expression):
    def eval(self):
        self.left.generate_left_value()
        add_to_output(move_to_cell(Left_Value, Generated_Number))


class Condition:
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Eq(Condition):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Condition_Value}' + '\n'
        add_to_output(result)


class Neq(Condition):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Condition_Value}' + '\n'
        add_to_output(result)


class Le(Condition):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Condition_Value}' + '\n'
        add_to_output(result)


class Ge(Condition):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Condition_Value}' + '\n'
        add_to_output(result)


class Leq(Condition):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Condition_Value}' + '\n'
        add_to_output(result)


class Geq(Condition):
    def eval(self):
        self.left.generate_left_value()
        self.right.generate_right_value()
        result: str = f'LOAD {Left_Value}' + '\n' + f'SUB {Right_Value}' + '\n' + f'STORE {Condition_Value}' + '\n'
        add_to_output(result)


class Assign:
    def __init__(self, id, value):
        self.id = id
        self.value = value

    def eval(self):
        self.id.generate_to_assign()
        self.value.eval()
        add_to_output(assign_value_to_cell(Variable_Index, Generated_Number))


class Write:
    def __init__(self, value):
        self.value = value

    def eval(self):
        self.value.generate_left_value()
        result: str = f'LOAD{Left_Value}' + '\nPUT\n'
        add_to_output(result)


class Read:
    def __init__(self, id):
        self.id = id

    def eval(self):
        self.id.generate_to_assign()
        result: str = 'GET\n' + f'STOREI{Variable_Index}' + '\n'
        add_to_output(result)


class IfElse:
    def __init__(self, condition, commands0, commands1):
        self.condition = condition
        self.commands0 = commands0
        self.commands1 = commands1

    def eval(self):
        self.condition.eval()
        add_to_output(f'LOAD {Condition_Value}' + '\n')
        global output_list
        x = len(output_list)
        output_list.append('')
        output_list.append('')
        for i in self.commands0.commands:
            i.eval()
        output_list.append('')
        y = len(output_list)
        if isinstance(self.condition, Eq):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JNEG {y}'
        elif isinstance(self.condition, Neq):
            output_list[x] = f'JZERO {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Le):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Ge):
            output_list[x] = f'JNEG {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Leq):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JPOS {y}'
        elif isinstance(self.condition, Geq):
            output_list[x] = f'JNEG {y}'
            output_list[x + 1] = f'JNEG {y}'
        for i in self.commands1.commands:
            i.eval()
        z = len(output_list)
        output_list[y - 1] = f'JUMP {z}'


class If:
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def eval(self):
        self.condition.eval()
        add_to_output(f'LOAD {Condition_Value}' + '\n')
        global output_list
        x = len(output_list)
        output_list.append('')
        output_list.append('')
        for i in self.commands.commands:
            i.eval()
        y = len(output_list)
        if isinstance(self.condition, Eq):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JNEG {y}'
        elif isinstance(self.condition, Neq):
            output_list[x] = f'JZERO {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Le):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Ge):
            output_list[x] = f'JNEG {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Leq):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JPOS {y}'
        elif isinstance(self.condition, Geq):
            output_list[x] = f'JNEG {y}'
            output_list[x + 1] = f'JNEG {y}'


class WhileDo:
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def eval(self):
        global output_list
        z = len(output_list)
        self.condition.eval()
        add_to_output(f'LOAD {Condition_Value}' + '\n')
        x = len(output_list)
        output_list.append('')
        output_list.append('')
        for i in self.commands.commands:
            i.eval()
        output_list.append(f'JUMP {z}')
        y = len(output_list)
        if isinstance(self.condition, Eq):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JNEG {y}'
        elif isinstance(self.condition, Neq):
            output_list[x] = f'JZERO {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Le):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Ge):
            output_list[x] = f'JNEG {y}'
            output_list[x + 1] = f'JZERO {y}'
        elif isinstance(self.condition, Leq):
            output_list[x] = f'JPOS {y}'
            output_list[x + 1] = f'JPOS {y}'
        elif isinstance(self.condition, Geq):
            output_list[x] = f'JNEG {y}'
            output_list[x + 1] = f'JNEG {y}'


class DoWhile:
    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def eval(self):
        global output_list
        y = len(output_list)
        for i in self.commands.commands:
            i.eval()
        self.condition.eval()
        add_to_output(f'LOAD {Condition_Value}' + '\n')
        if isinstance(self.condition, Eq):
            add_to_output(f'JZERO {y}')
            add_to_output(f'JZERO {y}')
        elif isinstance(self.condition, Neq):
            add_to_output(f'JPOS {y}')
            add_to_output(f'JNEG {y}')
        elif isinstance(self.condition, Le):
            add_to_output(f'JNEG {y}')
            add_to_output(f'JNEG {y}')
        elif isinstance(self.condition, Ge):
            add_to_output(f'JPOS {y}')
            add_to_output(f'JPOS {y}')
        elif isinstance(self.condition, Leq):
            add_to_output(f'JNEG {y}')
            add_to_output(f'JZERO {y}')
        elif isinstance(self.condition, Geq):
            add_to_output(f'JPOS {y}')
            add_to_output(f'JZERO {y}')


class ForTo:
    def __init__(self, id, value1, value2, commands):
        global counter
        global variables
        self.id = id
        self.value1 = value1
        self.value2 = value2
        self.commands = commands
        self.counter = counter
        counter = counter + 2

    def eval(self):
        # generate_number(int(self.value1), counter)
        variables[self.id] = self.counter
        self.value1.generate_left_value()
        add_to_output(move_to_cell(Left_Value, self.counter))
        # add_to_variables(self.id)
        # generate_number(int(self.value2), counter - 1)
        self.value2.generate_left_value()
        add_to_output(move_to_cell(Left_Value, self.counter + 1))
        x = len(output_list)
        add_to_output(f'LOAD {self.counter + 1}')
        add_to_output(f'SUB {self.counter}')
        output_list.append('')
        for h in self.commands.commands:
            h.eval()
        add_to_output(f'LOAD {self.counter}')
        add_to_output(f'INC')
        add_to_output(f'STORE {self.counter}')
        add_to_output(f'JUMP {x}')
        y = len(output_list)
        output_list[x+2] = f'JNEG {y}'
        variables.pop(self.id)


class ForDownTo:
    def __init__(self, id, value1, value2, commands):
        global counter
        global variables
        self.id = id
        self.value1 = value1
        self.value2 = value2
        self.commands = commands
        self.counter = counter
        counter = counter + 2

    def eval(self):
        # generate_number(int(self.value1), counter)
        variables[self.id] = self.counter
        self.value1.generate_left_value()
        add_to_output(move_to_cell(Left_Value, self.counter))
        # add_to_variables(self.id)
        # generate_number(int(self.value2), counter - 1)
        self.value2.generate_left_value()
        add_to_output(move_to_cell(Left_Value, self.counter + 1))
        x = len(output_list)
        add_to_output(f'LOAD {self.counter}')
        add_to_output(f'SUB {self.counter + 1}')
        output_list.append('')
        for h in self.commands.commands:
            h.eval()
        add_to_output(f'LOAD {self.counter}')
        add_to_output(f'DEC')
        add_to_output(f'STORE {self.counter}')
        add_to_output(f'JUMP {x}')
        y = len(output_list)
        output_list[x+2] = f'JNEG {y}'
        variables.pop(self.id)


class Commands:
    commands = []

    def __init__(self, command):
        self.commands = command

    def add_command(self, command):
        self.commands.append(command)

    def eval(self):
        return self.commands


class Program:
    def __init__(self, commands, directory):
        self.commands = commands
        for i in commands.commands:
            i.eval()
        add_to_output("HALT")
        smth = ''
        for i in output_list:
            smth = smth + i + '\n'
        out = open(directory, "w", newline="\n")
        out.write(smth)
        out.close()
