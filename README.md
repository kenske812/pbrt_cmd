# PBRT file Generator
helper functions/classes to generate pbrt input file.

Not all the attribute are implemented yet.

Every class overrides \__str__ method to generate strings.
```python
look_at = LookAt(eye=[0, 0, 5], p_look=[0, 0, 0], up=[0, 1, 0])
print(look_at)

LookAt 0 0 5  
       0 0 0  
       0 1 0   
```

They also override \__add__ method to produce strings.

```python
#the type of world becomes str
world = point_source + sphere 
```
