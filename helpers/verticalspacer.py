"""
Module represents a Label that can be used as spacer
"""

from PyQt6.QtWidgets import QLabel

class VerticalSpacer(QLabel):

    """
    Class represents spacer with no text
    """

    def __init__(self, width, height):
        super().__init__()
        if width is not None and height is not None:
            self.setFixedSize(width, height)
        elif width is not None and height is None:
            self.setFixedWidth(width)
        elif width is None and height is not None:
            self.setFixedHeight(height)
