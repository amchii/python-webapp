示例：
```python
import inspect

def f(a, *b, c, d='t', **kw):
    pass

s=inspect.signature(f)
print('s:'+str(s))

p=inspect.signature(f).parameters

for name, param in p.items():
    print(name, param)
    print(name + ':' + str(param.kind))
    print(name + ':' + str(param.default))
    if param.kind == inspect.Parameter.KEYWORD_ONLY:
        print('yes')
    print('\n')
```

输出：

```python
s:<Signature (a, *b, c, d='t', **kw)>

a a
a:POSITIONAL_OR_KEYWORD			#位置参数
a:<class 'inspect._empty'>


b *b
b:VAR_POSITIONAL				#可变参数
b:<class 'inspect._empty'>


c c
c:KEYWORD_ONLY					#命名关键字参数
c:<class 'inspect._empty'>
yes


d d='t'
d:KEYWORD_ONLY					#命名关键字参数
d:t
yes

kw **kw
kw:VAR_KEYWORD					#关键字参数
kw:<class 'inspect._empty'>

```