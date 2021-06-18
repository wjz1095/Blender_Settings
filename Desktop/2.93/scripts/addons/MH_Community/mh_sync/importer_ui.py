#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from ..util import checkMakeSkinAvailable, LEAST_REQUIRED_MAKESKIN_VERSION

overridePresets = []
overridePresets.append( ("DEFAULT", "Default", "(re)load the default settings", 1) )
overridePresets.append( ("MAKETARGET", "MakeTarget", "Load optimal settings for MakeTarget", 2) )
overridePresets.append( ("MAKECLOTHES", "MakeClothes", "Load optimal settings for MakeClothes", 3) )

handleHelperItems = []
handleHelperItems.append( ("MASK", "Mask", "Mask helper geometry", 1) )
handleHelperItems.append( ("NOTHING", "Don't modify", "Leave helper geometry as is", 2) )
handleHelperItems.append( ("DELETE", "Delete", "Delete helper geometry", 3))

scaleModeItems = []
scaleModeItems.append( ("METER", "Meter", "1 BU = 1 Meter", 1) )
scaleModeItems.append( ("DECIMETER", "Decimeter", "1 BU = 1 Decimeter", 2) )
scaleModeItems.append( ("CENTIMETER", "Centimeter", "1 BU = 1 Centimeter", 3) )

importProxyItems = []
importProxyItems.append( ("BODY", "Only import body", "Only import the base mesh body", 1) )
importProxyItems.append( ("BODYPARTS", "Body + bodyparts", "Only import the body and body parts such as eyes and hair", 2) )
importProxyItems.append( ("EVERYTHING", "Body, parts, clothes", "Import everything", 3) )

handleMaterialsItems = []
handleMaterialsItems.append( ("CREATENEW", "Create new", "Create a new material with a different name", 1) )
handleMaterialsItems.append( ("REUSE", "Use existing", "Use the existing material as it is", 2) )
handleMaterialsItems.append( ("OVERWRITE", "Overwrite", "Overwrite the existing material", 3) )

handleHiddenItems = []
handleHiddenItems.append( ("NOTHING", "Leave as is", "Do not do anything specific concerning hidden surfaces", 1) )
handleHiddenItems.append( ("MASK", "Mask", "Add a mask modifier to hide hidden surfaces", 2) )
handleHiddenItems.append( ("MATERIAL", "Invis material", "Add an invisible material to hidden surfaces", 3) )
handleHiddenItems.append( ("DELETE", "Delete", "Delete vertices for hidden surfaces", 4) )

from .presets import loadOrCreateDefaultSettings

_EVALUATED_MAKESKIN = False
_MAKESKIN_AVAILABLE = False

def registerImporterConstantsAndSettings():
    # Properties for human importer

    settings = loadOrCreateDefaultSettings()

    bpy.types.Scene.MhGeneralPreset = bpy.props.EnumProperty(items=overridePresets, name="handle_presents", description="If you plan on using MakeClothes or MakeTarget with the imported toon, you can load appropriate settings here", default="DEFAULT")

    bpy.types.Scene.MhHandleHelper = bpy.props.EnumProperty(items=handleHelperItems, name="handle_helper", description="How to handle helpers (such as clothes helper geometry and joint cubes)", default=settings["MhHandleHelper"])
    bpy.types.Scene.MhScaleMode = bpy.props.EnumProperty(items=scaleModeItems, name="Scale mode", description="How long in real world terms is a blender unit?", default=settings["MhScaleMode"])
    bpy.types.Scene.MhDetailedHelpers = BoolProperty(name="Detailed helper groups", description="Create one vertex group per helper part. This is usually superfluous unless you want to work with MakeTarget or MakeClothes", default=settings["MhDetailedHelpers"])
    bpy.types.Scene.MhAddSimpleMaterials = BoolProperty(name="Simple Materials for Helpers", description="Add simple Materials to Helpers", default=settings["MhAddSimpleMaterials"])

    bpy.types.Scene.MhImportWhat = bpy.props.EnumProperty(items=importProxyItems, name="Import what", description="What to import", default=settings["MhImportWhat"])
    bpy.types.Scene.MhPrefixProxy = BoolProperty(name="Prefix proxy names", description="Give all extra meshes (such as hair, clothes..) names that start with the name of the imported toon", default=settings["MhPrefixProxy"])
    bpy.types.Scene.MhMaskBase = BoolProperty(name="Mask base mesh if proxy available", description="If both the base mesh and a body proxy have been imported, then mask the base mesh.", default=settings["MhMaskBase"])
    bpy.types.Scene.MhAddSubdiv = BoolProperty(name="Add a subdivision", description="Add subdivision modifiers to all imported meshes", default=settings["MhAddSubdiv"])

    bpy.types.Scene.MhHandleMaterials = bpy.props.EnumProperty(items=handleMaterialsItems, name="When material exists", description="What to do if a material with the same name already exists", default=settings["MhHandleMaterials"])
    bpy.types.Scene.MhMaterialObjectName = BoolProperty(name="Name material after object", description="When creating a material, give it a name based on what mesh object it belongs to.", default=settings["MhMaterialObjectName"])
    bpy.types.Scene.MhPrefixMaterial = BoolProperty(name="Prefix material names", description="Give all materials a name that starts with the name of the imported toon", default=settings["MhPrefixMaterial"])
    bpy.types.Scene.MhFixRoughness = BoolProperty(name="Fix bad roughness", description="If a material is stated as having a roughness value of < 0.1, assume that this is an error and set to 0.5 instead.", default=settings["MhFixRoughness"])

    bpy.types.Scene.MhHiddenFaces = bpy.props.EnumProperty(items=handleHiddenItems, name="Handle hidden faces", description="What to do about faces (on the body and/or the body proxy) which are hidden behind clothes.", default=settings["MhHiddenFaces"])

    bpy.types.Scene.MhImportRig = BoolProperty(name="Import rig", description="Import the rig if it is set in MH", default=settings["MhImportRig"])
    bpy.types.Scene.MhRigBody = BoolProperty(name="Rig body and bodyparts", description="Use the imported rig as a skeleton for rigging the body and body parts such as eyes and hair", default=settings["MhRigBody"])
    bpy.types.Scene.MhRigClothes = BoolProperty(name="Rig clothes", description="Use the imported rig as a skeleton for rigging clothes", default=settings["MhRigClothes"])
    bpy.types.Scene.MhRigIsParent = BoolProperty(name="Use rig as parent", description="Use the rig as parent for all imported / created objects", default=settings["MhRigIsParent"])

    bpy.types.Scene.MhAdjustPosition = BoolProperty(name="Place feet on ground", description="Move the toon after import so that feet are on ground (z = 0.0). This is not to be confused with the feet on ground option inside MH.", default=settings["MhAdjustPosition"])
    bpy.types.Scene.MhAddCollection = BoolProperty(name='Create collection from name', description='Create a collection from model\'s name and add all objects to the collection on import', default=settings["MhAddCollection"])
    bpy.types.Scene.MhSubCollection = BoolProperty(name='Collections as children', description='New collections are created as children to the currently active collection. NOTICE: this will also force-show the current collection.', default=settings["MhSubCollection"])
    bpy.types.Scene.MhHost = StringProperty(name='Host Address', description='Set Host Adress To Connect With MakeHuman', default=settings["MhHost"])
    bpy.types.Scene.MhPort = IntProperty(name='Port Number', description='Set Port Number To Connect With MakeHuman', default=settings["MhPort"])

    # bpy.types.Scene.MhHandIK = BoolProperty(name="Hand IK", description="Create hand IK controls", default=False)
    # bpy.types.Scene.MhFootIK = BoolProperty(name="Foot IK", description="Create foot IK controls", default=False)
    # bpy.types.Scene.MhHideFK = BoolProperty(name="Hide FK", description="Hide FK bones that are part of an IK chain", default=True)

    bpy.types.Object.MhProxyName = StringProperty(name="Proxy name", description="This is what the proxy is called in MakeHuman", default="")
    bpy.types.Object.MhProxyUUID = StringProperty(name="Proxy UUID", description="This is the UUID of the proxy in MakeHuman", default="")
    bpy.types.Object.MhObjectType = StringProperty(name="Object type", description="This is what type of MakeHuman object this is (such as Clothes, Eyes...)", default="")

    bpy.types.Scene.MhEnhancedSkin = BoolProperty(name="Enhanced skin", description="Create enhanced skin node setup (rather than normal material)", default=settings["MhEnhancedSkin"])
    bpy.types.Scene.MhEnhancedSSS = BoolProperty(name="Enhanced skin SSS", description="When using enhanced skin, also add nodes for SSS", default=settings["MhEnhancedSSS"])
    bpy.types.Scene.MhUseMakeSkin = BoolProperty(name="Use MakeSkin to import material",
                                                 description="MakeSkin has a much more competent material importer than the one available in MPFB. By checking this, you will use MakeSkin to import materials when possible. This will be ignored for skin materials if you checked \"Enhanced skin\" above.",
                                                 default=settings["MhUseMakeSkin"])
    bpy.types.Scene.MhOnlyBlendMat = BoolProperty(name="Only use attached blend material",
                                                 description="MakeSkin is capable of importing entire attached blender materials. The default is to import both the mhmat model and the attached blend material. If checking this box, only the attached material will be imported (if available). This will be ignored for skin materials if you checked \"Enhanced skin\" above.",
                                                 default=settings["MhOnlyBlendMat"])
    bpy.types.Scene.MhExtraGroups = BoolProperty(name="Extra vertex groups", description="Attempt to assign additional vertex groups for body parts, such as lips, fingernails, ears and so on. This works on the base mesh and most (but not all) proxies.", default=settings["MhExtraGroups"])
    bpy.types.Scene.MhExtraSlots = BoolProperty(name="Extra material slots", description="When having assigned extra vertex groups, also create copies of the skin material and assign to separate material slots. This is useful if you for example want a different roughness on the fingernails than on the skin.", default=settings["MhExtraSlots"])

    # In case MHX2 isn't loaded
    bpy.types.Object.MhHuman = BoolProperty(default=False)
    bpy.types.Object.MhScaleFactor = FloatProperty(default=0.1)

    # TODO: hidden faces                MhHiddenFaces
    # TODO: Rig body and parts          MhRigBody
    # TODO: Rig clothes                 MhRigClothes
    # TODO: Use rig as parent           MhRigIsParent

def addImporterSettingsToTab(layout, scn):

    presetBox = layout.box()
    presetBox.label(text="Presets", icon="MODIFIER")
    presetBox.prop(scn, 'MhGeneralPreset', text="")
    presetBox.operator("mh_community.load_preset", text="Load")
    presetBox.operator("mh_community.save_preset", text="Save")

    meshBox = layout.box()
    meshBox.label(text="Mesh settings", icon="MESH_DATA")

    meshBox.label(text="What to import")
    meshBox.prop(scn, 'MhImportWhat', text="")
    meshBox.prop(scn, 'MhPrefixProxy', text="Prefix object name with toon")
    meshBox.prop(scn, 'MhMaskBase', text="Mask body when there is a proxy")
    meshBox.prop(scn, 'MhAddSubdiv', text="Add subdiv modifier")

    helperBox = layout.box()
    helperBox.label(text="Helper settings", icon="VPAINT_HLT")
    helperBox.label(text="How to handle helpers")
    helperBox.prop(scn, 'MhHandleHelper', text="")
    helperBox.prop(scn, 'MhDetailedHelpers', text="Detailed helper groups")
    if scn.MhDetailedHelpers:
        helperBox.prop(scn, 'MhAddSimpleMaterials', text="Simple Materials for Helpers")

    #importHumanBox.separator()
    #importHumanBox.label(text="Body hidden faces:")
    #importHumanBox.prop(scn, 'MhHiddenFaces', text="")

    materialsBox = layout.box()
    materialsBox.label(text="Materials", icon="MATERIAL_DATA")
    materialsBox.label(text="When a material exists...")
    materialsBox.prop(scn, 'MhHandleMaterials', text="")
    materialsBox.prop(scn, 'MhMaterialObjectName', text="Name after object")
    materialsBox.prop(scn, 'MhPrefixMaterial', text="Prefix material name with toon")
    materialsBox.prop(scn, 'MhFixRoughness', text="Fix bad roughness")

    rigBox = layout.box()
    rigBox.label(text="Rig / posing:", icon="ARMATURE_DATA")
    rigBox.prop(scn, 'MhImportRig', text="Import rig")
    #importHumanBox.prop(scn, 'MhRigBody', text="Rig body + parts")
    #importHumanBox.prop(scn, 'MhRigClothes', text="Rig clothes")
    rigBox.prop(scn, 'MhRigIsParent', text="Use rig as parent")

    # importHumanBox.prop(scn, 'MhHandIK', text="Hand IK")
    # importHumanBox.prop(scn, 'MhFootIK', text="Foot IK")
    # importHumanBox.prop(scn, 'MhHideFK', text="Hide FK")

    variousBox = layout.box()
    variousBox.label(text="Various", icon="HAND")
    variousBox.prop(scn, 'MhAdjustPosition', text="Place feet on ground")
    variousBox.prop(scn, 'MhAddCollection', text='Create collection from Name')
    variousBox.prop(scn, 'MhSubCollection', text='Collections as children')
    variousBox.separator()
    variousBox.label(text="Blender unit equals:")
    variousBox.prop(scn, 'MhScaleMode', text="")

    extrasBox = layout.box()
    extrasBox.label(text="Extras", icon="OUTLINER_OB_LIGHT")
    extrasBox.prop(scn, 'MhEnhancedSkin', text='Enhanced skin material')
    extrasBox.prop(scn, 'MhEnhancedSSS', text='Enhanced skin SSS')
    extrasBox.prop(scn, 'MhExtraGroups', text='Extra vertex groups')
    extrasBox.prop(scn, 'MhExtraSlots', text='Slots for extra groups')

    global _EVALUATED_MAKESKIN
    global _MAKESKIN_AVAILABLE

    if not _EVALUATED_MAKESKIN:
        ms = checkMakeSkinAvailable()
        if ms:
            from makeskin import MAKESKIN_VERSION
            if MAKESKIN_VERSION >= LEAST_REQUIRED_MAKESKIN_VERSION:
                _MAKESKIN_AVAILABLE = True
                print("A useful version of MakeSkin is available")
            else:
                print("MakeSkin is available, but in a too old version. At least " + str(LEAST_REQUIRED_MAKESKIN_VERSION) + " is required. Not showing related options.")
        else:
            print("MakeSkin is not available or not enabled. Not showing related options.")
        _EVALUATED_MAKESKIN = True

    if _MAKESKIN_AVAILABLE:
        extrasBox.prop(scn, 'MhUseMakeSkin', text='Use MakeSkin')
        extrasBox.prop(scn, 'MhOnlyBlendMat', text='Only blend mat')

    connectionBox = layout.box()
    connectionBox.label(text="Connect to MH", icon="LINKED")
    connectionBox.label(text="Host :")
    connectionBox.prop(scn, 'MhHost', text="")
    connectionBox.label(text="Port :")
    connectionBox.prop(scn, 'MhPort', text="")

def addImporterUIToTab(layout, scn):

    importHumanBox = layout.box()
    importHumanBox.label(text="Import human", icon="MESH_DATA")
    importHumanBox.operator("mh_community.import_body", text="Import human")


