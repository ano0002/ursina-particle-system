from panda3d.core import CollisionNode, CollisionBox, CollisionSphere, CollisionCapsule, CollisionPolygon
from panda3d.core import NodePath
from panda3d.core import BoundingVolume
from ursina.vec3 import Vec3
from ursina.mesh import Mesh


# Recursive.
def build_bvh(entity, node_path, solids, axis=0, only_xz=False, max_depth=8, max_solids=None, flatten=False, current_depth=0):
    if len(solids) == 1 or current_depth >= max_depth - 1:
        if max_solids is not None:
            if len(solids) <= max_solids:
                for e in solids:
                    node_path.node().addSolid(e)
                return
        else:
            for e in solids:
                node_path.node().addSolid(e)
            return
    solids_sorted = None
    if axis == 0:
        solids_sorted = sorted(solids, key=lambda s: s.getCollisionOrigin().getX())
    elif axis == 1:
        solids_sorted = sorted(solids, key=lambda s: s.getCollisionOrigin().getZ())
    else:
        solids_sorted = sorted(solids, key=lambda s: s.getCollisionOrigin().getY())
    mid_point = len(solids_sorted) // 2
    left_solids = solids_sorted[:mid_point]
    right_solids = solids_sorted[mid_point:]
    if only_xz:
        next_axis = (axis + 1) % 2
    else:
        next_axis = (axis + 1) % 3
    next_depth = current_depth + 1
    left_collision_node = CollisionNode('CollisionNode')
    left_collision_node.setBoundsType(BoundingVolume.BT_box)
    left_node_path = node_path.attachNewNode(left_collision_node)
    left_node_path.setPythonTag('Entity', entity)
    right_collision_node = CollisionNode('CollisionNode')
    right_collision_node.setBoundsType(BoundingVolume.BT_box)
    right_node_path = node_path.attachNewNode(right_collision_node)
    right_node_path.setPythonTag('Entity', entity)
    build_bvh(entity, left_node_path, left_solids, axis=next_axis, only_xz=only_xz, max_depth=max_depth, max_solids=max_solids, current_depth=next_depth, flatten=flatten)
    build_bvh(entity, right_node_path, right_solids, axis=next_axis, only_xz=only_xz, max_depth=max_depth, max_solids=max_solids, current_depth=next_depth, flatten=flatten)
    if flatten and current_depth < max_depth - 2:
        for child in left_node_path.getChildren():
            child.reparentTo(node_path)
        for child in right_node_path.getChildren():
            child.reparentTo(node_path)
        left_node_path.removeNode()
        right_node_path.removeNode()
        node_path.getBounds()


class Collider(NodePath):
    def __init__(self, entity, shape, bvh=False, bvh_max_depth=8, bvh_max_shapes=None, bvh_only_xz=False, bvh_flatten=False):
        super().__init__('collider')
        self.collision_node = CollisionNode('CollisionNode')

        self.shape = shape
        self.node_path = entity.attachNewNode(self.collision_node)
        self.node_path.setPythonTag('Entity', entity)

        if isinstance(shape, (list, tuple)):
            if bvh:
                self.node_path.node().setBoundsType(BoundingVolume.BT_box)
                build_bvh(entity, self.node_path, shape, max_depth=bvh_max_depth, max_solids=bvh_max_shapes, only_xz=bvh_only_xz, flatten=bvh_flatten)
            else:
                for e in shape:
                    self.node_path.node().addSolid(e)
        else:
            self.node_path.node().addSolid(self.shape)

    def show_bounds(self, only_leaves=True):
        stack = [self.node_path]
        while len(stack) > 0:
            node_path = stack.pop()
            if only_leaves:
                if node_path.getNumChildren() == 0:
                    node_path.showBounds()
            else:
                node_path.showBounds()
            for child in node_path.getChildren():
                stack.append(child)

    def hide_bounds(self):
        stack = [self.node_path]
        while len(stack) > 0:
            node_path = stack.pop()
            node_path.hideBounds()
            for child in node_path.getChildren():
                stack.append(child)

    # Recursive (depth first).
    def _remove(self, node_path):
        num_children = node_path.getNumChildren()
        for child in node_path.getChildren():
            self._remove(child)
        if num_children == 0:
            node_path.node().clearSolids()
            if node_path.hasPythonTag('Entity'):
                node_path.clearPythonTag('Entity')
        node_path.removeNode()

    def remove(self):
        self._remove(self.node_path)
        self.node_path = None
        # print('remove  collider')


    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        stack = [self.node_path]
        while len(stack) > 0:
            node_path = stack.pop()
            if value:
                node_path.show()
            else:
                node_path.hide()
            for child in node_path.getChildren():
                stack.append(child)


class BoxCollider(Collider):
    def __init__(self, entity, center=(0,0,0), size=(1,1,1)):
        self.center = center
        self.size = size

        size = [e/2 for e in size]
        size = [max(0.001, e) for e in size] # collider needs to have thickness
        super().__init__(entity, CollisionBox(Vec3(center[0], center[1], center[2]), size[0], size[1], size[2]))


class SphereCollider(Collider):
    def __init__(self, entity, center=(0,0,0), radius=.5):
        self.center = center
        self.radius = radius
        super().__init__(entity, CollisionSphere(center[0], center[1], center[2], radius))


class CapsuleCollider(Collider):
    def __init__(self, entity, center=(0,0,0), height=2, radius=.5):
        self.center = center
        self.height = height
        self.radius = radius
        super().__init__(entity, CollisionCapsule(center[0], center[1] + radius, center[2], center[0], center[1] + height, center[2], radius))


class MeshCollider(Collider):
    def __init__(self, entity, mesh=None, center=(0,0,0), bvh=False, bvh_max_depth=8, bvh_max_shapes=None, bvh_only_xz=False, bvh_flatten=False):
        self.center = center
        center = Vec3(center)
        if mesh is None and entity.model:
            mesh = entity.model
            # print('''auto generating mesh collider from entity's mesh''')

        self.collision_polygons = []

        if isinstance(mesh, Mesh):
            if mesh.mode == 'triangle':
                for i in range(0, len(mesh.generated_vertices), 3):
                    poly = CollisionPolygon(
                        Vec3(*mesh.generated_vertices[i+2]),
                        Vec3(*mesh.generated_vertices[i+1]),
                        Vec3(*mesh.generated_vertices[i]),
                        )
                    self.collision_polygons.append(poly)

            elif mesh.mode == 'ngon':
                # NOTE: does not support vertices len < 3. Is already being intercepted by pandas3D.
                for i in range(2, len(mesh.vertices)):
                    poly = CollisionPolygon(
                        Vec3(*mesh.vertices[i]),
                        Vec3(*mesh.vertices[i - 1]),
                        Vec3(*mesh.vertices[0]),
                    )
                    self.collision_polygons.append(poly)
            else:
                print('error: mesh collider does not support', mesh.mode, 'mode')
                return None


        elif isinstance(mesh, NodePath):
            from panda3d.core import GeomVertexReader
            verts = []
            children = mesh.getChildren()
            for child in children:
                child_transform = child.getTransform()
                child_mat = child_transform.getMat()
                geomNodeCollection = child.findAllMatches('**/+GeomNode')
                for nodePath in geomNodeCollection:
                    geomNode = nodePath.node()
                    for i in range(geomNode.getNumGeoms()):
                        geom = geomNode.getGeom(i)
                        vdata = geom.getVertexData()
                        for i in range(geom.getNumPrimitives()):
                            prim = geom.getPrimitive(i)
                            vertex_reader = GeomVertexReader(vdata, 'vertex')
                            prim = prim.decompose()

                            for p in range(prim.getNumPrimitives()):
                                s = prim.getPrimitiveStart(p)
                                e = prim.getPrimitiveEnd(p)
                                for i in range(s, e):
                                    vi = prim.getVertex(i)
                                    vertex_reader.setRow(vi)
                                    verts.append(child_mat.xformPointGeneral(vertex_reader.getData3()))

            for i in range(0, len(verts)-3, 3):
                p = CollisionPolygon(Vec3(verts[i+2]), Vec3(verts[i+1]), Vec3(verts[i]))
                self.collision_polygons.append(p)

        super().__init__(entity, self.collision_polygons, bvh=bvh, bvh_max_depth=bvh_max_depth, bvh_max_shapes=bvh_max_shapes, bvh_only_xz=bvh_only_xz, bvh_flatten=bvh_flatten)


    def remove(self):
        self.node_path.node().clearSolids()
        self.collision_polygons.clear()
        self.node_path.removeNode()



if __name__ == '__main__':
    from ursina import *
    from ursina import Ursina, Entity, Pipe, Circle, Button, scene, EditorCamera, color
    app = Ursina()

    e = Button(parent=scene, model='sphere', x=2)
    e.collider = 'box'          # add BoxCollider based on entity's bounds.
    e.collider = 'sphere'       # add SphereCollider based on entity's bounds.
    e.collider = 'capsule'      # add CapsuleCollider based on entity's bounds.
    e.collider = 'mesh'         # add MeshCollider matching the entity's model.
    e.collider = 'file_name'    # load a model and us it as MeshCollider.
    e.collider = e.model        # copy target model/Mesh and use it as MeshCollider.

    e.collider = BoxCollider(e, center=Vec3(0,0,0), size=Vec3(1,1,1))   # add BoxCollider at custom positions and size.
    e.collider = SphereCollider(e, center=Vec3(0,0,0), radius=.75)      # add SphereCollider at custom positions and size.
    e.collider = CapsuleCollider(e, center=Vec3(0,0,0), height=3, radius=.75) # add CapsuleCollider at custom positions and size.
    e.collider = MeshCollider(e, mesh=e.model, center=Vec3(0,0,0))      # add MeshCollider with custom shape and center.

    m = Pipe(base_shape=Circle(6), thicknesses=(1, .5))
    e = Button(parent=scene, model='cube', collider='mesh', color=color.red, highlight_color=color.yellow)
    # e = Button(parent=scene, model='quad', collider=, color=color.lime, x=-1)

    sphere = Button(parent=scene, model='icosphere', collider='mesh', color=color.red, highlight_color=color.yellow, x=4)

    EditorCamera()

    def input(key):
        if key == 'c':
            e.collider = None

    # def update():
    #     print(mouse.point)


    app.run()
