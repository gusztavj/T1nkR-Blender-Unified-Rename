
import bpy
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, AddonPreferences, PropertyGroup

# Addon settings for add-on preferences
class T1nkerRenameCollectionAddonSettings(PropertyGroup):
    isRegex: BoolProperty(
        name="Use regex", 
        description="Click if you want to use regular expressions",
        default=False
    )

    findWhat: StringProperty(
        name="Find what", 
        description="Text to find to replace"
    )
    
    replaceWith: StringProperty(
        name="Replace with", 
        description="Text to use as the replacement"
    )

    includeObjects: BoolProperty(
        name="Include objects", 
        description="Perform replacement on objects",
        default=True
    )

    includeCollections: BoolProperty(
        name="Include collections", 
        description="Perform replacement on collections",
        default=True
    )

    isTestOnly: BoolProperty(
        name="Just a test", 
        description="Just list replacements, but don't actually change anything",
        default=False
    )

class T1nkerRenameCollectionAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    
    settings : PointerProperty(type=T1nkerRenameCollectionAddonSettings)

    # Display addon preferences ===================================================================================================
    def draw(self, context):
             
        layout = self.layout
        layout.label(text="Default settings")                
        layout.prop(self.settings, "isRegex")        
        layout.prop(self.settings, "includeObjects")        
        layout.prop(self.settings, "includeCollections")        


# Main export operator class
class T1NKER_OT_RenameCollection(Operator):    
    """Export object compilations for Trainz"""
    bl_idname = "t1nker.renamecollection"
    bl_label = "Rename collections"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Operator settings
    settings : T1nkerRenameCollectionAddonSettings = None        

    # Constructor =================================================================================================================
    def __init__(self):
        self.settings = None
    
    # See if the operation can run ================================================================================================
    @classmethod
    def poll(cls, context):
        return True

    # Draw operator to show export settings during invoke =========================================================================
    def draw(self, context):        
        layout = self.layout        
        layout.prop(self.settings, "isRegex")
        layout.prop(self.settings, "findWhat")
        layout.prop(self.settings, "replaceWith")
        layout.prop(self.settings, "includeObjects")        
        layout.prop(self.settings, "includeCollections")      
        layout.prop(self.settings, "isTestOnly")  

    # Show the dialog ======================================================================================================
    def invoke(self, context, event):                
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            self.settings = context.preferences.addons[__package__].preferences.settings
 
        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
        
        return result

    # Return the Outliner ==================================================================================================
    # From: https://github.com/K-410/blender-scripts/blob/master/2.8/toggle_hide.py / space_outliner
    def _getSpaceOutliner():
        """Get the outliner. If context area is outliner, return it."""
        context = bpy.context
        if context.area.type == 'OUTLINER':
            return context.space_data
        for w in context.window_manager.windows:
            for a in w.screen.areas:
                if a.type == 'OUTLINER':
                    return a.spaces.active
   
    def _performFindAndReplace(self, object):
        if self.settings.isRegex:
            replacement = re.sub(string = object.name, pattern = self.settings.findWhat, repl = self.settings.replaceWith)
            if object.name == replacement:
                print(f"* '{object.name}' is not affected")
            else:
                print(f"* '{object.name}' --> '{replacement}'")

            if not self.settings.isTestOnly:
                object.name = re.sub(string = object.name, pattern = self.settings.findWhat, repl = self.settings.replaceWith)                    
        else:                    
            replacement = object.name.replace(self.settings.findWhat, self.settings.replaceWith)
            if object.name == replacement:
                print(f"* '{object.name}' is not affected")
            else:
                print(f"* '{object.name}' --> '{replacement}'")
            if not self.settings.isTestOnly:
                object.name = replacement
        return object


    # Here is the core stuff ======================================================================================================
    def execute(self, context):              
        
        collections = [i for i in bpy.context.selected_ids if isinstance(i, bpy.types.Collection)]
        objects = [i for i in bpy.context.selected_ids if isinstance(i, bpy.types.Object)]

        if self.settings.includeCollections:
            for collectionElement in collections:
                collection: bpy.types.Collection = collectionElement
                self._performFindAndReplace(collection)

        if self.settings.includeObjects:
            for objectElement in objects:
                object: bpy.types.Object = objectElement
                self._performFindAndReplace(object)   
                                            
        return {'FINISHED'}
    

