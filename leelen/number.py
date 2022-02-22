__all__ = ['Number']


class Number:
    block: int
    room: int

    def __init__(self, block, room=None, extension=None):
        if room is None:
            if isinstance(block, str):
                parts = block.split('-')
                if len(parts) > 3:
                    raise ValueError('too many parts')
                self.block = int(parts[0])
                self.room = int(parts[1])
                self.extension = int(parts[2]) if len(parts) > 2 else None
            else:
                self.extension = int(block[0])
                if self.extension == 0xff:
                    self.extension = None
                self.room = int(block[1]) + int(block[2]) * 100
                self.block = int(block[3]) + int(block[4]) * 100
        else:
            self.block = int(block)
            self.room = int(room)
            self.extension = int(extension) if extension is not None else None

        non_positive = "`{}' must be positive"
        too_many_digits = "`{}' must be {} digits"

        if self.block < 0:
            raise ValueError(non_positive.format('block'))
        if self.block > 9999:
            raise ValueError(too_many_digits.format('block', 4))

        if self.room < 0:
            raise ValueError(non_positive.format('room'))
        if self.room > 9999:
            raise ValueError(too_many_digits.format('room', 4))

        if self.extension is not None:
            if self.extension < 0:
                raise ValueError(non_positive.format('extension'))
            if self.extension > 9:
                raise ValueError(too_many_digits.format('extension', 1))

    def __repr__(self):
        return f'<{type(self).__name__}: {self}>'

    def __str__(self):
        s = f'{self.block:04d}-{self.room:04d}'
        if self.extension is not None:
            s += f'-{self.extension:01d}'
        return s

    def __bytes__(self):
        return bytes([
            self.extension if self.extension is not None else 0xff,
            *divmod(self.room, 100)[::-1], *divmod(self.block, 100)[::-1]
        ])
