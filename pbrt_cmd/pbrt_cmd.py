# coding: utf-8


import numpy as np
import subprocess
from pathlib import Path


def arr2str(arr, bracket=True):
    str_arr = [str(x) for x in arr]
    s = " ".join(str_arr)

    if bracket:
        return '['+ s + ']'
    else:
        return s

def unpack(obj_list):
    s = ""
    for obj in obj_list:
        s += obj

    return s

class StringGenerator:
    def __add__(self, other):
        return str(self) + "\n" + str(other)
    
    def __radd__(self, other):
        return str(other) + "\n" + str(self)

class BaseTexture:
    pass

class LookAt(StringGenerator):
    def __init__(self, eye, p_look, up):
        """    
        Args:
            eye (list or numpy array): eye
            p_look (list or numpy array)): look at point
            up (list or numpy array)): up vector
        """
        self.eye = eye
        self.p_look = p_look
        self.up = up

    def __str__(self):
        s  = "LookAt " + arr2str(self.eye, False) + "\n"
        s += "       " + arr2str(self.p_look, False) + "\n"
        s += "       " + arr2str(self.up, False) + "\n"

        return s


class Camera(StringGenerator):
    def __init__(self, projection, fov=None, screen_window=None):
        self.projection = projection
        self.fov = fov
        self.screen_window = screen_window #[x, -x, y, -y]
    
    def __str__(self):
        s = 'Camera "%s"\n' % self.projection
        if self.fov is not None:
            s += '    "float fov" %f\n' % (self.fov)
        if self.screen_window is not None:
            s += '    "float screenwindow" %s\n' % arr2str(self.screen_window)


        return s

class Sampler(StringGenerator):
    def __init__(self, method, n_sample):
        self.method = method
        self.n_sample = n_sample
    
    def __str__(self):
        s = 'Sampler "%s" "integer pixelsamples" %d\n' % (self.method, self.n_sample)
        return s

class Integrator(StringGenerator):
    def __init__(self, method, max_depth, light_sample_strategy=None):
        self.method = method
        self.max_depth = max_depth
        self.light_sample_strategy = light_sample_strategy
    
    def __str__(self):
        s = 'Integrator "%s" "integer maxdepth" %d\n' % (self.method, self.max_depth)
        if self.light_sample_strategy is not None:
            s += '    "string lightsamplestrategy" "%s"\n' % (self.light_sample_strategy)

        return s


class Film(StringGenerator):
    def __init__(self, x_res, y_res, scale=1.0, fname=None):
        self.fname = fname
        self.x_res = x_res
        self.y_res = y_res
        self.scale = scale
    
    def __str__(self):
        s = 'Film "image" \n'
        s += '    "integer xresolution" [%d]\n' % self.x_res
        s += '    "integer yresolution" [%d]\n' % self.y_res

        if self.scale != 1.0:
            s += '    "float scale" %f\n' % self.scale
        if self.fname is not None:
            s += '"string filename" "%s"\n' % self.fname
        return s
    

class PointSource(StringGenerator):
    def __init__(self, p_from, spectrum):
        self.p_from = p_from
        self.spectrum = spectrum
        self.spectrum.name = "I"
    
    def __str__(self):
        s  = 'LightSource "point"\n'
        s += '    "point from" ' + arr2str(self.p_from) + "\n"
        s += '    ' + str(self.spectrum) + "\n"

        return s

class DistantSource(StringGenerator):
    def __init__(self, p_from, p_to, spectrum):
        self.p_from = p_from
        self.p_to = p_to
        self.spectrum = spectrum
        self.spectrum.name = "L"
    
    def __str__(self):
        s  = 'LightSource "distant"\n'
        s += '    "point from" ' + arr2str(self.p_from) + "\n"
        s += '    "point to"   ' + arr2str(self.p_to) + "\n"
        s += '    ' + str(self.spectrum) + "\n"

        return s

class ProjectionSource(StringGenerator):
    def __init__(self, spectrum, fov, mapname, scale=1.0):
        self.spectrum = spectrum * scale
        self.spectrum.name = 'I'
        self.fov = fov
        self.mapname = mapname
        self.scale = scale
    def __str__(self):
        s  = 'LightSource "projection"\n'
        s += '    ' + str(self.spectrum) + "\n"
        s += '    "float fov" %f\n' % self.fov
        s += '    "string mapname" "%s"\n' % self.mapname

        return s

class InfiniteSource(StringGenerator):
    def __init__(self, spectrum):
        self.spectrum = spectrum
        self.spectrum.name = 'L'
    
    def __str__(self):
        s = 'LightSource "infinite"\n'
        s += '    ' + str(self.spectrum) + "\n"
        return s

class AreaLightSource(StringGenerator):
    def __init__(self, spectrum, reverse_orientation=False):
        self.spectrum = spectrum
        self.spectrum.name = 'L'
        self.reverse_orientation = reverse_orientation
    
    def __str__(self):
        s = 'AreaLightSource "diffuse"\n'
        s += '    ' + str(self.spectrum) + "\n"
        if self.reverse_orientation:
            s += '    ReverseOrientation\n'
        return s


class Sphere(StringGenerator):
    def __init__(self, r):
        self.r = r
    def __str__(self):
        return 'Shape "sphere" "float radius" %f\n' % self.r 

class Polymesh(StringGenerator):
    def __init__(self, fname):
        self.fname = fname
    
    def __str__(self):
        return 'Shape "plymesh" "string filename" ["%s"]' % self.fname


class Translate(StringGenerator):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return "Translate %f %f %f\n" % (self.x, self.y, self.z)


class Rotate(StringGenerator):
    def __init__(self, angle, x, y, z):
        """angle in degree"""

        self.angle = angle
        self.x = x
        self.y = y
        self.z = z
    
    def __str__(self):
        return "Rotate %f %f %f %f\n" % (self.angle, self.x, self.y, self.z)


class Disk(StringGenerator):
    def __init__(self, height=0, radius=1, innerradius=0, phimax=360):
        self.height = height
        self.radius = radius
        self.innerradius = innerradius
        self.phimax = phimax
    
    def __str__(self):
        s = 'Shape "disk"\n'
        if self.height != 0:
            s += '    "float height" %f\n' % self.height
        if self.radius != 1:
            s += '    "float radius" %f\n' % self.radius
        if self.innerradius != 0:
            s += '    "float innerradius" %f\n' % self.innerradius
        if self.phimax != 360:
            s += '    "float phimax" %f\n' % self.phimax
        
        return s


class Matte(StringGenerator):
    def __init__(self, spectrum, bumpmap=None):
        self.spectrum = spectrum
        self.spectrum.name = "Kd"
        self.bumpmap = bumpmap
    
    def __str__(self):
        s = 'Material "matte" \n' 
        s += '    ' + str(self.spectrum) + "\n"

        if self.bumpmap is not None:
            s += '    "texture bumpmap" "%s"\n' % self.bumpmap

        return s 

class Mirror(StringGenerator):
    def __init__(self, spectrum, bumpmap=None):
        self.spectrum = spectrum
        self.spectrum.name = "Kr"
        self.bumpmap = bumpmap
    
    def __str__(self):
        s = 'Material "mirror" \n' 
        s += '    ' + str(self.spectrum) + "\n"

        if self.bumpmap is not None:
            s += '    "texture bumpmap" "%s"\n' % self.bumpmap

        return s         



class Metal(StringGenerator):
    def __init__(self, eta=None, k=None, roughness=None, bumpmap=None):
        self.roughness = roughness

        if isinstance(eta, Spectrum):
            eta.name = "eta"
        else:
            TypeError("only Spectrum type is supported")

        if isinstance(k, Spectrum):
            k.name = "k"
        else:
            TypeError("only Spectrum type is supported")
 
        self.eta = eta
        self.k = k
        self.bumpmap = bumpmap
    
    def __str__(self):
        s = 'Material "metal"\n'
        
        if self.roughness is not None:
            s += '    "float roughness" %f\n' % self.roughness
        
        if self.eta is not None:
            s += '    ' + str(self.eta) + "\n"

        if self.k is not None:
            s += '    ' + str(self.k) + "\n"

        if self.bumpmap is not None:
            s += '    "texture bumpmap" "%s"\n' % self.bumpmap

        return s 

class NoneMaterial(StringGenerator):
    def __init__(self):
        pass
    def __str__(self):
        s = 'Material "none"\n'
        return s

class Plastic(StringGenerator):
    def __init__(self, kd=None, ks=None, roughness=None, bumpmap=None):
        self.roughness = roughness

        if isinstance(kd, Spectrum):
            kd.name = "Kd"
        elif kd is not None:
            raise TypeError("only Spectrum is supported for kd")



        if isinstance(ks, Spectrum):
            ks.name = "Ks"
        elif ks is not None:
            raise TypeError("only Spectrum is supported for ks")
 
        self.kd = kd
        self.ks = ks
        self.bumpmap = bumpmap
    
    def __str__(self):
        s = 'Material "plastic"\n'
        
        if self.roughness is not None:
            s += '    "float roughness" %f\n' % self.roughness
        
        if self.kd is not None:
            s += '    ' + str(self.kd) + "\n"

        if self.ks is not None:
            s += '    ' + str(self.ks) + "\n"
        
        if self.bumpmap is not None:
            s += '    "texture bumpmap" "%s"\n' % self.bumpmap

        return s


class Fbm(StringGenerator, BaseTexture):
    def __init__(self, name, type="float", octaves=None, roughness=None):
       self.name = name
       self.octaves = octaves
       self.roughness = roughness
       self.type = type
    
    def __str__(self):
        s = 'Texture "%s" "%s" "fbm"\n' % (self.name, self.type)
        
        if self.octaves is not None:
            s += '    "integer octaves" %d\n' % self.octaves
        
        if self.roughness is not None:
            s += '    "float roughness" %f\n' % self.roughness
        
        return s

class Wrinkled(StringGenerator, BaseTexture):
    def __init__(self, name, type="float", octaves=None, roughness=None):
       self.name = name
       self.octaves = octaves
       self.roughness = roughness
       self.type = type
    
    def __str__(self):
        s = 'Texture "%s" "%s" "wrinkled"\n' % (self.name, self.type)
        
        if self.octaves is not None:
            s += '    "integer octaves" %d\n' % self.octaves
        
        if self.roughness is not None:
            s += '    "float roughness" %f\n' % self.roughness
        
        return s

class ConstantTexture(StringGenerator, BaseTexture):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        s = 'Texture "%s" "float" "constant"\n' % (self.name)
        s += '    "float value" %f\n' % self.value

        return s
    

class ScaleTexture(StringGenerator, BaseTexture):
    def __init__(self, name, tex1, tex2):
        """[summary]
        
        Args:
            StringGenerator ([type]): [description]
            name (string): name of this texture
            tex1 (string): name of texture 1
            tex2 (string): name of texutre 2
        """
        self.name = name
        self.tex1 = tex1
        self.tex2 = tex2
    
    def __str__(self):
        s = 'Texture "%s" "float" "scale"\n' % (self.name)
        s += '    "texture tex1" "%s"\n' %  self.tex1
        s += '    "texture tex2" "%s"\n' %  self.tex2

        return s

class EZScaleTexture(StringGenerator, BaseTexture):
    """The wrapper class of ScaleTexture for ease of use.
    This class outputs strings of 
        input texture,
        const texture for scale value,
        ScaleTexture.
    """

    def __init__(self, scale, tex):
        """
        Args:
            scale ([type]): [description]
            tex ([type]): [description]
        
        Raises:
            ValueError: [description]
        """

        if not isinstance(tex, BaseTexture):
            raise ValueError("input texture is not a instance of Texture but %s" % type(tex))
        
        self.scale = scale
        self.tex = tex
        self.name = "scaled_" + self.tex.name

    def __str__(self):
        const_name = "__" + self.tex.name + "_" + "scale_val"
        const_tex = ConstantTexture(const_name, self.scale)

        scale_tex = ScaleTexture(self.name, const_name, self.tex.name)

        return str(self.tex) + str(const_tex) + str(scale_tex)



class Disney(StringGenerator):
    def __init__(self, color=None, anisotropic=None, clearcoat=None,
                    clearcoatgloss=None, eta=None, metallic=None,
                    roughness=None, scatterdistance=None,
                    sheen=None, sheentint=None, 
                    spectrans=None, speculartin=None,
                    bumpmap=None):
    
        self.color = color
        self.anisotropic = anisotropic
        self.clearcoat = clearcoat
        self.clearcoatgloss = clearcoatgloss
        self.eta = eta
        self.metallic = metallic
        self.roughness = roughness
        self.scatterdistance = scatterdistance
        self.sheen = sheen
        self.sheentint = sheentint
        self.spectrans = spectrans
        self.speculartin = speculartin
        self.bumpmap = bumpmap

        if isinstance(self.color, Spectrum):
            self.color.name = "color"
        elif self.color is not None:
            raise TypeError("only Spectrum is supported")

        if isinstance(self.scatterdistance, Spectrum):
            self.scatterdistance.name = "scatterdistance"
        elif self.scatterdistance is not None:
            raise TypeError("only Spectrum is supported")       

    def __str__(self):
        s = 'Material "disney"\n'

        for k, v in self.__dict__.items():
            if v is None:
                continue
            
            if k == 'color' or k == 'scatterdistance':
                #spectrums
                s += '    ' + str(v) + "\n"
            elif k == "bumpmap":
                s += '    "texture bumpmap" "%s"\n' % v
            
            else:
                #floats
                s += '    "float %s" %f\n' % (k, v)
        
        return s
        
        



class Spectrum:
    def __init__(self, _type, val, name=None):
        self.type = _type
        self.name = name
        self.val = val
    
    def __str__(self):
        return '"%s %s" %s' % (self.type, self.name, arr2str(self.val))
    
    def __mul__(self, v):
        self.val = [a * v for a in self.val]
        return self

        
def world_block(s):
    tabbed = "    " + s.replace("\n", "\n    ")
    return "\nWorldBegin\n" + tabbed + "\nWorldEnd\n"

def attr_block(s):
    tabbed = "    " + s.replace("\n\n", "\n").replace("\n", "\n    ")
    return "\nAttributeBegin\n" + tabbed +"\nAttributeEnd\n"


def run_pbrt(fname_pbrt, quiet=False, outfile=None):
    cmd = ["pbrt", str(fname_pbrt)]
    if quiet:
        cmd.append("--quiet")
    if outfile is not None:
        cmd.append("--outfile")
        cmd.append(str(outfile))

    if not quiet:
        print("running '" + " ".join(cmd) + "'")
    ret = subprocess.run(cmd)

    #if ret == 0:
    #    print("done")

    return ret

if __name__ == "__main__":

    base_dir = Path("/home/kuchida/Documents/programs/pbrt_cmd")
    fname_pbrt = base_dir / "sphere2.pbrt"
    fname_out = base_dir / "sphere.png"

    look_at = LookAt(eye=[0, 0, 5], p_look=[0, 0, 0], up=[0, 1, 0])
    camera = Camera(projection="perspective", fov=45)
    sampler = Sampler("sobol", n_sample=128)
    integrator = Integrator("sppm", max_depth=20)
    film = Film(x_res=400, y_res=400, scale=10000)

    obj_list = [look_at, camera, sampler, integrator, film]
    imager = "\n\n".join([str(x) for x in obj_list]) + "\n\n"
    

    sphere = attr_block(Sphere(1) + Matte(Spectrum("rgb", [1, 1, 1])))

    i_light = [1, 1, 1]
    spectrum = Spectrum("rgb", [1, 1, 1])
    point_source = PointSource(p_from=[0, 100, 100], spectrum=spectrum)
    
    world = point_source + sphere
    
    text = imager + world_block(world)
    print(text)

    with open(fname_pbrt, 'w') as f:
        f.write(text)
    
    run_pbrt(fname_pbrt, outfile=fname_out)

