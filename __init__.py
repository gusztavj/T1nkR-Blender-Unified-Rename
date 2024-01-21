# T1nk-R's Unified Rename add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# This module is responsible for managing add-on and settings lifecycle.
#
# Module and add-on authored by T1nk-R (https://github.com/gusztavj/)
#
# PURPOSE & USAGE *****************************************************************************************************************
# You can use this add-on to get a single panel to batch rename collections, objects and object data in Blender's Outliner
# using text or regex-based search and replace.
#
# Help, support, updates and anything else: https://github.com/gusztavj/Custom-Object-Property-Manager
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
#   * This add-on is intended to change the name of your Blender objects, collections and data blocks belonging to objects.
#   * This add-on is not intended to modify your objects and other Blender assets in any other way.
#   * You shall be able to simply undo consequences made by this add-on.
#
# You may learn more about legal matters on page https://github.com/gusztavj/Custom-Object-Property-Manager
#
# *********************************************************************************************************************************

bl_info = {
    "name": "T1nk-R Collection Renamer",
    "author": "GusJ",
    "version": (1, 0, 0),
    "blender": (2, 91, 0),
    "location": "Edit",
    "description": "Rename your collections",
    "category": "User Interface",
    "doc_url": "Yet to come, till that just drop a mail to Gus at na.mondhatod@gmail.com",
}

if "bpy" in locals():
    from importlib import reload
    reload(rename)
    del reload

import bpy
from . import rename

# Store keymaps here to access after registration
addon_keymaps = []

# Register menu item  "Export Compilations to Trainz" under File > Export  
def menuItem(self, context):
    self.layout.operator(rename.T1NKER_OT_RenameCollection.bl_idname)

# Class registry
classes = [
    rename.T1nkerRenameCollectionAddonSettings, 
    rename.T1nkerRenameCollectionAddonPreferences, 
    rename.T1NKER_OT_RenameCollection
]

# Register the plugin
def register():
    
    # Make sure to avoid double registration
    unregister()
    
    # Register classes
    for c in classes:
        bpy.utils.register_class(c)
    
    # Add menu command to File > Export
    bpy.types.TOPBAR_MT_edit.append(menuItem)
    bpy.types.OUTLINER_MT_context_menu.append(menuItem)

    # Set CTRL+SHIFT+Y as shortcut
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Outliner', space_type='OUTLINER')
        kmi = km.keymap_items.new(rename.T1NKER_OT_RenameCollection.bl_idname, 'F2', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

# Unregister the plugin
def unregister():

    # Put in try since we perform this as a preliminary cleanup of leftover stuff during registration    
    try:
        # Unregister key mapping
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        # Unregister classes (in reverse order)
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        # Delete menu item
        bpy.types.TOPBAR_MT_file_export.remove(menuItem)
    except:
        pass

# Let you run registration without installing. You'll find the command in Edit menu
if __name__ == "__main__":
    register()
