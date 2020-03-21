
from pbrt_cmd import (LookAt, Camera, Sampler, Integrator, Film, Spectrum, 

Disney,
Sphere, 
DistantSource, 
Rotate, Translate, 
attr_block, world_block, run_pbrt, unpack)

from pathlib import Path

def create_imager():
    look_at = LookAt(eye=[0, 0, 5], p_look=[0, 0, 0], up=[0, 1, 0])
    camera = Camera(projection="orthographic")
    #camera = Camera(projection="perspective", fov=45)
    sampler = Sampler("sobol", n_sample=64)
    integrator = Integrator("path", max_depth=20)
    film = Film(x_res=400, y_res=400, scale=1)

    imager = look_at + camera + sampler + integrator + film

    return imager


if __name__ == "__main__":
    output_dir = Path("/home/kuchida/Documents/programs/pbrt_cmd/examples")

    imager = create_imager()

    # object
    obj_spectrum = Spectrum("rgb", [1, 1, 1])
    material = Disney(color=obj_spectrum, metallic=0.7, roughness=0.3)
    sphere = Sphere(r=1)

    obj = attr_block(material + sphere)

    #lighting
    light_spectrum = Spectrum("rgb", [1, 1, 1])
    light = DistantSource(p_from=[0,0,1], p_to=[0,0,0], spectrum=light_spectrum)

    # writing pbrt file
    world = world_block(light + obj)
    text = imager + world

    fname_pbrt = output_dir / "distant_source.pbrt"
    fname_pbrt.open("w").write(text)

    # run
    ret = run_pbrt(fname_pbrt, quiet=True, outfile=fname_pbrt.with_suffix(".exr"))
    if ret.returncode != 0:
            raise RuntimeError("pbrt returns abnormal value: %d" % ret.returncode)
    

