# T1nk-R's Unified Rename add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info below.
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
#
# ** MIT License **
# 
# Copyright (c) 2023, T1nk-R (Gusztáv Jánvári)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ** Commercial Use **
# 
# I would highly appreciate to get notified via [janvari.gusztav@imprestige.biz](mailto:janvari.gusztav@imprestige.biz) about 
# any such usage. I would be happy to learn this work is of your interest, and to discuss options for commercial support and 
# other services you may need.
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
    "name": "T1nk-R Unified Rename (T1nk-R Utilities)",
    "author": "T1nk-R (GusJ)",
    "version": (1, 1, 1),
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
    rename.T1nkerUnifiedRenameAddonSettings, 
    rename.T1nkerUnifiedRenameAddonPreferences, 
    rename.T1NKER_OT_UnifiedRename
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
    self.layout.operator(rename.T1NKER_OT_UnifiedRename.bl_idname)

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
        
        kmi = km.keymap_items.new(rename.T1NKER_OT_UnifiedRename.bl_idname, 'F2', 'PRESS', ctrl=True, shift=True)
        
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
