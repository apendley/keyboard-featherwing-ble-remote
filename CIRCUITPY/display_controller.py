import displayio
import terminalio
from collections import namedtuple
from adafruit_display_text.label import Label
from sprite_sheet import SpriteSheet, SpriteInstance
from user import colors

Layout = namedtuple("Layout", [
    'width', 
    'height', 
    'L1_X', 
    'L2_X', 
    'R1_X', 
    'R2_X', 
    'DBUTTON_X', 
    'DBUTTON_Y', 
    'BUTTON_ICON_Y', 
    'TOUCH_SCREEN_LABEL_Y'
])

Icon = namedtuple("Icon", ['view', 'width', 'height'])
Insets = namedtuple("Insets", ['top', 'bottom', 'left', 'right'])

class DisplayController:
    ALIGN_LEADING = 0
    ALIGN_CENTER = 1
    ALIGN_TRAILING = 2

    def __init__(self, display):
        self._display = display

        self._layout = Layout(
            width=display.width,
            height=display.height,
            L1_X=0,
            L2_X=88,
            R1_X=242,
            R2_X=display.width,
            DBUTTON_X=display.width // 2 + 4,
            DBUTTON_Y=display.height - 104,
            BUTTON_ICON_Y=220,
            TOUCH_SCREEN_LABEL_Y=54
        )

        self.color_index = 0
        self._sprite_sheet = SpriteSheet("icons-tilemap-32.bmp", palette=self.palette)

        self._root_group = displayio.Group()
        display.root_group = self._root_group

    @property
    def display(self):
        return self._display

    @property
    def layout(self):
        return self._layout

    @property
    def root_group(self):
        return self._root_group
        
    @property
    def sprite_sheet(self):
        return self._sprite_sheet

    @property
    def color_index(self):
        return self._color_index

    @color_index.setter
    def color_index(self, index):
        self._color_index = index
        self._palette = colors.make_palette(colors.ALL[index])

    @property
    def palette(self):
        return self._palette


    @palette.setter
    def palette(self, p):
        self._palette = p        

    @property
    def background_color(self):
        return self._palette[0]

    @property
    def foreground_color(self):
        return self._palette[1]

    # Add an aligned label
    def add_label(
        self, 
        to_group, 
        text, 
        x, 
        y, 
        h_align=ALIGN_CENTER, 
        v_align=ALIGN_CENTER, 
        font=terminalio.FONT, 
        color=None, 
        scale=1, 
        padding=False, 
        **kwargs
    ):
        if color is None:
            color = self.foreground_color

        if padding:
            insets = self._padding_for_text(text)
        else:
            insets = Insets(0, 0, 0, 0)

        anchor_x = 0.5
        anchor_y = 0.5

        if h_align == self.ALIGN_LEADING:
            anchor_x = 0.0
            x += insets.left * scale
        elif h_align == self.ALIGN_TRAILING:
            anchor_x = 1.0
            x -= insets.right * scale

        if v_align == self.ALIGN_LEADING:
            anchor_y = 0.0
            y += insets.top * scale
        elif v_align == self.ALIGN_TRAILING:
            anchor_y = 1.0            
            y -= insets.bottom * scale

        new_label = Label(font=font, 
            text=text, 
            color=color,
            padding_left=insets.left,
            padding_right=insets.right,
            padding_top=insets.top,
            padding_bottom=insets.bottom,
            scale=scale,
            **kwargs
        )

        new_label.anchor_point = (anchor_x, anchor_y)
        new_label.anchored_position = (x, y)
        to_group.append(new_label)
        return new_label

    # Add a sprite from the sprite sheet
    def add_sprite(
        self, 
        to_group, 
        sprite_frame, 
        x, 
        y, 
        h_align=ALIGN_CENTER, 
        v_align=ALIGN_CENTER, 
        palette=None,
        scale=1
    ):
        if palette is None:
            palette = self._palette

        offset_x = SpriteSheet.SPRITE_WIDTH // 2 * scale
        offset_y = SpriteSheet.SPRITE_HEIGHT // 2 * scale

        if h_align == self.ALIGN_LEADING:
            offset_x = 0
        elif h_align == self.ALIGN_TRAILING:
            offset_x = SpriteSheet.SPRITE_WIDTH * scale

        if v_align == self.ALIGN_LEADING:
            offset_y = 0
        elif v_align == self.ALIGN_TRAILING:
            offset_y = SpriteSheet.SPRITE_HEIGHT * scale

        return self._sprite_sheet.add_sprite(
            to_group=to_group,
            sprite_frame=sprite_frame,
            x=x - offset_x,
            y=y - offset_y,
            palette=palette,
            scale=scale
        )

    # For the purpose of this program, "Icon" means either an aligned label OR sprite, depending on the type of 'content'. 
    # if content is a string, the icon will be padded, double-sized label with an inverted palette.
    # if content is an int, the icon will be a sprite, where content is an index into the sprite sheet.
    # Returns an Icon, where 'view' is either a Label or a SpriteInstance, depending on 'content' type.
    def add_icon(
        self, 
        to_group, 
        content, 
        x, 
        y, 
        h_align=ALIGN_CENTER, 
        v_align=ALIGN_CENTER, 
        palette=None,
        scale=1
    ):
        if palette is None:
            palette = self._palette

        # If content is a string, create a label.
        if isinstance(content, str):
            # Text icons are always 2x scale
            scale *= 2

            new_label = self.add_label(
                to_group=to_group,
                text=content,
                x=x,
                y=y,
                h_align=h_align,
                v_align=v_align,
                color=palette[0],
                background_color=palette[1],
                padding=True,
                scale=scale
            )

            insets = self._padding_for_text(content)

            return Icon(
                view=new_label,
                width=(new_label.width + insets.left + insets.right) * scale,
                height=(new_label.height + insets.top + insets.bottom) * scale
            )

        # Otherwise content should be a int, which we'll use to create a SpriteInstance.
        else:
            sprite = self.add_sprite(
                to_group=to_group,
                sprite_frame=content,
                x=x,
                y=y,
                h_align=h_align,
                v_align=v_align,
                palette=palette,
                scale=scale
            )

            return Icon(view=sprite, width=SpriteSheet.SPRITE_WIDTH, height=SpriteSheet.SPRITE_HEIGHT)

    # We need to calculate this when determining a label's alignment,
    # as well as when trying to account for the padding when trying
    # to position things around a padded label.
    def _padding_for_text(self, text):
        if len(text) == 1:
            left_padding = 5
        else:
            left_padding = 3

        return Insets(
            top=1, 
            bottom=1, 
            left=left_padding, 
            # Probably due to rounding errors, the right side always seems
            # a little more padded than the left with the default font
            right=left_padding - 1
        )