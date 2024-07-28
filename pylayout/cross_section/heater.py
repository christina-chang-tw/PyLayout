from gdsfactory.typings import LayerSpec, LayerSpecs, Floats
from gdsfactory.cross_section import Section, cross_section

def _heater(
    width: float = 0.45,
    width_slab: float = 7.0,
    width_heater: float = 1.0,
    layer: LayerSpec = "WG",
    layer_slab: LayerSpec = "SLAB90",
    layer_heater: LayerSpec = None,
    port_names: tuple[str, str] = ("o1", "o2"),
    sections: tuple[Section, ...] | None = None,
    slab_inset: float | None = None,
    cladding_layers: LayerSpecs | None = None,
    cladding_offsets: Floats | None = None,
    cladding_simplify: Floats | None = None,
    **kwargs,
):
    slab_insets = (slab_inset,) * 2 if slab_inset else None

    slab = Section(width=width_slab, offset=0, layer=layer_slab, insets=slab_insets)

    sections = list(sections or [])
    sections += [slab]

    heater = Section(
        name="HEATER",
        width=width_heater,
        offset=0,
        layer=layer_heater,
        port_types=("electrical", "electrical"),
        port_names=("e1", "e2"),
    )
    sections.append(heater)

    return cross_section(
        width=width,
        offset=0,
        layer=layer,
        port_names=port_names,
        sections=tuple(sections),
        cladding_offsets=cladding_offsets,
        cladding_layers=cladding_layers,
        cladding_simplify=cladding_simplify,
        **kwargs,
    )