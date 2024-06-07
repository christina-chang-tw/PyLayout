import gdsfactory as gf
from typing import List

class Methods:
    """
    Class for storing methods that can be used for manipulating components.
    """
    @staticmethod
    def connect(
        com1: gf.ComponentReference,
        port1: list,
        com2: gf.ComponentReference,
        port2: list
    ):
        """
        Connect two components with the given ports

        Args:
            com1 [gf.ComponentReference]: this component will be moved
            port1 [list]: list: list of ports of component 1
            com2 [gf.ComponentReference]: gf.ComponentReference: component 2
            port2 [list]: list: list of ports of component 2

            * The position of the ports in the list should be the same.
        """
        for p1, p2 in zip(port1, port2):
            com1.connect(p1, com2.ports[p2])


    @staticmethod
    def add_ports(
        com1: gf.Component,
        names: list,
        com2: gf.Component,
        ports: list
    ):
        """
        Add ports to com1 component from com2 component

        Args:
            com1 [gf.Component]: gf.Component: component 1
            names [list]: list: list of names for the ports
            com2 [gf.Component]: gf.Component: component 2
            ports [list]: list: list of ports of component 2
        """
        for name, port in zip(names, ports):
            com1.add_port(name=name, port=com2.ports[port])
    
    @staticmethod
    def symmetry(
        com: gf.Component,
        com1: gf.Component, # coponent to be symmetrized
        name: str=None,
        *,
        p1: float=None,
        p2: float=None,
        xport: str=None,
        x0: float=None,
        yport: str=None,
        y0: float=None
    ) -> gf.ComponentReference:
        """
        Symmetry the component com1 with respect to the x0

        Args:
            com [gf.Component]: gf.Component: component to add the symmetrized component
            com1 [gf.Component]: gf.Component: component to be symmetrized
            p1 [float]: float: first point for the mirror line
            p2 [float]: float: second point for the mirror line
            xport [str]: str: port name for the mirror line
            x0 [float]: float: x coordinate for the mirror line
            yport [str]: str: port name for the mirror line
            y0 [float]: float: y coordinate for the mirror line
        
        Returns:
            gf.ComponentReference: reference to the symmetrized component
        """
        name = name if name is not None else f"{com1.name}_copy"
        com2 = com1.copy(name=name)
        com2_ref = com.add_ref(com2)
        if p1 is not None and p2 is not None:
            com2_ref.mirror(p1, p2)
        if x0 is not None or xport is not None:
            com2_ref.mirror_x(x0=x0, port_name=xport)
        if y0 is not None or yport is not None:
            com2_ref.mirror_y(y0=y0, port_name=yport)

        return com2, com2_ref

    @staticmethod
    def gen_copies(
        com: gf.Component,
        number: int,
        names: List[str]=None,
    ):
        """
        Generate copies of a component

        Args:
            com [gf.Component]: gf.Component: component to be copied
            number [int]: int: number of copies to be generated
            names [List[str]]: List[str]: list of names for the copies

        Returns:
            List[gf.ComponentReference]: list of references to the copied components
        """
        names = names if names is not None else [f"{com.name}_{i}" for i in range(number)]
        copies = [com.copy(name=name) for name in names]
        return copies


    @staticmethod
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
        max_len = max([len(value) for value in specs.values() if isinstance(value, list)], default=1)
        if any([len(value) != max_len for value in specs.values() if isinstance(value, list)]):
            raise ValueError("All lists should have the same length")

        specs_list = [
            {key: value[i] if isinstance(value, list) else value for key, value in specs.items()}
            for i in range(max_len)
        ]

        objects = [func(**spec) for spec in specs_list]

        return objects
