bl_info = {
        "name": "Estival Mesher",
        "author": "bluesnowball18",
        "version": (1, 0),
        "blender": (2, 80, 0),
        "description": "Senran Kagura: Estival Versus file editor"
}

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

import struct

def import_cat_file(filepath):
        file = open(filepath, "rb")

        file.seek(0x400)
        names = file.read(256).decode("ascii").split(",\r\n")

        del names[-1:]

        # go to number section of tmd0 header
        # file.seek(0x528)

        magic, = struct.unpack("I", file.read(4))

        file.seek(2, 1)
        verts_format, verts_format_2 = struct.unpack("BB", file.read(2))

        file.seek(104, 1)
        faces_start, = struct.unpack("I", file.read(4))

        file.seek(28, 1)
        verts_start, = struct.unpack("I", file.read(4))

        file.seek(56, 1)
        faces_count, = struct.unpack("I", file.read(4))

        file.seek(12, 1)
        verts_count, = struct.unpack("I", file.read(4))

        verts = []
        faces = []

        # pl*, hr*, en* (except en17_*)
        if verts_format == 0x9F and verts_format_2 == 0x74:
                verts_padding = 28
        # TODO: add support for wpn*
        # elif verts_format == 0x97 and verts_format_2 == 0x74:
        #        verts_padding = 20
        # en17_*, Costume (except Bura)
        elif verts_format == 0xBF and verts_format_2 == 0x74:
                verts_padding = 32
        # acce_*
        elif verts_format == 0x9F and verts_format_2 == 0x50:
                verts_padding = 20
        # obj*
        elif verts_format == 0xB7 and verts_format_2 == 0x50:
                verts_padding = 16
        # bg*
        elif verts_format == 0xB7 and verts_format_2 == 0x58:
                verts_padding = 16
        else:
                return

        file.seek(0x500 + verts_start)
        i = 0

        while i < verts_count:
                x, z, y = struct.unpack("fff", file.read(12))

                # verts.append(struct.unpack("fff", file.read(12)))
                verts.append((x, -y, z))

                i += 1
                file.seek(verts_padding, 1)

        file.seek(0x500 + faces_start)
        i = 0

        if verts_format_2 != 0x58:
                while i < faces_count:
                        faces.append(struct.unpack("HHH", file.read(6)))
                        i += 1
        else:
                while i < faces_count:
                        faces.append(struct.unpack("III", file.read(12)))
                        i += 1

        file.close()

        mesh = bpy.data.meshes.new(names[0])
        mesh.from_pydata(verts, [], faces)

        object = bpy.data.objects.new(names[0], mesh)

        bpy.context.collection.objects.link(object)

class ESM_MT_import_cat(Operator, ImportHelper):
        bl_idname = "import.cat"
        bl_label = "Import CAT"

        filename_ext = ".cat"

        def execute(self, operator):
                import_cat_file(self.properties.filepath)
                return { "FINISHED" }

def menu_func(self, context):
        self.layout.operator(ESM_MT_import_cat.bl_idname, text = "Senran Kagura: Estival Versus (*.cat)")

def register():
        bpy.utils.register_class(ESM_MT_import_cat)
        bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
        bpy.utils.unregister_class(ESM_MT_import_cat)
        bpy.types.TOPBAR_MT_file_import.remove(menu_func)

if __name__ == "__main__":
        register()