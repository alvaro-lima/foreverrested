# Native quest window style

The quest frame uses the supplied Map & Quest Log, Professions and Character window screenshot as its visual reference: opaque charcoal/brown surfaces, native thin metal borders, inset sections, a centered gold title, square native buttons and the red/gold close control. Existing subtle alternating rows and font settings remain in place.

Inspected Forever UI source at `70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e`:

- `Blizzard_SharedXML/Mainline/NineSliceLayouts.lua`: `SimplePanelTemplate` metal border and `InsetFrameTemplate` inset border.
- `Blizzard_SharedXML/NineSlice.lua`: `GetLayout` and `ApplyLayoutByName`.
- `Blizzard_SharedXML/Mainline/SharedUIPanelTemplates.xml`: native rock background, shared panel and inset templates.
- `Blizzard_UIPanels_Game/Camelot/CharacterFrame.xml` and `Blizzard_Professions/Camelot/Blizzard_ProfessionsFrame.xml`: Forever-specific frame structure.

Source paths show shared definitions, not an assumption that all Mainline APIs exist in Forever. At runtime, the addon requires the actual layout, every referenced atlas and the native NineSlice template before applying it. The fallback uses the Blizzard tooltip border confirmed in installed Leatrix. `Interface/FrameGeneral/UI-Background-Rock` is also referenced by installed Auctionator. A solid dark underlay covers transparent texture pixels.

No source/artwork from another addon is copied or required. No art paths are synthesized. Exact appearance requires checking the running client after `/reload`.
