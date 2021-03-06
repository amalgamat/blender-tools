# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMI# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org/>

import bpy
import bmesh
import os
import bpy_extras
import bpy_extras.io_utils
import mathutils
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        path_reference_mode,
        )


def f2str(value):
    return "%.5f"%value

def writeVector3d(file,vector):
        file.write("[");        
        file.write(f2str(vector.x))
        file.write(",")
        file.write(f2str(vector.y))
        file.write(",")
        file.write(f2str(vector.z))
        file.write("]")            
def writeVector2d(file,vector):
        file.write("[");
        file.write(f2str(vector.x))
        file.write(",")
        file.write(f2str(vector.y))         
        file.write("]")
def writeColor(file,color):
        file.write("[");        
        file.write(f2str(color.r))
        file.write(",")
        file.write(f2str(color.g))
        file.write(",")
        file.write(f2str(color.b))
        file.write("]")            
def sameVectors(na,nb):
        coeff = na*nb/(na.length*nb.length)
        return coeff > 0.999     

# keyVertexList 3 indices in P only list
# uniqueVertexList - uniqueVertexList in PUNT list (unique combination)
def add2AdjancedDictionary(keyVertexList,uniqueVertexList,adjancedDict):
        adjKey = (keyVertexList[0],keyVertexList[1])
        if adjKey not in adjancedDict:
            adjancedDict[adjKey] = uniqueVertexList[2]
        adjKey = (keyVertexList[1],keyVertexList[2])
        if adjKey not in adjancedDict:
            adjancedDict[adjKey] = uniqueVertexList[0]            
        adjKey = (keyVertexList[2],keyVertexList[0])
        if adjKey not in adjancedDict:
            adjancedDict[adjKey] = uniqueVertexList[1]
    
# uniqueFaceVertexList - face  "unique vertex" indices
# adjancedDisct - dictionary keyed by "position only" vertex indices
# uniqe2ponly - dictionar - unique to postion only index
def getAindAdjancedVertices(uniqueFaceVertexList,adjancedDict,uniqe2ponly):
        ponly = []
        result = []
        for unique in uniqueFaceVertexList:
            ponly.append(uniqe2ponly[unique])
        adjKey = (ponly[0],ponly[2])    # adjanced traingles have reversed order of indices
        if adjKey not in adjancedDict:
            result.append(None)
        else:
            result.append(adjancedDict[adjKey]) 
        adjKey = (ponly[2],ponly[1])    # adjanced traingles have reversed order of indices
        if adjKey not in adjancedDict:
            result.append(None)
        else:
            result.append(adjancedDict[adjKey])
        adjKey = (ponly[1],ponly[0])    # adjanced traingles have reversed order of indices
        if adjKey not in adjancedDict:
            result.append(None)
        else:
            result.append(adjancedDict[adjKey])
        return result

class VertexData:
    def __init__(self):
        self.Position = None
        self.Tangents = []
        self.Normals = []
        self.UVs = []        
    def addToList(value,list2Mod):
        if value in list2Mod:
            return list2Mod.index(value)
        else:
            list2Mod.append(value)
            return list2Mod.index(value)
    def addTangent(self,value):
            return VertexData.addToList(value,self.Tangents)
    def addNormal(self,value):
            return VertexData.addToList(value,self.Normals)
    def addUV(self,value):
            return VertexData.addToList(value,self.UVs)
    def formatFloat(self,value):
            return "%.5f".value
    def writeUniqueVertex(self,file,uvIndex,normalIndex,tangentIndex):
            file.write("VERTEX_PUNT: ")
            writeVector3d(file,self.Position)
            writeVector2d(file,self.UVs[uvIndex])
            writeVector3d(file,self.Normals[normalIndex])
            writeVector3d(file,self.Tangents[tangentIndex])
            file.write("\n")
            file.write("VERTEX_AVG_N: ")
            writeVector3d(file,self.AvgN)
            file.write("\n")
    def calcAvgVal(self):
            self.AvgN = mathutils.Vector()
            uniqueNormals = []
            for nN in self.Normals:
                found = False
                for uN in uniqueNormals:
                    if sameVectors(nN,uN):
                        found = True
                        break
                if not found:
                    uniqueNormals.append(nN)
            for cN in uniqueNormals:
                self.AvgN += cN
            self.AvgN /= self.AvgN.length
 
     
def writeAIN(file,srcdir,dstdir):
    file.write("AIN_FILE: V0.0-0\n")    
    file.write("# lines beginning with # are comments\n")
    file.write("# empty lines are ignored\n")
    file.write("# all other begin with line type id token(word) followed by : and space\n")
    file.write("# all tokens with _NAME ending mark begin of new context - new image, mesh or texture\n")
    file.write("# list of context starting tokens\n")
    file.write("# MATER_NAME - material id (referenced in meshes)\n")
    file.write("# MESH_NAME - mesh name\n")
    file.write("# list of normal data fields\n")
    file.write("# IMG_COUNT - number of image paths defined in file\n") 
    file.write("# MATER_COUNT - number of materials defined in file\n")
    file.write("# MESH_COUNT - number of meshes defined in file\n")
    file.write("#           _COUNT lines always appear before corresponding data blocks\n")
    file.write("# IMG_PATH - path to image source\n")
    file.write("# MATER_AMBIENT MATER_DIFFUSE_COLOR MATER_DIFFUSE_INTENSITY MATER_SPECULAR_COLOR MATER_SPECULAR_INTENSITY MATER_EMIT - generic material parameters\n")
    file.write("# MATER_TEX_AMBIENT - ambient texture image - index of image (index base 0 ) from IMAGES section\n")
    file.write("# MATER_TEX_DIFFUSE - diffuse texture image\n")
    file.write("# MATER_TEX_SPECULAR_COL - speculat color texture image\n")
    file.write("# MATER_TEX_NORMAL - normal texture image\n")
    file.write("# MATER_TEX_EMISSION - emission texture\n")
    file.write("# MESH_VERTEX_COUNT - number of vertices in current mesh (for easier lodaing)\n")
    file.write("# MESH_FACE_COUNT - number of faces in current mesh\n")
    file.write("# MESH_MATER_COUNT - number of materials used in current mesh\n")
    file.write("# MESH_MATER - material index\n")
    file.write("# VERTEX_PUNT - vertex definition in form [position][uv][normal][tangent]\n")
    file.write("# VERTEX_AVG_N - additional averaged normal for generation of shadow volume\n")
    file.write("# FACE3 - triangular face definioniton in format [index of v0, index of v1, index of v2]\n")
    file.write("# ADJANCED3 - indices of vertexes 'adjanced' to face - if 'N' if there is no adjanced vertex\n")
    file.write("#====================== IMAGES =====================\n")
    img2index = {}
    count=0
    for img in bpy.data.images:
        if img.filepath != "":
            count = count + 1
    file.write("IMG_COUNT: ")
    file.write(str(count))
    file.write("\n")
    count = 0
    for img in bpy.data.images:
        if img.filepath != "":
            file.write("IMG_PATH: ")
            filepath = bpy_extras.io_utils.path_reference(img.filepath, srcdir, dstdir, mode='ABSOLUTE', copy_subdir='', copy_set=None, library=None)
            file.write(filepath)
            file.write("\n")
            img2index[img.name]=count
            count=count + 1
    file.write("#====================== MATERIALS =====================\n")
    file.write("MATER_COUNT: ")
    file.write(str(len(bpy.data.materials)))
    file.write("\n")
    mater2index = {}
    count = 0
    for mater in bpy.data.materials:
        mater2index[mater.name] = count
        count = count + 1
        file.write("MATER_NAME: ")
        file.write(mater.name)        
        file.write("\n")
        file.write("MATER_AMBIENT: ")
        file.write(f2str(mater.ambient))
        file.write("\n")    
        file.write("MATER_DIFFUSE_COLOR: ")
        writeColor(file,mater.diffuse_color)
        file.write("\n")
        file.write("MATER_DIFFUSE_INTENSITY: ")
        file.write(f2str(mater.diffuse_intensity))
        file.write("\n")    
        file.write("MATER_SPECULAR_COLOR: ")
        writeColor(file,mater.specular_color)
        file.write("\n")
        file.write("MATER_SPECULAR_INTENSITY: ")
        file.write(f2str(mater.specular_intensity))
        file.write("\n")
        file.write("MATER_EMIT: ")
        file.write(f2str(mater.emit))
        file.write("\n")          
        for texslot in mater.texture_slots:
            if texslot != None:
                texture = bpy.data.textures[texslot.name]
                if hasattr(texture,'image'):
                    if texture.image.name in img2index:
                        imgIdx = str(img2index[texture.image.name])
                        if texslot.use_map_ambient:
                            file.write("MATER_TEX_AMBIENT: ")
                            file.write(imgIdx)
                            file.write("\n")
                        if texslot.use_map_emit:
                            file.write("MATER_TEX_EMISSION: ")
                            file.write(imgIdx)
                            file.write("\n")                            
                        elif texslot.use_map_color_diffuse: # blender requires that "emission" texture influences both color and emission
                            file.write("MATER_TEX_DIFFUSE: ")
                            file.write(imgIdx)
                            file.write("\n")
                        if texslot.use_map_color_spec:
                            file.write("MATER_TEX_SPECULAR_COL: ")
                            file.write(imgIdx)
                            file.write("\n")
                        if texslot.use_map_normal:
                            file.write("MATER_TEX_NORMAL: ")
                            file.write(imgIdx)
                            file.write("\n")
    file.write("#====================== MESHES =====================\n")
    # "selected only"
    #me = bpy.context.active_object.to_mesh(bpy.context.scene,apply_modifiers=True,settings="RENDER")
    #me.name = bpy.context.active_object.name
    #bm = bmesh.new()
    #bm.from_mesh(me)
    #bmesh.ops.triangulate(bm,faces=bm.faces)
    #bm.to_mesh(me)
    #bm.free()
    # collect all meshes in project
    meshes = []
    for obj in bpy.data.objects:
        try:
            me = obj.to_mesh(bpy.context.scene,apply_modifiers=True,settings="RENDER")
        except RuntimeError:
            continue # no mesh data in this object
        if len(me.uv_layers) == 0:
            print("Mesh ",me.name," has no UV coordinates")
            continue 
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm,faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.name = obj.name
        meshes.append(me)
    file.write("MESH_COUNT: ")
    file.write(str(len(meshes)))
    file.write("\n");
    for me in meshes:
        uvlist = me.uv_layers[0].data[:] # copy data to separate table - for some reason orginal table will be overwritten with normals?
        me.calc_tangents()
        vertices = {}
        faces = {} # key is material ID
        adjancedDict = {} # key id tuple of vertex indices (3 entries from every triangle)
        unique2ponly = {}
        unique_vertices = []
        for face in me.polygons:
            face_indices = []
            ponly_vertices = []
            for loopIdx in face.loop_indices:
                vert = me.loops[loopIdx]
                uv = uvlist[loopIdx].uv
                if vert.vertex_index in vertices:
                    vdata = vertices[vert.vertex_index]
                else:
                    vdata = VertexData()
                    vdata.Position = me.vertices[vert.vertex_index].co
                    vertices[vert.vertex_index] = vdata
                ti = vdata.addTangent(vert.tangent)
                ni = vdata.addNormal(vert.normal)
                uvi = vdata.addUV(uv)
                unique_vi = (vert.vertex_index,uvi,ni,ti)
                if unique_vi not in unique_vertices:
                    unique_vertices.append(unique_vi)
                face_indices.append(unique_vertices.index(unique_vi))
                unique2ponly[unique_vertices.index(unique_vi)] = vert.vertex_index
                ponly_vertices.append(vert.vertex_index)
            material_name=me.materials[face.material_index].name
            global_material_index=mater2index[material_name]
            if global_material_index not in faces:
                faces[global_material_index] = []
            faces[global_material_index].append(face_indices)
            add2AdjancedDictionary(ponly_vertices,face_indices,adjancedDict)
        for vert in vertices.values():
            vert.calcAvgVal()
        # save data
        file.write("MESH_NAME: ")
        file.write(me.name)
        file.write("\n")
        file.write("MESH_VERTEX_COUNT: ")
        file.write(str(len(unique_vertices)))
        file.write("\n")
        file.write("MESH_FACE_COUNT: ")
        file.write(str(len(faces)))
        file.write("\n")
        file.write("MESH_MATER_COUNT: ")
        file.write(str(len(me.materials)))
        file.write("\n")
        for uvi in unique_vertices:
            vdata = vertices[uvi[0]]
            vdata.writeUniqueVertex(file,uvi[1],uvi[2],uvi[3])
        for material_id in faces.keys():
            file.write("MESH_MATER: ")
            file.write(str(material_id))
            file.write("\n")
            for face in faces[material_id]:
                file.write("FACE3: ")
                file.write("[")
                file.write(str(face[0]))
                file.write(",")
                file.write(str(face[1]))
                file.write(",")
                file.write(str(face[2]))
                file.write("]\n")
                file.write("ADJANCED3: ")
                adjVert = getAindAdjancedVertices(face,adjancedDict,unique2ponly)
                file.write("[")
                if adjVert[0] == None:
                    file.write("N")
                else:
                    file.write(str(adjVert[0]))
                file.write(",")
                if adjVert[1] == None:
                    file.write("N")
                else:
                    file.write(str(adjVert[1]))
                file.write(",")
                if adjVert[2] == None:
                    file.write("N")
                else:
                    file.write(str(adjVert[2]))
                file.write("]\n")     
            # debug
            #for face in faces[material_id]: 
            #    file.write("FACE3PO: ")
            #    for uvi in face:
            #        writeVector3d(file,vertices[unique_vertices[uvi][0]].Position)
            #    file.write("\n")
            #    file.write("ADJANCEDPO: ")
            #    adjVert = getAindAdjancedVertices(face,adjancedDict,unique2ponly)
            #    for uvi in adjVert:
            #        if uvi == None:
            #            file.write("[-,-,-]")
            #        else:
            #            writeVector3d(file,vertices[unique_vertices[uvi][0]].Position)
            #    file.write("\n")
            file.write("\n")
        # remove temporary object
        bpy.data.meshes.remove(me)
    
    
bl_info = {
    "name": "AllINeed AIN format",
    "author": "Grzegorz Domagala",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Export AIN",
    "warning": "",
    "wiki_url": "",
    "support": 'OFFICIAL',
    "category": "Import-Export"}


    
class ExportAIN(bpy.types.Operator, ExportHelper):
    """ Save AIN file """

    bl_idname = "export_scene.ain"
    bl_label = "Export AIN"
    bl_options = {'PRESET'}
    
    filename_ext = ".ain"
    filer_glob = StringProperty(
        default="*.ain",
        options={'HIDDEN'},
        )
    path_mode = path_reference_mode
    check_extension = True
    
    def execute(self,context):
        keywords = self.as_keywords()    
        file = open(keywords["filepath"],"w")    
        srcdir = os.path.dirname(bpy.data.filepath)
        dstdir = os.path.dirname(keywords["filepath"])
        writeAIN(file,srcdir,dstdir)
        file.close()
        return {'FINISHED'}
    
def menu_func_export_ain(self,context):
    self.layout.operator(ExportAIN.bl_idname, text = "All I Need (.ain)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export_ain)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_ain)
    
if __name__ == "__main__":
    register()
TED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org/>

import bpy
import bmesh
import os
import bpy_extras
import bpy_extras.io_utils
import mathutils
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        path_reference_mode,
        )


def f2str(value):
    return "%.5f"%value

def writeVector3d(file,vector):
        file.write("[");        
        file.write(f2str(vector.x))
        file.write(",")
        file.write(f2str(vector.y))
        file.write(",")
        file.write(f2str(vector.z))
        file.write("]")            
def writeVector2d(file,vector):
        file.write("[");
        file.write(f2str(vector.x))
        file.write(",")
        file.write(f2str(vector.y))         
        file.write("]")
def writeColor(file,color):
        file.write("[");        
        file.write(f2str(color.r))
        file.write(",")
        file.write(f2str(color.g))
        file.write(",")
        file.write(f2str(color.b))
        file.write("]")            
def sameVectors(na,nb):
        coeff = na*nb/(na.length*nb.length)
        return coeff > 0.999     

# keyVertexList 3 indices in P only list
# uniqueVertexList - uniqueVertexList in PUNT list (unique combination)
def add2AdjancedDictionary(keyVertexList,uniqueVertexList,adjancedDict):
        adjKey = (keyVertexList[0],keyVertexList[1])
        if adjKey not in adjancedDict:
            adjancedDict[adjKey] = uniqueVertexList[2]
        adjKey = (keyVertexList[1],keyVertexList[2])
        if adjKey not in adjancedDict:
            adjancedDict[adjKey] = uniqueVertexList[0]            
        adjKey = (keyVertexList[2],keyVertexList[0])
        if adjKey not in adjancedDict:
            adjancedDict[adjKey] = uniqueVertexList[1]
    
# uniqueFaceVertexList - face  "unique vertex" indices
# adjancedDisct - dictionary keyed by "position only" vertex indices
# uniqe2ponly - dictionar - unique to postion only index
def getAindAdjancedVertices(uniqueFaceVertexList,adjancedDict,uniqe2ponly):
        ponly = []
        result = []
        for unique in uniqueFaceVertexList:
            ponly.append(uniqe2ponly[unique])
        adjKey = (ponly[0],ponly[2])    # adjanced traingles have reversed order of indices
        if adjKey not in adjancedDict:
            result.append(None)
        else:
            result.append(adjancedDict[adjKey]) 
        adjKey = (ponly[2],ponly[1])    # adjanced traingles have reversed order of indices
        if adjKey not in adjancedDict:
            result.append(None)
        else:
            result.append(adjancedDict[adjKey])
        adjKey = (ponly[1],ponly[0])    # adjanced traingles have reversed order of indices
        if adjKey not in adjancedDict:
            result.append(None)
        else:
            result.append(adjancedDict[adjKey])
        return result

class VertexData:
    def __init__(self):
        self.Position = None
        self.Tangents = []
        self.Normals = []
        self.UVs = []        
    def addToList(value,list2Mod):
        if value in list2Mod:
            return list2Mod.index(value)
        else:
            list2Mod.append(value)
            return list2Mod.index(value)
    def addTangent(self,value):
            return VertexData.addToList(value,self.Tangents)
    def addNormal(self,value):
            return VertexData.addToList(value,self.Normals)
    def addUV(self,value):
            return VertexData.addToList(value,self.UVs)
    def formatFloat(self,value):
            return "%.5f".value
    def writeUniqueVertex(self,file,uvIndex,normalIndex,tangentIndex):
            file.write("VERTEX_PUNT: ")
            writeVector3d(file,self.Position)
            writeVector2d(file,self.UVs[uvIndex])
            writeVector3d(file,self.Normals[normalIndex])
            writeVector3d(file,self.Tangents[tangentIndex])
            file.write("\n")
            file.write("VERTEX_AVG_N: ")
            writeVector3d(file,self.AvgN)
            file.write("\n")
    def calcAvgVal(self):
            self.AvgN = mathutils.Vector()
            uniqueNormals = []
            for nN in self.Normals:
                found = False
                for uN in uniqueNormals:
                    if sameVectors(nN,uN):
                        found = True
                        break
                if not found:
                    uniqueNormals.append(nN)
            for cN in uniqueNormals:
                self.AvgN += cN
            self.AvgN /= self.AvgN.length
 
     
def writeAIN(file,srcdir,dstdir):
    file.write("AIN_FILE: V0.0-0\n")    
    file.write("# lines beginning with # are comments\n")
    file.write("# empty lines are ignored\n")
    file.write("# all other begin with line type id token(word) followed by : and space\n")
    file.write("# all tokens with _NAME ending mark begin of new context - new image, mesh or texture\n")
    file.write("# list of context starting tokens\n")
    file.write("# MATER_NAME - material id (referenced in meshes)\n")
    file.write("# MESH_NAME - mesh name\n")
    file.write("# list of normal data fields\n")
    file.write("# IMG_COUNT - number of image paths defined in file\n") 
    file.write("# MATER_COUNT - number of materials defined in file\n")
    file.write("# MESH_COUNT - number of meshes defined in file\n")
    file.write("#           _COUNT lines always appear before corresponding data blocks\n")
    file.write("# IMG_PATH - path to image source\n")
    file.write("# MATER_AMBIENT MATER_DIFFUSE_COLOR MATER_DIFFUSE_INTENSITY MATER_SPECULAR_COLOR MATER_SPECULAR_INTENSITY MATER_EMIT - generic material parameters\n")
    file.write("# MATER_TEX_AMBIENT - ambient texture image - index of image (index base 0 ) from IMAGES section\n")
    file.write("# MATER_TEX_DIFFUSE - diffuse texture image\n")
    file.write("# MATER_TEX_SPECULAR_COL - speculat color texture image\n")
    file.write("# MATER_TEX_NORMAL - normal texture image\n")
    file.write("# MESH_VERTEX_COUNT - number of vertices in current mesh (for easier lodaing)\n")
    file.write("# MESH_FACE_COUNT - number of faces in current mesh\n")
    file.write("# MESH_MATER_COUNT - number of materials used in current mesh\n")
    file.write("# MESH_MATER - material index\n")
    file.write("# VERTEX_PUNT - vertex definition in form [position][uv][normal][tangent]\n")
    file.write("# VERTEX_AVG_N - additional averaged normal for generation of shadow volume\n")
    file.write("# FACE3 - triangular face definioniton in format [index of v0, index of v1, index of v2]\n")
    file.write("# ADJANCED3 - indices of vertexes 'adjanced' to face - if 'N' if there is no adjanced vertex\n")
    file.write("#====================== IMAGES =====================\n")
    img2index = {}
    count=0
    for img in bpy.data.images:
        if img.filepath != "":
            count = count + 1
    file.write("IMG_COUNT: ")
    file.write(str(count))
    file.write("\n")
    count = 0
    for img in bpy.data.images:
        if img.filepath != "":
            file.write("IMG_PATH: ")
            filepath = bpy_extras.io_utils.path_reference(img.filepath, srcdir, dstdir, mode='ABSOLUTE', copy_subdir='', copy_set=None, library=None)
            file.write(filepath)
            file.write("\n")
            img2index[img.name]=count
            count=count + 1
    file.write("#====================== MATERIALS =====================\n")
    file.write("MATER_COUNT: ")
    file.write(str(len(bpy.data.materials)))
    file.write("\n")
    mater2index = {}
    count = 0
    for mater in bpy.data.materials:
        mater2index[mater.name] = count
        count = count + 1
        file.write("MATER_NAME: ")
        file.write(mater.name)        
        file.write("\n")
        file.write("MATER_AMBIENT: ")
        file.write(f2str(mater.ambient))
        file.write("\n")    
        file.write("MATER_DIFFUSE_COLOR: ")
        writeColor(file,mater.diffuse_color)
        file.write("\n")
        file.write("MATER_DIFFUSE_INTENSITY: ")
        file.write(f2str(mater.diffuse_intensity))
        file.write("\n")    
        file.write("MATER_SPECULAR_COLOR: ")
        writeColor(file,mater.specular_color)
        file.write("\n")
        file.write("MATER_SPECULAR_INTENSITY: ")
        file.write(f2str(mater.specular_intensity))
        file.write("\n")
        file.write("MATER_EMIT: ")
        file.write(f2str(mater.emit))
        file.write("\n")          
        for texslot in mater.texture_slots:
            if texslot != None:
                texture = bpy.data.textures[texslot.name]
                if hasattr(texture,'image'):
                    if texture.image.name in img2index:
                        imgIdx = str(img2index[texture.image.name])
                        if texslot.use_map_ambient:
                            file.write("MATER_TEX_AMBIENT: ")
                            file.write(imgIdx)
                            file.write("\n")
                        if texslot.use_map_color_diffuse:
                            file.write("MATER_TEX_DIFFUSE: ")
                            file.write(imgIdx)
                            file.write("\n")
                        if texslot.use_map_color_spec:
                            file.write("MATER_TEX_SPECULAR_COL: ")
                            file.write(imgIdx)
                            file.write("\n")
                        if texslot.use_map_normal:
                            file.write("MATER_TEX_NORMAL: ")
                            file.write(imgIdx)
                            file.write("\n")
    file.write("#====================== MESHES =====================\n")
    # "selected only"
    #me = bpy.context.active_object.to_mesh(bpy.context.scene,apply_modifiers=True,settings="RENDER")
    #me.name = bpy.context.active_object.name
    #bm = bmesh.new()
    #bm.from_mesh(me)
    #bmesh.ops.triangulate(bm,faces=bm.faces)
    #bm.to_mesh(me)
    #bm.free()
    # collect all meshes in project
    meshes = []
    for obj in bpy.data.objects:
        try:
            me = obj.to_mesh(bpy.context.scene,apply_modifiers=True,settings="RENDER")
        except RuntimeError:
            continue # no mesh data in this object
        if len(me.uv_layers) == 0:
            print("Mesh ",me.name," has no UV coordinates")
            continue 
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm,faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
        me.name = obj.name
        meshes.append(me)
    file.write("MESH_COUNT: ")
    file.write(str(len(meshes)))
    file.write("\n");
    for me in meshes:
        uvlist = me.uv_layers[0].data[:] # copy data to separate table - for some reason orginal table will be overwritten with normals?
        me.calc_tangents()
        vertices = {}
        faces = {} # key is material ID
        adjancedDict = {} # key id tuple of vertex indices (3 entries from every triangle)
        unique2ponly = {}
        unique_vertices = []
        for face in me.polygons:
            face_indices = []
            ponly_vertices = []
            for loopIdx in face.loop_indices:
                vert = me.loops[loopIdx]
                uv = uvlist[loopIdx].uv                
                if vert.vertex_index in vertices:
                    vdata = vertices[vert.vertex_index]
                else:
                    vdata = VertexData()
                    vdata.Position = me.vertices[vert.vertex_index].co
                    vertices[vert.vertex_index] = vdata
                ti = vdata.addTangent(vert.tangent)
                ni = vdata.addNormal(vert.normal)
                uvi = vdata.addUV(uv)
                unique_vi = (vert.vertex_index,uvi,ni,ti)
                if unique_vi not in unique_vertices:
                    unique_vertices.append(unique_vi)
                face_indices.append(unique_vertices.index(unique_vi))
                unique2ponly[unique_vertices.index(unique_vi)] = vert.vertex_index
                ponly_vertices.append(vert.vertex_index)
            material_name=me.materials[face.material_index].name
            global_material_index=mater2index[material_name]
            if global_material_index not in faces:
                faces[global_material_index] = []
            faces[global_material_index].append(face_indices)
            add2AdjancedDictionary(ponly_vertices,face_indices,adjancedDict)
        for vert in vertices.values():
            vert.calcAvgVal()
        # save data
        file.write("MESH_NAME: ")
        file.write(me.name)
        file.write("\n")
        file.write("MESH_VERTEX_COUNT: ")
        file.write(str(len(unique_vertices)))
        file.write("\n")
        file.write("MESH_FACE_COUNT: ")
        file.write(str(len(faces)))
        file.write("\n")
        file.write("MESH_MATER_COUNT: ")
        file.write(str(len(me.materials)))
        file.write("\n")
        for uvi in unique_vertices:
            vdata = vertices[uvi[0]]
            vdata.writeUniqueVertex(file,uvi[1],uvi[2],uvi[3])
        for material_id in faces.keys():
            file.write("MESH_MATER: ")
            file.write(str(material_id))
            file.write("\n")
            for face in faces[material_id]:
                file.write("FACE3: ")
                file.write("[")
                file.write(str(face[0]))
                file.write(",")
                file.write(str(face[1]))
                file.write(",")
                file.write(str(face[2]))
                file.write("]\n")
                file.write("ADJANCED3: ")
                adjVert = getAindAdjancedVertices(face,adjancedDict,unique2ponly)
                file.write("[")
                if adjVert[0] == None:
                    file.write("N")
                else:
                    file.write(str(adjVert[0]))
                file.write(",")
                if adjVert[1] == None:
                    file.write("N")
                else:
                    file.write(str(adjVert[1]))
                file.write(",")
                if adjVert[2] == None:
                    file.write("N")
                else:
                    file.write(str(adjVert[2]))
                file.write("]\n")     
            # debug
            #for face in faces[material_id]: 
            #    file.write("FACE3PO: ")
            #    for uvi in face:
            #        writeVector3d(file,vertices[unique_vertices[uvi][0]].Position)
            #    file.write("\n")
            #    file.write("ADJANCEDPO: ")
            #    adjVert = getAindAdjancedVertices(face,adjancedDict,unique2ponly)
            #    for uvi in adjVert:
            #        if uvi == None:
            #            file.write("[-,-,-]")
            #        else:
            #            writeVector3d(file,vertices[unique_vertices[uvi][0]].Position)
            #    file.write("\n")
            file.write("\n")
        # remove temporary object
        bpy.data.meshes.remove(me)
    
    
bl_info = {
    "name": "AllINeed AIN format",
    "author": "Grzegorz Domagala",
    "version": (1, 0, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Export AIN",
    "warning": "",
    "wiki_url": "",
    "support": 'OFFICIAL',
    "category": "Import-Export"}


    
class ExportAIN(bpy.types.Operator, ExportHelper):
    """ Save AIN file """

    bl_idname = "export_scene.ain"
    bl_label = "Export AIN"
    bl_options = {'PRESET'}
    
    filename_ext = ".ain"
    filer_glob = StringProperty(
        default="*.ain",
        options={'HIDDEN'},
        )
    path_mode = path_reference_mode
    check_extension = True
    
    def execute(self,context):
        keywords = self.as_keywords()    
        file = open(keywords["filepath"],"w")    
        srcdir = os.path.dirname(bpy.data.filepath)
        dstdir = os.path.dirname(keywords["filepath"])
        writeAIN(file,srcdir,dstdir)
        file.close()
        return {'FINISHED'}
    
def menu_func_export_ain(self,context):
    self.layout.operator(ExportAIN.bl_idname, text = "All I Need (.ain)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export_ain)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_ain)
    
if __name__ == "__main__":
    register()
