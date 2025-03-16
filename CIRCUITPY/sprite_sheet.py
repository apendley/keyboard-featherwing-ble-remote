import displayio
from collections import namedtuple

# A SpriteInstance is returned from the SpriteSheet.add_sprite() method.
# It contains all of the information necessary to manipulate a sprite
# that has been created from a sprite sheet.
SpriteInstance = namedtuple("Sprite", ['group', 'tilegrid', 'bitmap'])

class SpriteSheet:
    SPRITE_WIDTH = 32
    SPRITE_HEIGHT = 32

    def __init__(self, bitmap_path, palette=None):
        self._sprite_sheet = displayio.OnDiskBitmap(bitmap_path)

        if palette:
            self._palette = palette
        else:
            self._palette = self._sprite_sheet.pixel_shader

    @property
    def palette(self):
        return self._palette

    def add_sprite(self, to_group, sprite_frame, x=0, y=0, scale=1, palette=None):
        if palette is None:
            palette = self._palette

        tilegrid = displayio.TileGrid(self._sprite_sheet, 
                                      pixel_shader=palette,
                                      width = 1,
                                      height = 1,
                                      tile_width = self.SPRITE_WIDTH, 
                                      tile_height = self.SPRITE_HEIGHT)

        tilegrid[0] = sprite_frame

        sprite_group = displayio.Group()
        sprite_group.append(tilegrid)

        sprite_group.x = x
        sprite_group.y = y
        sprite_group.scale = scale

        to_group.append(sprite_group)

        return SpriteInstance(
            group=sprite_group, 
            tilegrid=tilegrid, 
            bitmap=self._sprite_sheet
        )
