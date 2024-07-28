import uuid

import numpy as np
import gdsfactory as gf
from gdsfactory.technology import LayerLevel
from gdsfactory.typings import List, Union, Dict, Component, ComponentReference

def micro(val: float) -> float:
    return val*1e+3

# generate uuid
def gen_uuid(name: str) -> str:
    return f"{name}_{uuid.uuid4().hex}"

def make_even_number(num: float):
    temp = str(np.round(num,3)/2)
    temp = temp[temp.index(".")+1:]
    if len(temp) > 3:
        num += 0.001
    return np.round(num, 3)

def find_outer_and_inner_r(rout: float, rin: float, y: float) -> Union[float, float]:
    if rout < rin:
        raise ValueError("Outer radius must be larger than inner radius")
    
    if rin > y and rout > y:
        width = make_even_number(np.sqrt(rout**2 - y**2) - np.sqrt(rin**2 - y**2))
        rin_x = np.sqrt(rin**2 - y**2)
        rout = np.round(np.sqrt((width + rin_x)**2 + y**2), 3)
    return rout, rin

def gen_objects(
    func: callable,
    **specs: dict,
) -> List[gf.Component]:
    """
    Generate objects from a single function with different specifications

    Args:
        func [callable]: callable: function to be called
        number [int]: int: number of objects to be generated
        specs [dict]: dict: specifications for the objects. The specifications should be a dictionary with the keys as the arguments of the function and the values can be a list or  a single value. If it is a value, the value will be applied to all the objects. If it is a list, the values will be applied to the objects in the order of the list.

    Returns:
        List[gf.Component]: list of generated objects

    Example:
        >> obj_list = Methods.gen_objects(
        >>    gf.components.coupler_asymmetric,
        >>    gap=gap,
        >>    dx=5,
        >>    dy=5,
        >>    cross_section=cs
        >> )
    """
    # error checking if all lists have the same length
    max_len = max([len(value) for value in specs.values() if isinstance(value, (list, np.ndarray))], default=1)

    if any([len(value) != max_len for value in specs.values() if isinstance(value, (list, np.ndarray))]):
        raise ValueError("All lists should have the same length")

    specs_list = [
        {key: value[i] if isinstance(value, (list, np.ndarray)) else value for key, value in specs.items()}
        for i in range(max_len)
    ]

    objects = [func(**spec) for spec in specs_list]
    return objects

def offsetting(
        com: gf.Component,
        layer_from: LayerLevel,
        layer_to: LayerLevel,
        offset: float=5,
        dilation: float=0
    ) -> gf.Component:
    """
    Generate an offset between two layers. This should always be called after a complete construction
    of a layer.

    Args:
        com [gf.Component]: gf.Component: component to be offset
        layer_from [LayerLevel]: LayerLevel: layer to be offset from
        layer_to [LayerLevel]: LayerLevel: layer to be offset to
        offset [float]: float: offset value in um
    """
    polygons = com.get_polygons()[layer_from]

    # for polygon in polygons:
    region = gf.kdb.Region(polygons)
    region = region.sized(offset*1E+03 + dilation)
    region = region.sized(dilation)
    com.add_polygon(region, layer=layer_to)

    return com