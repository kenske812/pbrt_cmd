# PBRT file Generator
helper functions/classes to generate pbrt input file.

Not all the attribute are implemented yet.

## install
```
pip install git+http://10.9.158.35:8080/git/kuchida/pbrt_cmd.git
pip uninstall pbrt_cmd
```

## Usage
```python
import pbrt_cmd
sphere = pbrt_cmd.Sphere(r=10)
```

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

See example files for more examples.
