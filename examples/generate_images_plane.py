# coding: utf-8

import sys
sys.path.append("/home/kuchida/Documents/programs/pbrt_cmd")
import json

from pbrt_cmd import (LookAt, Camera, Sampler, Integrator, Film, Spectrum, 
Fbm, Wrinkled, EZScaleTexture,
Matte, Metal, Plastic, Disney,
Sphere, Disk, Polymesh,
DistantSource, InfiniteSource, PointSource,
Rotate, Translate, 
attr_block, world_block, run_pbrt, unpack)
import os
from pathlib import Path
import numpy as np


def create_imager():
    look_at = LookAt(eye=[0, 0, 5], p_look=[0, 0, 0], up=[0, 1, 0])
    camera = Camera(projection="orthographic")
    #camera = Camera(projection="perspective", fov=45)
    sampler = Sampler("sobol", n_sample=64)
    integrator = Integrator("path", max_depth=20)
    film = Film(x_res=400, y_res=400, scale=1)

    imager = look_at + camera + sampler + integrator + film

    return imager


def create_tilted_disk(angle, material):
    rot = Rotate(angle, x=0, y=1, z=0)
    disk = Disk(radius=2)
    return attr_block(rot + material + disk)


def multi_distant_sources(p_from_list, p_to_list, spectrum_list):
    return [DistantSource(p_from, p_to, spectrum) for p_from, p_to, spectrum 
            in zip(p_from_list, p_to_list, spectrum_list)]

def multi_point_sources(p_from_list, spectrum_list):
    return [PointSource(p_from, spectrum) 
              for p_from, spectrum in zip(p_from_list, spectrum_list)]


def generate_ps_imgs_for_plastic(**kargs):
    
    rot_angle = kargs["rot_angle"]
    diffuse = kargs["diffuse"]
    material_roughness = kargs["material_roughness"]
    bump_roughness = kargs["bump_roughness"]
    specular = kargs["specular"]
    bump_enable = kargs["bump_enable"]
    bump_scale = kargs["bump_scale"]
    n_light = kargs["n_light"]

    base_dir = Path("/home/kuchida/Documents/programs/photometric_stereo/images")
    base_dir = base_dir / ("robustness_simulation/rot%0.1f" % (rot_angle) )
    base_dir.mkdir(parents=True, exist_ok=True)

    #save params
    with (base_dir / "params.json").open('w') as f:
        f.write(json.dumps(kargs, indent=4))

    imager = create_imager()

    #objects
    rot = Rotate(rot_angle, x=0, y=1, z=0)
    obj_spectrum = Spectrum("rgb", [1, 1, 1])
    diffuse_spectrum = Spectrum("rgb", [diffuse] * 3)
    specular_spectrum = Spectrum("rgb", [specular] * 3)

    disk = Polymesh("../plane_10um_mesh_no_normal.ply")
    #material = Metal()
    #material = Matte(obj_spectrum
    #material = Plastic()

    if bump_enable:
        bump_name = "bumps"
        texture = Fbm(bump_name, octaves=8, roughness=bump_roughness)
        scaled_tex = EZScaleTexture(bump_scale, texture)
        material = Plastic(kd=diffuse_spectrum, ks=specular_spectrum, 
                           roughness=material_roughness,bumpmap=scaled_tex.name)
        
        plane = attr_block(rot + scaled_tex + material + disk)

    else:
        material = Plastic(kd=diffuse_spectrum, ks=specular_spectrum, roughness=material_roughness)
        plane = attr_block(rot + material + disk)
    


    #lighting
    z = 10
    r = 10
    dx = 0
    
    thetas = np.arange(0, 2*np.pi, 2*np.pi/n_light)

    l_dirs = [[r*np.cos(theta)+dx, r*np.sin(theta), z] for theta in thetas]
    p_from_list = [[l] for l in l_dirs]
    p_to_list = [[[0, 0, 0]] for i in range(len(l_dirs))]

    light_spectrum = Spectrum("rgb", [1, 1, 1])
    specs_list = [[light_spectrum] * len(p_froms) for p_froms in p_from_list]

    light_sources = [multi_point_sources(p_froms, specs)
                        for p_froms, specs in zip(p_from_list, specs_list)]
    light_sources = [multi_distant_sources(p_froms, p_tos, specs)
                        for p_froms, p_tos, specs in zip(p_from_list, p_to_list, specs_list)]


    n_image = len(light_sources)
    fnames_pbrt = [base_dir / ("l%02d.pbrt" % i) for i in range(n_image)]
    fnames_image = [base_dir / ("l%02d.exr" % i) for i in range(n_image)]
    fnames_light = [base_dir / ("l%02d_light" % i) for i in range(n_image)]

    #writing pbrt files
    text_list = []
    for l_source in light_sources:
        world = unpack(l_source) + plane
        text = imager + world_block(world)
        text_list.append(text)


    for text, fname in zip(text_list, fnames_pbrt):
        with open(fname, 'w') as f:
            f.write(text)

    for fname, p_from in zip(fnames_light, p_from_list):
        np.save(fname, p_from)

    # run .pbrt files
    for fname_pbrt, fname_image in zip(fnames_pbrt, fnames_image):
        ret = run_pbrt(fname_pbrt, quiet=True, outfile=fname_image)
        
        if ret.returncode != 0:
            raise RuntimeError("pbrt returns abnormal value: %d" % ret.returncode)
        #break

if __name__ == "__main__":
    rot_angle = 0
    diffuse = 0.01
    material_roughness = 0.0
    bump_roughness = 0.55
    specular = 1.0
    bump_enable = True
    bump_scale = 0.01
    n_light = 4

    params = {"rot_angle": rot_angle, "material_roughness":material_roughness,
            "bump_roughness": bump_roughness, "specular": specular, "diffuse": diffuse,
            "bump_enable": bump_enable, "bump_scale": bump_scale,
            "n_light": n_light}
    
    rot_angle_list = np.linspace(0, 90, 45)
    for rot_angle in rot_angle_list:
        params["rot_angle"] = rot_angle
        generate_ps_imgs_for_plastic(**params)

