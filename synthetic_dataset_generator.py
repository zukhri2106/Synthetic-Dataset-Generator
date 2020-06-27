import bpy
import os
import random
import datetime

# constant
CAMERA_HEIGHT = 15

# configuration
NUM_ITERATION = 1
MAX_CLASSES_PER_IMAGE = 5
MAX_OBJECTS_PER_CLASSES = 2

# Paths
ROOT_DIR = 'I:/synthetic data generator'
MASK_DIR = ROOT_DIR + '/annotations'
IMAGE_DIR = ROOT_DIR + '/images'
BG_DIR = ROOT_DIR + '/backgrounds'
CLASS_DIR = ROOT_DIR + '/categories'

def setup_nodes():
    nodes = []
    tree = scene.node_tree
    for node in tree.nodes:
        tree.nodes.remove(node)

    # adding nodes
    renderlayer_node = tree.nodes.new(type='CompositorNodeRLayers') # render layes node
    composite_node = tree.nodes.new(type='CompositorNodeComposite') # composite node    
    alphaover_node = tree.nodes.new(type='CompositorNodeAlphaOver') # alpha over node
    image_node = tree.nodes.new(type='CompositorNodeImage')         # image node
    scale_node = tree.nodes.new(type='CompositorNodeScale')         # scale node
    idmask_node = tree.nodes.new(type='CompositorNodeIDMask')       # ID Mask node
    
    nodes.append(image_node)
    nodes.append(alphaover_node)
    nodes.append(idmask_node)
    nodes.append(composite_node)
    
    scale_node.space = 'RENDER_SIZE'
    
    # link nodes
    links = tree.links  
    
    # link for image
    links.new(image_node.outputs[0], scale_node.inputs[0])
    links.new(scale_node.outputs[0], alphaover_node.inputs[1])
    links.new(renderlayer_node.outputs[0], alphaover_node.inputs[2]) 
    links.new(renderlayer_node.outputs[14], idmask_node.inputs[0])
    
    return links, nodes

def create_image(mode, camera, links, nodes, filename, background=None, list_of_objects=None): 
    links = links
    nodes = nodes
    
    scene.camera = camera
    if mode == 'IMAGE':
        links.new(nodes[1].outputs[0], nodes[3].inputs[0]) 
        image = bpy.data.images.load(BG_DIR + '/' + background)
        bg = cam.data.background_images.new()
        bg.image = image
        nodes[0].image = bpy.data.images[background]   
                
        scene.render.filepath = IMAGE_DIR + '/' + filename
        bpy.ops.render.render(write_still=True) # save rendered image
        
    elif mode == 'MASK':

        
        # link for annotations

        links.new(nodes[2].outputs[0], nodes[3].inputs[0])
        
        index = 0
        if list_of_objects is not None:
            for object in list_of_objects:
                nodes[2].index = index+1
                # save rendered annotation
                scene.render.filepath = MASK_DIR + '/' + filename + '_' + object + '_' + str(index)
                bpy.ops.render.render(write_still=True)
                index += 1
        
def rescale_object(object):
    # the number given is relative to the grid
    # grid of rendered image: width=10, height=6
    if object == 'Akkuschrauber':
        bpy.context.object.scale[0] = 0.7
        bpy.context.object.scale[1] = 0.7
    elif object == 'Cityroller':
        bpy.context.object.scale[0] = 2.5
        bpy.context.object.scale[1] = 2.5
    elif object == 'Door.013':
        bpy.context.object.scale[0] = 3.5
        bpy.context.object.scale[1] = 3.5
    elif object == 'Elektrischer_Hubwagen':
        bpy.context.object.scale[0] = 4.76
        bpy.context.object.scale[1] = 4.76
    elif object == 'Europalette':
        bpy.context.object.scale[0] = 2.3
        bpy.context.object.scale[1] = 2.3
    elif object == 'Hammer_LP':
        bpy.context.object.scale[0] = 0.7
        bpy.context.object.scale[1] = 0.7
    elif object == 'Karton':
        bpy.context.object.scale[0] = 2
        bpy.context.object.scale[1] = 2
    elif object == 'Laptop_Genauer':
        bpy.context.object.scale[0] = 1.2
        bpy.context.object.scale[1] = 1.2
    elif object == 'Mensch':
        bpy.context.object.scale[0] = 3.5
        bpy.context.object.scale[1] = 3.5
    elif object == 'Rollregal':
        bpy.context.object.scale[0] = 3.5
        bpy.context.object.scale[1] = 3.5
    elif object == 'Rollwagen_Lang':
        bpy.context.object.scale[0] = 2.5
        bpy.context.object.scale[1] = 2.5
    elif object == 'shelf02':
        bpy.context.object.scale[0] = 3.5
        bpy.context.object.scale[1] = 3.5
    elif object == 'Stuhl_Mit_Rollen':
        bpy.context.object.scale[0] = 2
        bpy.context.object.scale[1] = 2
    

if __name__=='__main__':
    print("start")
    bpy.ops.object.select_all(action='SELECT')  # select all objects
    bpy.ops.object.delete(use_global=True)     # delete all objects
    
    #remove datablocks
    for datablock in bpy.data.meshes:
        if datablock.users == 0:
            bpy.data.meshes.remove(datablock)
            
    # add camera to scene
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, 0, CAMERA_HEIGHT), rotation=(0, 0, 0))
    # add sun to the scene
    #bpy.ops.object.light_add(type='SUN', radius=1, location=(0, 1, 5))
    
    # declare some obj
    scene = bpy.context.scene
    cam = bpy.data.objects['Camera']
    #sun = bpy.data.objects['Sun']
    
    # configuration
    scene.use_nodes = True  # enable use node
    scene.render.film_transparent = True    # enable film transparent
    cam.data.show_background_images = True  # enable show bg image

    scene.world.light_settings.use_ambient_occlusion = True
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.view_layers["View Layer"].use_pass_object_index = True 

    links, nodes = setup_nodes()   
    
    backgrounds = next(os.walk(BG_DIR))[2]
    classes = next(os.walk(CLASS_DIR))[1]

    image_idx = 1000
    for background in backgrounds:
        for i in range(NUM_ITERATION):
            annotation_id = 0
            z_location = 0 
            list_of_objects = []       
            objects = random.sample(classes, random.randint(3, MAX_CLASSES_PER_IMAGE))
            
            # Deselect all
            bpy.ops.object.select_all(action='DESELECT')
            # clear everything except Camera
            for plane in bpy.data.objects:
                if plane.name != 'Camera':
                    bpy.data.objects[plane.name].select_set(True)
                    
            bpy.ops.object.delete()
                    
            for object in objects:
                items = next(os.walk(CLASS_DIR+'/'+object))[2]
                selected_items = random.sample(items, random.randint(1, MAX_OBJECTS_PER_CLASSES))
                for selected_item in selected_items:
                    list_of_objects.append(object)
                    # import image as plane
                    bpy.ops.import_image.to_plane(files=[{"name":selected_item, "name":selected_item}], directory=CLASS_DIR+'/'+object, align_axis='Z+', relative=False)
                    rescale_object(object)
                    # relocate image randomly
                    bpy.context.object.location[0] = random.randint(-100,100)/20
                    bpy.context.object.location[1] = random.randint(-20,20)/10
                    bpy.context.object.location[2] = z_location
                    
                    # assign index for every object
                    bpy.context.object.pass_index = annotation_id + 1
                
                    z_location += 0.001                    
                    annotation_id += 1
            
            create_image ('MASK', cam, links, nodes, str(image_idx), list_of_objects=list_of_objects)
            create_image('IMAGE', cam, links, nodes, str(image_idx), background=background)
            image_idx += 1
        
    print("done")
