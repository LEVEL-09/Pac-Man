"""Axis-aligned bounding box collision detection."""


class Hitbox:
    """An axis-aligned rectangular collision box relative to an origin.

    Attributes:
        xo (int): X offset of the box relative to its owner's position.
        yo (int): Y offset of the box relative to its owner's position.
        w (int): Width of the box.
        h (int): Height of the box.
    """

    def __init__(
        self, x_offset: int, y_offset: int, width: int, height: int
    ) -> None:
        """Initialize the hitbox with an offset and size.

        Args:
            x_offset (int): X offset of the box relative to its
                owner's position.
            y_offset (int): Y offset of the box relative to its
                owner's position.
            width (int): Width of the box.
            height (int): Height of the box.
        """
        self.xo = x_offset
        self.yo = y_offset
        self.w = width
        self.h = height

    def detect_collision(
        self, x: int, y: int, other: "Hitbox", other_x: int, other_y: int
    ) -> bool:
        """Check whether this hitbox overlaps another hitbox.

        Args:
            x (int): X position of this hitbox's owner.
            y (int): Y position of this hitbox's owner.
            other (Hitbox): The other hitbox to test against.
            other_x (int): X position of the other hitbox's owner.
            other_y (int): Y position of the other hitbox's owner.

        Returns:
            bool: True if the two hitboxes overlap, False otherwise.
        """
        left = x + self.xo
        right = left + self.w
        top = y + self.yo
        bottom = top + self.h

        return not (
            left > other_x + other.xo + other.w
            or right < other_x + other.xo
            or bottom < other_y + other.yo
            or top > other_y + other.yo + other.h
        )
