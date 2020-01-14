from string import Template

a = []
t = Template('$name')
a .append(t)
t.substitute(name="hej")
print(t)
