from gdsfactory.cross_section import cross_section, CrossSection
from gdsfactory.cross_section import Section, LayerSpec, Floats, LayerSpecs

def _pn(
    width: float = 0.45,
    layer: LayerSpec = "WG",
    layer_slab: LayerSpec = "SLAB90",
    gap_medium_doping: float | None = 0.5,
    gap_medium_to_via: float | None = 0.5,
    gap_metal_to_via: float | None = 0.5,
    offset_low_doping: float | None = 0.0,
    width_low_doping: float = 12.1,
    width_slab: float = 8.8,
    layer_p: LayerSpec | None = None,
    layer_pp: LayerSpec | None = None,
    layer_n: LayerSpec | None = None,
    layer_np: LayerSpec | None = None,
    layer_via: LayerSpec | None = None,
    width_via: float = 1.0,
    layer_metal: LayerSpec | None = None,
    layer_heater: LayerSpec | None = None,
    layer_heater_pad: LayerSpec | None = None,
    width_heater: float = 1.0,
    port_names: tuple[str, str] = ("o1", "o2"),
    sections: tuple[Section, ...] | None = None,
    cladding_layers: LayerSpecs | None = None,
    cladding_offsets: Floats | None = None,
    cladding_simplify: Floats | None = None,
    slab_inset: float | None = None,
    via_min_distance: float | None = None,
    **kwargs,
) -> CrossSection:
    """Rib PN doped cross_section.

    Args:
        width: width of the ridge in um.
        layer: ridge layer.
        layer_slab: slab layer.
        gap_low_doping: from waveguide center to low doping. Only used for PIN.
        gap_medium_doping: from waveguide center to medium doping. None removes it.
        gap_high_doping: from center to high doping. None removes it.
        offset_low_doping: from center to junction center.
        width_doping: in um.
        width_slab: in um.
        layer_p: p doping layer.
        layer_pp: p+ doping layer.
        layer_ppp: p++ doping layer.
        layer_n: n doping layer.
        layer_np: n+ doping layer.
        layer_npp: n++ doping layer.
        layer_via: via layer.
        width_via: via width in um.
        layer_metal: metal layer.
        width_metal: metal width in um.
        port_names: input and output port names.
        sections: optional list of sections.
        cladding_layers: optional list of cladding layers.
        cladding_offsets: optional list of cladding offsets.
        cladding_simplify: Optional Tolerance value for the simplification algorithm. \
                All points that can be removed without changing the resulting\
                polygon by more than the value listed here will be removed.
        slab_inset: slab inset in um.
        kwargs: cross_section settings.

    .. code::

                              offset_low_doping
                                <------>
                               |       |
                              wg     junction
                            center   center
                               |       |
                 ______________|_______|______
                 |             |       |     |
        _________|             |       |     |_________________|
              P                |       |               N       |
          width_p              |       |            width_n    |
        <----------------------------->|<--------------------->|
                               |               |       N+      |
                               |               |    width_n    |
                               |               |<------------->|
                               |<------------->|
                               gap_medium_doping

    .. plot::
        :include-source:

        import gdsfactory as gf

        xs = gf.cross_section.pn_cs(width=0.5)
        p = gf.path.arc(radius=10, angle=45)
        c = p.extrude(xs)
        c.plot()
    """
    slab_insets = (slab_inset,) * 2 if slab_inset else None

    slab = Section(width=width_slab, offset=0, layer=layer_slab, insets=slab_insets)

    sections = list(sections or [])
    sections += [slab]

    if gap_medium_doping is not None:
        medium_inside_r = gap_medium_doping
        medium_outside_r = gap_medium_doping + gap_medium_to_via + width_via + 0.5 # 0.5 is the min gap between via and medium doped
        if layer_heater:
            medium_outside_r = max(medium_outside_r, width_heater/2 + via_min_distance + + width_via + 0.5)
        offset_medium_doping = (medium_inside_r + medium_outside_r)/2
        width_medium_doping = medium_outside_r - medium_inside_r

        if layer_np is not None:
            np = Section(
                name="NP",
                width=width_medium_doping,
                offset=-offset_medium_doping - offset_low_doping,
                layer=layer_np,
            )
            sections.append(np)
        if layer_pp is not None:
            pp = Section(
                name="PP",
                width=width_medium_doping,
                offset=offset_medium_doping - offset_low_doping,
                layer=layer_pp,
            )
            sections.append(pp)

    if layer_n:
        width = width_medium_doping + gap_medium_doping + 2
        if layer_via:
            width = max(width, gap_medium_doping + gap_medium_to_via + width_via + 2)
        if layer_heater:
            width = max(width, width_heater/2 + via_min_distance + width_via + 2)
        n = Section(
            name="N",
            width=width,
            offset=-width/2-offset_low_doping,
            layer=layer_n,
        )
        sections.append(n)

    # for cornerstone operation, low doped p must overlap low dose n -> need to double checked with Dave
    if layer_p:
        p = Section(
            name="P",
            width=width_low_doping + gap_medium_doping,
            offset=(width_low_doping-gap_medium_doping)/2-offset_low_doping,
            layer=layer_p,
        )
        sections.append(p)

    if layer_via is not None:
        offset_via = gap_medium_doping + gap_medium_to_via + width_via / 2
        if layer_heater:
            offset_via = max(offset_via, width_heater/2 + via_min_distance + width_via / 2)
        via_top = Section(
            name="VIA_TOP",
            width=width_via,
            offset=offset_via - offset_low_doping,
            layer=layer_via
        )
        via_bot = Section(
            name="VIA_BOT",
            width=width_via,
            offset=-offset_via - offset_low_doping,
            layer=layer_via
        )
        sections.append(via_top)
        sections.append(via_bot)

    if layer_metal is not None:
        metal_inside_r = offset_via - width_via/2 - gap_metal_to_via
        metal_outside_r = offset_via + width_via/2 + gap_metal_to_via
        offset_metal = (metal_inside_r + metal_outside_r)/2
        width_metal = metal_outside_r - metal_inside_r

        port_types = ("electrical", "electrical")
        metal_top = Section(
            name="METAL_TOP",
            width=width_metal,
            offset=offset_metal-offset_low_doping,
            layer=layer_metal,
            port_types=port_types,
            port_names=("e1_bot", "e2_bot"),
        )
        metal_bot = Section(
            name="METAL_BOT",
            width=width_metal,
            offset=-offset_metal-offset_low_doping,
            layer=layer_metal,
            port_types=port_types,
            port_names=("e1_bot", "e2_bot"),
        )
        sections.append(metal_top)
        sections.append(metal_bot)

    if layer_heater is not None:
        port_types = ("electrical", "electrical")
        heater = Section(
            name="HEATER",
            width=width_heater,
            offset=0,
            layer=layer_heater,
            port_types=port_types,
            port_names=("e1", "e2"),
        )
        sections.append(heater)

    if layer_heater_pad is not None:
        heater_metal = Section(
            name="HEATER_METAL",
            width=width_heater,
            offset=0,
            layer=layer_heater_pad,
            port_types=port_types,
            port_names=("e1", "e2"),
        )
        sections.append(heater_metal)

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