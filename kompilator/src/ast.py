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
        print(variables)


# Negates number which is in register 0 (p0)
# Registers used: 0-1
def negate_number() -> str:
    return 'STORE 1' + '\n' + 'SUB 0\nSUB 1' + '\n'


# Generates constant value and stores it in destination_register
# registers used: 0-1
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
        print(self.value)

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
    def __init__(self, variable):
        self.variable = variable
        print(self.variable)
        add_to_variables(variable)


class DeclarationArray:
    def __init__(self, variable, start, end):
        self.variable = variable
        string = '{}({}:{})'.format(variable, start, end)
        global arrays
        global counter
        arrays[variable] = ArrayInfo(counter, int(end) - int(start), int(start))
        for x in range(int(start), int(end) + 1):
            add_to_variables(variable + str(x))


class Identifier:
    def __init__(self, id):
        self.id = id

    def eval(self):
        return self.id.eval()


class Pidentifier:
    def __init__(self, id):
        self.id = id
        print(self.id)

    def eval(self):
        if self.id in variables:
            generate_number(variables[self.id], Variable_Index)
        else:
            sys.exit()

    def getValue(self):
        return self.id

    def generate_left_value(self):
        add_to_output(move_to_cell(variables[self.id], Left_Value))

    def generate_right_value(self):
        add_to_output(move_to_cell(variables[self.id], Right_Value))

    def generate_to_assign(self):
        add_to_output(generate_number(variables[self.id], Variable_Index))


class PidentifierArrayID:
    def __init__(self, id1, id2):
        self.id = id1 + id2
        self.id1 = id1
        self.id2 = id2
        print(self.id)

    def eval(self):
        index = variables[self.id2]

    def getValue(self):
        return self.id

    def generate_left_value(self):
        add_to_output(pidentifier_expression_case(arrays[self.id1], variables[self.id2], Left_Value))

    def generate_right_value(self):
        add_to_output(pidentifier_expression_case(arrays[self.id1], variables[self.id2], Right_Value))

    def generate_to_assign(self):
        add_to_output(pidentifier_assignment_case(arrays[self.id1], variables[self.id2]))


class PidentifierArrayNumber:
    def __init__(self, id1, id2):
        self.id = id1 + id2
        print(self.id)

    def eval(self):
        if self.id in variables:
            generate_number(variables[self.id], Variable_Index)
        else:
            sys.exit()

    def getValue(self):
        return self.id

    def generate_left_value(self):
        add_to_output(move_to_cell(variables[self.id], Left_Value))

    def generate_right_value(self):
        add_to_output(move_to_cell(variables[self.id], Right_Value))

    def generate_to_assign(self):
        add_to_output(generate_number(variables[self.id], Variable_Index))


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
        # TODO
        return self.left.eval() - self.right.eval()


class Mul(Expression):
    def eval(self):
        return self.left.eval() * self.right.eval()


class Div(Expression):
    def eval(self):
        # TODO
        return self.left.eval() / self.right.eval()


class Mod(Expression):
    def eval(self):
        # TODO
        return self.left.eval() % self.right.eval()


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
        print('xd' + output_list[x + 1])
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
        print('wtf' + output_list[x - 1])
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
        variables[self.id] = self.counter

    def eval(self):
        # generate_number(int(self.value1), counter)
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
        print(x)
        add_to_output(f'JUMP {x}')
        y = len(output_list)
        print('he' + output_list[x+2])
        print(y)
        output_list[x+2] = f'JNEG {y}'


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
        variables[self.id] = self.counter

    def eval(self):
        # generate_number(int(self.value1), counter)
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
        print(x)
        add_to_output(f'JUMP {x}')
        y = len(output_list)
        print('he' + output_list[x+2])
        print(y)
        output_list[x+2] = f'JNEG {y}'


class Commands:
    commands = []

    def __init__(self, command):
        self.commands = command

    def add_command(self, command):
        self.commands.append(command)

    def eval(self):
        return self.commands


class Program:
    def __init__(self, commands):
        self.commands = commands
        for i in commands.commands:
            i.eval()
        add_to_output("HALT")
        print(output_list)
        smth = ''
        for i in output_list:
            smth = smth + i + '\n'
        out = open("out.mr", "w", newline="\n")
        out.write(smth)
        out.close()