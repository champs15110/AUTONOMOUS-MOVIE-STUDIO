#!/bin/bash
# Rebuild /tmp/glstub so the pypi `bpy` module imports headless (no GPU/X).
# /tmp is not persisted across sandbox rebuilds - re-run this after any reset.
# Usage: bash tools/glstub_recipe.sh
set -e
SITE=$(python3 -c "import site; print(site.getusersitepackages())")
BPY_SO=$(find "$SITE/bpy" -name "*.so" | head -1)
echo "bpy so: $BPY_SO"
mkdir -p /tmp/glstub

# libxkbcommon ships inside the opencv-python wheel
XKB=$(find "$SITE" -name "libxkbcommon.so*" | head -1)
if [ -n "$XKB" ]; then cp -L "$XKB" /tmp/glstub/libxkbcommon.so.0; echo "xkb: $XKB"; fi

# undefined GL/X symbols that must exist as no-ops (scan ALL bpy .so files,
# nested libs like libusd_ms.so have their own undefined symbols)
: > /tmp/glstub_syms.txt
for SO in $(find "$SITE/bpy" -name "*.so"); do
  nm -D -u "$SO" 2>/dev/null | awk '{print $NF}' | sed 's/@.*//'
done | sort -u \
  | grep -E '^(gl|glu|glX|egl|EGL|X|_X|Sm|SM|Ice|ICE|xkb_|xcb_|XF86VM|_XF86)' \
  > /tmp/glstub_syms.txt || true
echo "stub syms: $(wc -l < /tmp/glstub_syms.txt)"

# every missing DT_NEEDED lib becomes a stub exporting all those symbols
: > /tmp/glstub_libs.txt
for SO in $(find "$SITE/bpy" -name "*.so"); do
  ldd "$SO" 2>/dev/null | grep "not found" | awk '{print $1}'
done | sort -u > /tmp/glstub_libs.txt
cat /tmp/glstub_libs.txt
while read -r LIB; do
  [ -z "$LIB" ] && continue
  {
    echo '#include <stdint.h>'
    while read -r S; do
      [ -z "$S" ] && continue
      echo "void $S(void) {}"
    done < /tmp/glstub_syms.txt
  } > /tmp/glstub_stub.c
  gcc -shared -fPIC -O0 -o "/tmp/glstub/$LIB" /tmp/glstub_stub.c
done < /tmp/glstub_libs.txt
echo "glstub ready: $(ls /tmp/glstub | wc -l) files"
LD_LIBRARY_PATH=/tmp/glstub python3 -c "import bpy; print('bpy', bpy.app.version_string)"
