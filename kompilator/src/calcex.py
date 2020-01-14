from sly import Lexer, Parser
from ast import *

class Scanner(Lexer):
    # Set of token names.   This is always required
    tokens = {'DECLARE', 'BEGIN', 'END',
              'NUM',
              'PLUS', 'MINUS', 'TIMES', 'DIV', 'MOD',
              'EQ', 'NEQ', 'LE', 'GE', 'LEQ', 'GEQ',
              'ASSIGN',
              'IF', 'THEN', 'ELSE', 'ENDIF',
              'DO',
              'FOR', 'FROM', 'TO', 'DOWNTO', 'ENDFOR',
              'WHILE', 'ENDDO', 'ENDWHILE',
              'READ', 'WRITE',
              'ID'}

    literals = "();,:"
    # String containing ignored characters between tokens

    # Regular expression rules for tokens

    ignore = ' \t'
    ignore_comment = r'\[[^\]]*\]'
    ignore_newline = r'\n+'

    ID = r'[_a-z]+'

    PLUS = r'PLUS'
    MINUS = r'MINUS'
    TIMES = r'TIMES'
    DIV = r'DIV'
    MOD = r'MOD'

    NEQ = r'NEQ'
    EQ = r'EQ'
    LEQ = r'LEQ'
    LE = r'LE'
    GEQ = r'GEQ'
    GE = r'GE'

    ASSIGN = r'ASSIGN'

    ENDWHILE = r'ENDWHILE'
    ENDFOR = r'ENDFOR'
    FOR = r'FOR'
    FROM = r'FROM'
    DOWNTO = r'DOWNTO'
    TO = r'TO'

    WHILE = r'WHILE'
    ENDDO = r'ENDDO'
    DO = r'DO'

    READ = r'READ'
    WRITE = r'WRITE'

    ENDIF = r'ENDIF'
    IF = r'IF'
    THEN = r'THEN'
    ELSE = r'ELSE'

    DECLARE = r'DECLARE'
    BEGIN = r'BEGIN'
    END = r'END'

    NUM = r'-?\d+'

    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        string = "Illegal character {} in line {}".format(t.value[0], t.lineno)
        print(string)
        self.index += 1


class MyParser(Parser):
    tokens = Scanner.tokens

    @_('DECLARE declarations BEGIN commands END')
    def program(self, p):
        return Program(p.commands)

    @_('BEGIN commands END')
    def program(self, p):
        return Program(p.commands)

    @_('declarations "," ID')
    def declarations(self, p):
        Declaration(p.ID)

    @_('declarations "," ID "(" NUM  ":" NUM ")"')
    def declarations(self, p):
        DeclarationArray(p.ID, p.NUM0, p.NUM1)

    @_('ID')
    def declarations(self, p):
        Declaration(p.ID)

    @_('ID "(" NUM ":" NUM ")"')
    def declarations(self, p):
        DeclarationArray(p.ID, p.NUM0, p.NUM1)

    @_('commands command')
    def commands(self, p):
        p.commands.add_command(p.command)
        return p.commands

    @_('command')
    def commands(self, p):
        return Commands([p.command])

    @_('identifier ASSIGN expression ";"')
    def command(self, p):
        return Assign(p.identifier, p.expression)

    @_('IF condition THEN commands ELSE commands ENDIF')
    def command(self, p):
        return IfElse(p.condition, p.commands0, p.commands1)

    @_('IF condition THEN commands ENDIF')
    def command(self, p):
        return If(p.condition, p.commands)

    @_('WHILE condition DO commands ENDWHILE')
    def command(self, p):
        return WhileDo(p.condition, p.commands)

    @_('DO commands WHILE condition ENDDO')
    def command(self, p):
        return DoWhile(p.condition, p.commands)

    @_('FOR ID FROM value TO value DO commands ENDFOR')
    def command(self, p):
        return ForTo(p.ID, p.value0, p.value1, p.commands)

    @_('FOR ID FROM value DOWNTO value DO commands ENDFOR')
    def command(self, p):
        return ForDownTo(p.ID, p.value0, p.value1, p.commands)

    @_('READ identifier ";"')
    def command(self, p):
        return Read(p.identifier)

    @_('WRITE value ";"')
    def command(self, p):
        return Write(p.value)

    @_('value')
    def expression(self, p):
        return Value(p.value, p.value)

    @_('value PLUS value')
    def expression(self, p):
        return Sum(p.value0, p.value1)

    @_('value MINUS value')
    def expression(self, p):
        return Sub(p.value0, p.value1)

    @_('value TIMES value')
    def expression(self, p):
        return Mul(p.value0, p.value1)

    @_('value DIV value')
    def expression(self, p):
        return Div(p.value0, p.value1)

    @_('value MOD value')
    def expression(self, p):
        return Mod(p.value0, p.value1)

    @_('value EQ value')
    def condition(self, p):
        return Eq(p.value0, p.value1)

    @_('value NEQ value')
    def condition(self, p):
        return Neq(p.value0, p.value1)

    @_('value LE value')
    def condition(self, p):
        return Le(p.value0, p.value1)

    @_('value GE value')
    def condition(self, p):
        return Ge(p.value0, p.value1)

    @_('value LEQ value')
    def condition(self, p):
        return Leq(p.value0, p.value1)

    @_('value GEQ value')
    def condition(self, p):
        return Geq(p.value0, p.value1)

    @_('NUM')
    def value(self, p):
        return Number(p.NUM)

    @_('identifier')
    def value(self, p):
        return IdValue(p.identifier)

    @_('ID')
    def identifier(self, p):
        return Pidentifier(p.ID)

    @_('ID "(" ID ")"')
    def identifier(self, p):
        return PidentifierArrayID(p.ID0, p.ID1)

    @_('ID "(" NUM ")"')
    def identifier(self, p):
        return PidentifierArrayNumber(p.ID, p.NUM)


if __name__ == '__main__':
    data = "ENDIF     END"
    lexer = Scanner()
    parser = MyParser()

    # for tok in lexer.tokenize(data):
    #     print('type=%r, value=%r' % (tok.type, tok.value))

    with open(sys.argv[1], 'r') as input_file:
        data = input_file.read()
        parser.parse(lexer.tokenize(data))
