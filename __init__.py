# T1nk-R's Unified Rename add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# This module is responsible for managing add-on and settings lifecycle.
#
# Module and add-on authored by T1nk-R (https://github.com/gusztavj/)
#
# PURPOSE & USAGE *****************************************************************************************************************
# You can use this add-on to get a single panel to batch rename collections and objects shown in Blender's Outliner
# using text or regex-based search and replace.
#
# Help, support, updates and anything else: https://github.com/gusztavj/T1nkR-Blender-Unified-Rename
#
# COPYRIGHT ***********************************************************************************************************************
# Creative Commons CC BY-NC-SA:
#       This license enables re-users to distribute, remix, adapt, and build upon the material in any medium 
#       or format for noncommercial purposes only, and only so long as attribution is given to the creator. 
#       If you remix, adapt, or build upon the material, you must license the modified material under 
#       identical terms. CC BY-NC-SA includes the following elements:
#           BY: credit must be given to the creator.
#           NC: Only noncommercial uses of the work are permitted.
#           SA: Adaptations must be shared under the same terms.
#
#       Credit text:
#           Original addon created by: T1nk-R - janvari.gusztav@imprestige.biz
#
#       For commercial use, please contact me via janvari.gusztav@imprestige.biz. Don't be scared of
#       rigid contracts and high prices, above all I just want to know if this work is of your interest,
#       and discuss options for commercial support and other services you may need.
#
#
# Version: Please see the version tag under bl_info below.
#
# DISCLAIMER **********************************************************************************************************************
# This add-on is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen:
#   * This add-on is intended to change the name of your Blender objects and collections matching the criteria you specify.
#   * This add-on is not intended to modify your objects and other Blender assets in any other way.
#   * You shall be able to simply undo consequences made by this add-on.
#
# You may learn more about legal matters on page https://github.com/gusztavj/T1nkR-Blender-Unified-Rename
#
# *********************************************************************************************************************************

# Blender add-on identification ===================================================================================================
bl_info = {
    "name": "T1nk-R Ultimate Rename (T1nk-R Utilities)",
    "author": "T1nk-R (GusJ)",
    "version": (1, 0, 0),
    "blender": (2, 91, 0),
    "location": "Outliner > Context menu, Outliner > Context menu of objects and collections",
    "description": "Rename collections and objects in one go, using plain text or regex. Open from Edit menu or hit CTRL+SHIFT+F2 in Outliner.",
    "category": "Object",
    "doc_url": "https://github.com/gusztavj/T1nkR-Blender-Unified-Rename",
}

# Lifecycle management ============================================================================================================

# Reload the main module to make sure it's up to date
if "bpy" in locals():
    from importlib import reload
    reload(rename)
    del reload

import bpy
from . import rename

# Properties ======================================================================================================================


addon_keymaps = []
"""
Store keymaps here to access after registration.
"""

classes = [
    rename.T1nkerUltimateRenameAddonSettings, 
    rename.T1nkerUltimateRenameAddonPreferences, 
    rename.T1NKER_OT_UltimateRename
]
"""
List of classes requiring registration and unregistration.
"""


        
# Public functions ================================================================================================================

# Register menu item --------------------------------------------------------------------------------------------------------------
def menuItem(self, context):
    """
    Add a menu item
    """
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(rename.T1NKER_OT_UltimateRename.bl_idname)

# Register the plugin -------------------------------------------------------------------------------------------------------------
def register():
    """
    Perform registration of the add-on when being enabled.
    """
    
    # Make sure to avoid double registration
    unregister()
    
    # Register classes
    for c in classes:
        bpy.utils.register_class(c)
    
    # Add menu command to the context menu of the Outliner editor space
    bpy.types.OUTLINER_MT_context_menu.append(menuItem)
    bpy.types.OUTLINER_MT_collection.append(menuItem)
    bpy.types.OUTLINER_MT_object.append(menuItem)
    

    # Configure hotkey
    #
    
    wm = bpy.context.window_manager

    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    
    if kc: # Blender runs with GUI
        # The hotkey will only be available when the mouse is within an Outliner
        km = wm.keyconfigs.addon.keymaps.new(name='Outliner', space_type='OUTLINER')
        
        kmi = km.keymap_items.new(rename.T1NKER_OT_UltimateRename.bl_idname, 'F2', 'PRESS', ctrl=True, shift=True)
        
        addon_keymaps.append((km, kmi))

# Unregister the plugin -----------------------------------------------------------------------------------------------------------
def unregister():

    # Put in try since we perform this as a preliminary cleanup of leftover stuff during registration,
    # and it may be normal that unregistering something simply does not work without being registered first.
    try:
        # Unregister key mapping
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
            
        addon_keymaps.clear()

        # Unregister classes (in reverse order)
        for c in reversed(classes):
            try:
                bpy.utils.unregister_class(c)
            except:
                # Don't panic, it was probably not registered
                pass
        
        # Delete menu items in separate try blocks so if one fails others may still be attempted to be removed
        try:
            bpy.types.OUTLINER_MT_context_menu.remove(menuItem)
        except:
            pass
        try:
            bpy.types.OUTLINER_MT_collection.remove(menuItem)
        except:
            pass
        try:
            bpy.types.OUTLINER_MT_object.remove(menuItem)
        except:
            pass
    except:
        # Keep walking silently
        pass

# Developer mode ##################################################################################################################

# Lets you run registration without installing. 
if __name__ == "__main__":
    register()
