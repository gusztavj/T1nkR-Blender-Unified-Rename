# T1nk-R's Unified Rename add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info in __init__.py.
#
# This module is responsible for the UI and the actual processing.
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
# Copyright (c) 2023-2024, T1nk-R (Gusztáv Jánvári)
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

from datetime import datetime
import bpy
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, AddonPreferences, PropertyGroup

from . import updateChecker

# Addon settings for add-on preferences ###########################################################################################
class T1nkerUnifiedRenameAddonSettings(PropertyGroup):
    isRegex: BoolProperty(
        name="Use regex", 
        description="Click if you want to use regular expressions",
        default=False
    )
    """
    `True` if the text in `Find what` and `Replace with` shall be interpreted as regular expressions, `False` otherwise.
    """

    findWhat: StringProperty(
        name="Find what", 
        description="Text to find to replace"
    )
    """
    The text to find or regular expression to match.
    """
    
    replaceWith: StringProperty(
        name="Replace with", 
        description="Text to use as the replacement"
    )
    """
    Replacement text or expression.
    """

    includeObjects: BoolProperty(
        name="Include objects", 
        description="Perform replacement on objects",
        default=True
    )
    """
    Tells if scope shall be extended to objects. If checked (`True`), objects will be renamed if they are included in the scope.
    """

    includeCollections: BoolProperty(
        name="Include collections", 
        description="Perform replacement on collections",        
        default=True
    )
    """
    Tells if scope shall be extended to collections. If checked (`True`), collections will be renamed if they are included in the scope.
    """

    isTestOnly: BoolProperty(
        name="Just a test", 
        description="Just list replacements, but don't actually change anything",
        default=False
    )
    """
    If checked (`True`), nothing will actually be changed. You can learn the effects of your planned changes in the System Console.
    """

# Addon preferences ###############################################################################################################
class T1nkerUnifiedRenameAddonPreferences(AddonPreferences):
    
    # Properties required by Blender ==============================================================================================
    bl_idname = __package__
    """
    Blender's ID name for it to know to which add-on this class belongs. This must match the add-on name, 
    so '__package__' shall be used when defining this in a submodule of a python package.
    """
    
    # Other properties ============================================================================================================
    settings : PointerProperty(type=T1nkerUnifiedRenameAddonSettings)
    """
    Default settings for the add-on.
    """
    
    updateInfo: PointerProperty(type=updateChecker.T1nkerUnifiedRenameUpdateInfo)
    """
    Information about the current version and the latest available
    """

    # Public functions ============================================================================================================

    # Display addon preferences ---------------------------------------------------------------------------------------------------
    def draw(self, context):
        """
        Draws the UI of the add-on preferences (default settings)

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
        """
        
        layout = self.layout
        
        box = layout.box()
        
        layout.label(text="Default settings")                
        layout.prop(self.settings, "isRegex")        
        layout.prop(self.settings, "includeObjects")        
        layout.prop(self.settings, "includeCollections")    
        
        # Update available button
        #
        
        try: # to see if we know anything about updates
            updateInfo = context.preferences.addons[__package__].preferences.updateInfo
            
            # Note that checking update is part of executing the main operator, that is, performing at least
            # one synchronization. Until that no updates will be detected. Updates are not checked each time
            # this dialog is drawn, but as set in `updateInfo.T1nkerUnifiedRenameUpdateInfo.checkFrequencyDays`.
            if updateInfo.updateAvailable:
                # Draw update button and tip
                opUpdate = layout.column().row().operator(
                        'wm.url_open',
                        text=f"Update available",
                        icon='URL'
                        )            
                opUpdate.url = updateChecker.RepoInfo.repoReleasesUrl
                layout.row().label(text=f"You can update from {updateInfo.currentVersion} to {updateInfo.latestVersion}")
        except:
            # Do nothing, if we could not check updates, probably this is the first time of enabling the add-on
            # and corresponding data structures are not yet available.
            pass    
        
        

                
# Main operator class #############################################################################################################
class T1NKER_OT_UnifiedRename(Operator):    
    """
    Rename collections and objects in one go using plain text or regex
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "t1nker.unifiedrename"
    bl_label = "Unified Rename (T1nk-R Utils)"
    bl_options = {'REGISTER', 'UNDO'}    
        
    # Lifecycle management ========================================================================================================
    
    # Initialize object -----------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Make an instance and create a scene-level copy of the settings.
        """
        
        self.settings: T1nkerUnifiedRenameAddonSettings = None
        """
        Copy of the operator settings specific to the Blender file (scene)
        """
    
    # Public functions ============================================================================================================
    
    # See if the operation can run ------------------------------------------------------------------------------------------------
    @classmethod
    def poll(cls, context):
        return True

    # Display UI ------------------------------------------------------------------------------------------------------------------
    def draw(self, context):        
                
        layout = self.layout        
        
        box = layout.box()        
        box.row().label(text="What and how to find and replace")        
        innerBox = box.box()
        
        innerBox.row().prop(self.settings, "isRegex")
        innerBox.row().prop(self.settings, "findWhat")
        innerBox.row().prop(self.settings, "replaceWith")
        
        box = layout.box()
        box.row().label(text="Specify scope")        
        innerBox = box.box()
        
        row = innerBox.row()
        row.label(text="", icon="OUTLINER_OB_MESH")
        row.prop(self.settings, "includeObjects")
        
        row = innerBox.row()
        row.label(text="", icon="OUTLINER_COLLECTION")
        row.prop(self.settings, "includeCollections")
        
        box = layout.box()
        box.row().label(text="Operation mode")        
        innerBox = box.box()        
        innerBox.row().prop(self.settings, "isTestOnly")  
        
        # Update available button
        #
        
        try:
            updateInfo = context.preferences.addons[__package__].preferences.updateInfo
            
            # Note that checking update is part of executing the main operator, that is, performing at least
            # one synchronization. Until that no updates will be detected. Updates are not checked each time
            # this dialog is drawn, but as set in `updateInfo.T1nkerUnifiedRenameUpdateInfo.checkFrequencyDays`.
            if updateInfo.updateAvailable:
                box = layout.box()
                
                row = box.row(align=True)
                
                row.label(text="Update available")
                
                # Update button            
                opUpdate = box.row().operator(
                        'wm.url_open',
                        text=f"Get new version",
                        icon='URL'
                        )            
                opUpdate.url = updateChecker.RepoInfo.repoReleasesUrl
                box.row().label(text=f"You can update from {updateInfo.currentVersion} to {updateInfo.latestVersion}")
        except:
            # Fail silently if we cannot check for updates or draw the UI
            pass    

    # Show the UI -----------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):
        """
        React to invocation by showing the properties dialog.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
            event: The event triggering the operation, as passed on by Blender.

        Returns:
            {'FINISHED'} or {'ERROR'}, indicating success or failure of the operation.
        """
        
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            self.settings = context.preferences.addons[__package__].preferences.settings

        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
        
        return result


    # Perform the operation -------------------------------------------------------------------------------------------------------
    def execute(self, context):          
        """
        Executes the operation.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.

        Returns:
            {'FINISHED'} or {'ERROR'}, indicating success or failure of the operation.
        """
        
        # Call the update checker to check for updates time to time, as specified in 
        # `updateInfo.T1nkerDecoratorUpdateInfo.checkFrequencyDays`
        try:
            bpy.ops.t1nker.unifiedrenameupdatechecker(forceUpdateCheck=True)            
        except:
            # Don't mess up anything if update checking doesn't work, just ignore the error
            pass
        
        operationStarted = f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}"
        
        status = None
        collectionsRenamed = 0
        objectsRenamed = 0
        
        try:
            print("")
            print("")
            print(f"=" * 80)
            print(f"T1nk-R Unified Rename started ({operationStarted})")
            print(f"-" * 80)
            
            print("")
            if self.settings.isTestOnly:
                print(f"Operating in test mode, nothing will actually be changed")
            else:
                print(f"Operating in production mode, names of matching elements will actually be changed")
            print("")
            
            # Check if the find what expression is empty and terminate gracefully if it is
            if len(self.settings.findWhat) == 0:
                raise Exception("No search term is specified, there's nothing to do")
            
            # Check and terminate gracefully if scope is empty
            if not self.settings.includeObjects and not self.settings.includeCollections:
                raise Exception("Empty scope specified. Include at least objects or collections.")
                return {'CANCELLED'}
            
            # Collect selected collections and objects
            collections = [i for i in bpy.context.selected_ids if isinstance(i, bpy.types.Collection)]
            objects = [i for i in bpy.context.selected_ids if isinstance(i, bpy.types.Object)]
            
            # Rename collections if requested
            if self.settings.includeCollections:
                for collectionElement in collections:
                    collection: bpy.types.Collection = collectionElement
                    renamed = self._performFindAndReplace(collection)
                    if renamed:
                        collectionsRenamed = collectionsRenamed + 1

            # Rename objects if requested
            if self.settings.includeObjects:
                for objectElement in objects:
                    object: bpy.types.Object = objectElement
                    renamed = self._performFindAndReplace(object)   
                    if renamed:
                        objectsRenamed = objectsRenamed + 1
            
            status = {'FINISHED'}
        
        except Exception as ex:            
            print(f"{ex}")
            self.report({'ERROR'}, f"{ex}")
            status = {'CANCELLED'}
        
        finally: # Print some summary
            # Leave here instead of moving toward the end of the try block as some things might have been changed
            # even if an error occurred afterwards            
            summary = \
                f"Renamed {objectsRenamed if objectsRenamed > 0 else 'no'} object(s) " + \
                f"and {collectionsRenamed if collectionsRenamed > 0 else 'no'} collections"
                            
            self.report({'INFO'}, summary)
            
            print("")
            print(f"-" * 80)
            print(summary)    
            print(f"-" * 80)
            print(f"T1nk-R Unified Rename finished")                                            
            print(f"=" * 80)
            print("")
        
        return status
    

    # Private functions ===========================================================================================================

    # Return the Outliner ---------------------------------------------------------------------------------------------------------    
    def _getSpaceOutliner():        
        """
        Get the Outliner. If context area is outliner, return it.
        
        Returns: The Outliner object, if there is any.      
        
        """
        
        # Idea from: https://github.com/K-410/blender-scripts/blob/master/2.8/toggle_hide.py / space_outliner
        context = bpy.context
        if context.area.type == 'OUTLINER':
            return context.space_data
        
        for w in context.window_manager.windows:
            for a in w.screen.areas:
                if a.type == 'OUTLINER':
                    return a.spaces.active
                
        # No Outliner area open
        return None

    # Perform the operation -------------------------------------------------------------------------------------------------------
    def _performFindAndReplace(self, item):
        """
        Check if the object received is subject to renaming and perform rename if it is.

        Args:
            object (bpy.types.Object or bpy.types.Collection): The object or collection to rename if matching conditions.

        Returns:
            True if the item was renamed, false if not
        """
        
        renamed = False
        
        if self.settings.isRegex: # treat the find and replace pattern regular expressions
            replacement = re.sub(string = item.name, pattern = self.settings.findWhat, repl = self.settings.replaceWith)
            
            if item.name == replacement:
                if self.settings.isTestOnly:    
                    print(f"* '{item.name}' is not affected")
            else:
                renamed = True
                
                if self.settings.isTestOnly:
                    print(f"* '{item.name}' --> '{replacement}'")

            if not self.settings.isTestOnly:
                item.name = re.sub(string = item.name, pattern = self.settings.findWhat, repl = self.settings.replaceWith)                    
                
        else: # treat the find and replace pattern plain text
            replacement = item.name.replace(self.settings.findWhat, self.settings.replaceWith)
            
            if item.name == replacement:
                if self.settings.isTestOnly:
                    print(f"* '{item.name}' is not affected")
            else:
                renamed = True
                
                if self.settings.isTestOnly:
                    print(f"* '{item.name}' --> '{replacement}'")
                    
            if not self.settings.isTestOnly:
                item.name = replacement
                
        return renamed