#!/usr/bin/env python3
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Script copyright (C) 2021 Jannik Vogel


#FIXME: Mark processed files in header, so we don't cause people to create garbage FBX tools based on our broken files

BLENDER_FBX_PATH="/usr/share/blender/2.91/scripts/addons/io_scene_fbx/"

import sys
sys.path.insert(0,BLENDER_FBX_PATH)

TMP_PATH_FBX="/tmp/fbx.fbx"

import sys
import shutil
import os

import json2fbx
import fbx2json

import json

import zlib

def uid(name):
  h = zlib.crc32(name.encode('utf-8'))
  assert(h >= 0)
  return h

randomid = 0
def random_uid():
  global randomid
  randomid += 1
  return uid("random%d" % randomid)

# Copy target file to temp
shutil.copyfile(sys.argv[1], TMP_PATH_FBX)

# Convert to JSON
fbx2json.fbx2json(TMP_PATH_FBX)
TMP_PATH_JSON="%s.json" % os.path.splitext(TMP_PATH_FBX)[0]
os.remove(TMP_PATH_FBX) 

# Load JSON
jsonData = open(TMP_PATH_JSON).read()
f = json.loads(jsonData)

# Dump JSON
#print(f)

# Replace Properties60 with Properties70
globalSettings = []
models = []
textures = []
materials = []
def fixup(es, isObject=False, isConnections=False):
  global textures
  global models
  global materials
  global globalSettings
  name, unka, unkb, es = es
  assert(len(unka) == len(unkb))

  if name == "Properties60":
    name = "Properties70"
  if name == "FBXVersion":
    assert(unka == [6100])
    unka = [7100]

  _isTexture = False
  _isModelMesh = False
  _isMaterial = False

  # In PoseNode
  if True:
    if name == "Node":
      assert(len(unka) == 1)
      #FIXME: Is LS also okay? I'd like to preserve the name
      unka = [uid(unka[0])]
      unkb = "L"
    if name == "Matrix":
      unka = [unka]
      unkb = "d"

  # In Deformer
  if True:
    if name == "Indexes":
      unka = [unka]
      unkb = "i"
    if name == "Weights":
      unka = [unka]
      unkb = "d"
    if name == "Transform":
      unka = [unka]
      unkb = "d"
    if name == "TransformLink":
      unka = [unka]
      unkb = "d"
    #FIXME: Blender code also mentions TransformAssociateModel, but does not appear in my 6100 files
    assert(name != "TransformAssociateModel")

  if isObject:

    if name == "Texture":
      _isTexture = True

    if name == "Material":
      _isMaterial = True

    if name != "GlobalSettings":
      unka = [uid(unka[0])] + unka
      unkb = "L" + unkb

    if name == "Model":
      #FIXME: A lot of this should only be done for meshes!

      __unka = unka[:]
      __unkb = unkb[:]

      # Also create geometry for meshes
      if unka[-1] == "Mesh":
        # Fixup name and UID
        __unka[1] = __unka[1].replace("::Model", "::Geometry")
        __unka[0] = uid(__unka[1])

        orig = ["Geometry", __unka, __unkb]

        # Schedule to add geometry to list
        _isModelMesh = True

        # Collect reference to Model and Geometry
        models += [[unka[0], __unka[0]]]
      
      #FIXME: Also do lights?
      elif unka[-1] == "Camera":

        # Fixup name and UID
        __unka[1] = __unka[1].replace("::Model", "::NodeAttribute")
        __unka[0] = uid(__unka[1])

        orig = ["NodeAttribute", __unka, __unkb]

#                ["P", ["FocalLength", "double", "Number", "A", 50.0], "SSSSD", []],
#                ["P", ["FocalLength", "Real", "", "A+", 21.354494094848633], "SSSSD", []],

        # Schedule to add camera to list
        _isModelMesh = True

        # Collect reference to Model and NodeAttribute
        models += [[unka[0], __unka[0]]]

      else:
        # Add model to list
        models += [[unka[0]]]


  #FIXME: If isGeometry
  if True:
    if name == "Vertices":
      unka = [unka]
      unkb = "d"
    if name == "PolygonVertexIndex":
      unka = [unka]
      unkb = "i"
    if name == "Edges":
      unka = [unka]
      unkb = "i"

  #FIXME: If isLayerElementMaterial
  if True:
    if name == "Materials":
      unka = [unka]
      unkb = "i"

  #FIXME: If isLayerElementUV
  if True:
    if name == "UV":
      unka = [unka]
      unkb = "d"
    if name == "UVIndex":
      unka = [unka]
      unkb = "i"

  #FIXME: If isLayerElementSmoothing
  if True:
    if name == "Smoothing":
      unka = [unka]
      unkb = "i"

  #FIXME: If isLayerElementTexture
  if True:
    if name == "TextureAlpha":
      unka = [unka]
      unkb = "d"
    if name == "TextureId":
      unka = [unka]
      unkb = "i"

  #FIXME: If isLayerElementNormal
  if True:
    if name == "Normals":
      unka = [unka]
      unkb = "d"

  #FIXME: If isLayerElementColor
  if True:
    if name == "Colors":
      unka = [unka]
      unkb = "d"
    if name == "ColorIndex":
      unka = [unka]
      unkb = "i"



  if isConnections:
    assert(unkb == "SSS")
    unka = [unka[0], uid(unka[1]), uid(unka[2])]
    unkb = "SLL"

  fes = []
  _isObject = (name == "Objects")
  _isConnections = (name == "Connections")

  # Add all models to connection
  if _isConnections:
    for model in models:
      fes += [["C", ["OO", model[0], 0], "SLL", []]]
    # Link geometrys to models
    for model in models:
      if len(model) >= 2:
        fes += [["C", ["OO", model[1], model[0]], "SLL", []]]
    
  for e in es:
    fes += fixup(e, _isObject, _isConnections)

  # Mark models as processed
  if _isConnections:
    #print("materials\n", materials)
    #print("models\n", models)
    # Collect all materials
    #print("connections\n", fes)
    modelMaterials = {}
    for fe in fes:
      __name, __unka, __unkb, __es = fe
      for material in materials:
        if material == __unka[1]:
          for model in models:
            if model[0] == __unka[2]:
              modelMaterials[__unka[2]] = __unka[1]
    #print(modelMaterials)
    # Recreate connections
    nfes = []
    for fe in fes:
      __name, __unka, __unkb, __es = fe
      for texture in textures:
        #print(unka[2])
        if texture == __unka[1]:
          print("Fixing texture")
          # Replace model by material
          __unka[0] = "OP"
          __unka[-1] = modelMaterials[__unka[-1]]
          __unka += ["DiffuseColor"]
          __unkb += "S"
      nfes += [[__name, __unka, __unkb, __es]]
    #print("\n\n",fes)
    #print("\n\n",nfes)
    fes = nfes
    models = []
  
  if name == "Connect":
    name = "C"

  # Remap properties
  if name == "Property":
    name = "P"
    unkaTypes = {
      "bool": "",
      "double": "Number",
      "Vector3D": "Vector",
      "enum": "",
      "object": "",
      "int": "Integer"
    }

    # Fixup
    if unka[1] == "ColorRGB":
      unka[1] = "Color"
    if unka[1] == "Real":
      unka[1] = "double"

    unkaType = unka[1]
    if unkaType in unkaTypes:
      unkaNewType = unkaTypes[unkaType]
    else:
      unkaNewType = ""
    unka = unka[0:2] + [unkaNewType] + unka[2:]
    unkb = unkb[0:2] + "S" + unkb[2:]

  fes = [name, unka, unkb, fes]

  # Store GlobalSettings as we'll move it
  if name == "GlobalSettings":
    globalSettings = [fes]
    return []

  res = [fes]

  # Add model
  if _isModelMesh:
    
    # Add original model
    #print("%.100s" % fes)
    res += [orig + fes[3:]]

  # Keep track of all textures
  if _isTexture:
    textures += [fes[1][0]]

  # Keep track of all materials
  if _isMaterial:
    materials += [fes[1][0]]



  hacks = """
  if False:
    # Input samples:

                                ["Key", [
    215535403999, 0.0, true,
    217074942600, -5.102129936218262, true, true, 100.0, 16.04795265197754, true, true,
    415675422000, 63.90406036376953, true, true, 16.04795265197754, 0.0, true], "LDCLDCCDDCCLDCCDDC", []],






                                ["Key", [
               0, -36.74919509887695, true, true, 18.912996292114258, 18.778860092163086, true,
    215535403999, 51.511451721191406, true, true, 18.778860092163086, 0.0, true,
    217074942600, 51.511451721191406, true, true, 0.0,                0.0, true], "LDCCDDCLDCCDDCLDCCDDC", []],


  if False:
  """

  def emitCurves(model, vectorCurves):
    connections = []

    curveTypes = {
      "T": "Lcl Translation",
      "R": "Lcl Rotation",
      "S": "Lcl Scaling"
    }

    animationStack = random_uid()
    animationLayer = random_uid()

    objects += [["AnimationStack", [animationStack, "|Action::AnimStack", ""], "LSS", []]]
    objects += [["AnimationLayer", [animationLayer, "|Action::AnimLayer", ""], "LSS", []]]

    connections += [["C", ["OO", animationLayer, animationStack], "SLL", []]]

    for vectorCurve in vectorCurves:

      curveType = curveTypes[vectorCurve]

      animationCurveNode = random_uid()

      objects += [["AnimationCurveNode", [animationCurveNode, "%s::AnimCurveNode" % vectorCurve, ""], "LSS", []]]

      connections += [["C", ["OO", animationCurveNode, animationLayer], "SLL", []]]
      connections += [["C", ["OP", animationCurveNode, model, curveType], "SLLS", []]]

      scalarCurves = vectorCurves[vectorCurve]
      for scalarCurve in scalarCurves:

        keyTime = [time for time in scalarCurve]
        keyValueFloat = [scalarCurve[time] for time in scalarCurve]

        objects += [["AnimationCurve", [animationCurve, "::AnimCurve", ""], "LSS", [
          ["KeyTime", [keyTime], "l", []],
          ["KeyValueFloat", [keyValueFloat], "f", []],
        ]]]
        connections += [["C", ["OP", animationCurve, animationCurveNode, "d|%s" % scalarCurve], "SLLS", []]]


  def findFirst(root, _type):
    print("looking for '%s' in " % _type, root)
    children = root[3]
    for child in children:
      if child[0] == _type:
        return child
    return None

  # Scalar curve values
  def processTakesTakeModelChannelChannelChannelKey(root):
    keys = {}
    print(root)
    values = root[1]
    types = root[2]
    while(len(types) > 0):
      print(types)
      assert(types[0] == 'L')
      nextLink = types.find('L', 1)
      if nextLink == -1:
        nextLink = len(types)
      keyTypes = types[0:nextLink]
      print(keyTypes)

      if   keyTypes == "LDC":
        pass
      elif keyTypes == "LDCCDD":
        pass
      elif keyTypes == "LDCCDDC":
        pass
      elif keyTypes == "LDCCDDCC":
        pass
      else:
        print(keyTypes)
        assert(False)

      keyTime = values[0]
      keyValue = values[1]

      keys[keyTime] = keyValue

      values = values[nextLink:]
      types = types[nextLink:]

    return keys
      

  # Scalar curve
  def processTakesTakeModelChannelChannelChannel(root):
    print("reading scalar from", root)
    keyRoot = findFirst(root, "Key")
    if keyRoot == None:
      keys = {}
    else:
      keys = processTakesTakeModelChannelChannelChannelKey(keyRoot)
      keyCount = findFirst(root, "KeyCount")
      assert(len(keys) == keyCount[1][0])

    scalarCurve = keys

    return scalarCurve

  # Vector curve
  def processTakesTakeModelChannelChannel(root):

    vectorCurves = {}

    children = root[3]
    for child in children:
      if child[0] == "LayerType":
        #FIXME: Process?
        continue
      print(child)
      assert(child[0] == "Channel")
      curve = processTakesTakeModelChannelChannelChannel(child)

      curveName = child[1][0]
      vectorCurves[curveName] = curve

    return vectorCurves

  # Transform
  def processTakesTakeModelChannel(root):
    children = root[3]
    for child in children:
      print(child)
      assert(child[0] == "Channel")
      vectorCurves = processTakesTakeModelChannelChannel(child)

  def processTakesTakeModel(root):
    channels = {}
    children = root[3]
    for child in children:
      print(child)
      if child[0] == "Version":
        #FIXME: Process?
        continue
      assert(child[0] == "Channel")
      if child[1][0] != "Transform":
        print("Ignoring %s" % child)
        continue
      channels[child[1][0]] = processTakesTakeModelChannel(child)
    return channels

  def processTakesTake(root):
    model = findFirst(root, "Model")
    assert(model != None)
    channels = processTakesTakeModel(model)

    emitCurves(model[1][0], channels)

  def processTakes(root):
    print("Processing takes")
    children = root[3]
    for child in children:
      if child[0] == "Take":
        processTakesTake(child)

  
  hacks="""

  # Input:
      ["Takes", [], "", [
          ["Current", ["Take 001"], "S", []],
          ["Take", ["Take 001"], "S", [
              ["FileName", ["Take_001.tak"], "S", []],
              ["LocalTime", [0, 415675422000], "LL", []],
              ["ReferenceTime", [0, 415675422000], "LL", []],
              ["Model", ["camera1::Model"], "S", [
                  ["Version", [1.1], "D", []],
                  ["Channel", ["Transform"], "S", [
                      ["Channel", ["T"], "S", [
                          ["Channel", ["X"], "S", [
                              ["Default", [51.511451721191406], "D", []],
                              ["KeyVer", [4005], "I", []],
                              ["KeyCount", [3], "I", []],
                              ["Key", [0, -36.74919509887695, true, true, 18.912996292114258, 18.778860092163086, true, 215535403999, 51.511451721191406, true, true, 18.778860092163086, 0.0, true, 217074942600, 51.511451721191406, true, true, 0.0, 0.0, true], "LDCCDDCLDCCDDCLDCCDDC", []],
                              ["Color", [1.0, 0.0, 0.0], "DDD", []]]],
                          ["Channel", ["Y"], "S", [
                              ["Default", [116.69074249267578], "D", []],
                              ["KeyVer", [4005], "I", []],
                              ["KeyCount", [3], "I", []],
                              ["Key", [0, 127.337890625, true, true, -2.2815325260162354, -2.2653512954711914, true, 215535403999, 116.69074249267578, true, true, -2.2653512954711914, 0.0, true, 217074942600, 116.69074249267578, true, true, 0.0, 0.0, true], "LDCCDDCLDCCDDCLDCCDDC", []],
                              ["Color", [0.0, 1.0, 0.0], "DDD", []]]],
                          ["Channel", ["Z"], "S", [
                              ["Default", [107.56563568115234], "D", []],
                              ["KeyVer", [4005], "I", []],
                              ["KeyCount", [3], "I", []],
                              ["Key", [0, 121.76580810546875, true, true, -3.0428950786590576, -3.0213141441345215, true, 215535403999, 107.56563568115234, true, true, -3.0213141441345215, 0.0, true, 217074942600, 107.56563568115234, true, true, 0.0, 0.0, true], "LDCCDDCLDCCDDCLDCCDDC", []],
                              ["Color", [0.0, 0.0, 1.0], "DDD", []]]],
                          ["LayerType", [1], "I", []]]],
                      ["Channel", ["R"], "S", [

  # Output:
    animations = 
            ["AnimationStack", [819533392, "Cube|CubeAction::AnimStack", ""], "LSS", [
                #["Properties70", [], "", [
                #    ["P", ["LocalStop", "KTime", "Time", "", 36564041750], "SSSSL", []],
                #    ["P", ["ReferenceStop", "KTime", "Time", "", 36564041750], "SSSSL", []]]]]],
            ["AnimationLayer", [551956971, "Cube|CubeAction::AnimLayer", ""], "LSS", []],
            ["AnimationCurveNode", [338936673, "T::AnimCurveNode", ""], "LSS", [
                #["Properties70", [], "", [
                #    ["P", ["d|X", "Number", "", "A", 0.0], "SSSSD", []],
                #    ["P", ["d|Y", "Number", "", "A", 0.0], "SSSSD", []],
                #    ["P", ["d|Z", "Number", "", "A", 0.0], "SSSSD", []]]]]],
            ["AnimationCurve", [584517692, "::AnimCurve", ""], "LSS", [
                #["Default", [0.0], "D", []],
                #["KeyVer", [4008], "I", []],
                ["KeyTime", [[0, 1924423250, 3848846500, 5773269750, 7697693000, 9622116250, 11546539500, 13470962750, 15395386000, 17319809250, 19244232500, 21168655750, 23093079000, 25017502250, 26941925500, 28866348750, 30790772000, 32715195250, 34639618500, 36564041750]], "l", []],
                ["KeyValueFloat", [[0.0, -3.4027111530303955, -13.115904808044434, -28.397174835205078, -48.50410079956055, -72.69429016113281, -100.2253189086914, -130.3547821044922, -162.34027099609375, -195.43936157226562, -228.90968322753906, -262.0088195800781, -293.9942626953125, -324.1237487792969, -351.6547546386719, -375.84490966796875, -395.95184326171875, -411.23309326171875, -420.9463195800781, -424.3490295410156]], "f", []],
                #["KeyAttrFlags", [[24836]], "i", []],
                #["KeyAttrDataFloat", [[0.0, 0.0, 9.419963346924634e-30, 0.0]], "f", []],
                #["KeyAttrRefCount", [[20]], "i", []]]],

    connections =
          ["C", ["OO", 551956971, 819533392], "SLL", []], # AnimationLayer, AnimationStack
          ["C", ["OO", 338936673, 551956971], "SLL", []], # AnimationCurveNode, AnimationLayer
          ["C", ["OP", 338936673, 857243342, "Lcl Translation"], "SLLS", []], # AnimationCurveNode, Model
          ["C", ["OP", 584517692, 338936673, "d|X"], "SLLS", []], # AnimationCurve, AnimationCurveNode
          ["C", ["OP", 234080535, 338936673, "d|Y"], "SLLS", []],
          ["C", ["OP", 519460037, 338936673, "d|Z"], "SLLS", []],

          ["C", ["OO", 753068511, 551956971], "SLL", []],
          ["C", ["OP", 753068511, 857243342, "Lcl Rotation"], "SLLS", []],
          ["C", ["OP", 399065581, 753068511, "d|X"], "SLLS", []],
          ["C", ["OP", 979191344, 753068511, "d|Y"], "SLLS", []],
          ["C", ["OP", 841626665, 753068511, "d|Z"], "SLLS", []],

          ["C", ["OO", 761637206, 551956971], "SLL", []],
          ["C", ["OP", 761637206, 857243342, "Lcl Scaling"], "SLLS", []],
          ["C", ["OP", 946133573, 761637206, "d|X"], "SLLS", []],
          ["C", ["OP", 128370511, 761637206, "d|Y"], "SLLS", []],
          ["C", ["OP", 405789412, 761637206, "d|Z"], "SLLS", []],

          ["C", ["OO", 748381990, 551956971], "SLL", []],
          ["C", ["OP", 748381990, 933217033, "FocalLength"], "SLLS", []], # AnimationCurveNode, Camera
          ["C", ["OP", 489243950, 748381990, "d|FocalLength"], "SLLS", []]]],
  """

  if name == "Takes":
    print("Found takes?!")
    #FIXME: Re-enable this and finish it!
    #processTakes([name, unka, unkb, es])

  return res

ff = []
for e in f:
  for fe in [fixup(e)]:
    ff += fe
ff += globalSettings
assert(len(models) == 0)
# Replace version 6100 with version 7100
# Move Objects/GlobalSettings to /GlobalSettings

# Store JSON
jsonData = json.dumps(f, indent=2)
open(TMP_PATH_JSON + "-original", "w").write(jsonData)
jsonData = json.dumps(ff, indent=2)
open(TMP_PATH_JSON + "-fixed", "w").write(jsonData)

open(TMP_PATH_JSON, "w").write(jsonData)

# Convert back to FBX
json2fbx.json2fbx(TMP_PATH_JSON)

if False:
  #FIXME: Asserts?!
  # And back to JSON for pretty-print
  os.remove(TMP_PATH_JSON) 
  fbx2json.fbx2json(TMP_PATH_FBX)
