"""
    Defines classes, which can be used to align text, printed to the buffers.
        Author: O.Z.
"""


class AutoAligner(object):
    """RAII class, which push aligner into the stream and pops it at exit.
    """
    def __init__(self, out_stream, aligner):
        self.__out_stream = out_stream
        self.__aligner = aligner

    def __enter__(self):
        self.__out_stream.push_aligner(self.__aligner)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__out_stream.pop_aligner()

    @property
    def stream(self):
        """Gets the aligned stream.
        """
        return self.__out_stream

    @property
    def aligner(self):
        """Gets the aligner.
        """
        return self.__aligner


class BaseAligner(object):
    """Base class for the aligners.

    Aligners can pass to the constructor of the base aligner class formatted
    string.

    Attributes:
        __string: saved initial string, which should be aligned.
    """

    def __init__(self, string):
        self.__string = string

    def __str__(self):
        return str(self.__string)

    @property
    def value(self):
        """Gets the string.

        Returns:
            string value.
        Raises:
            nothing.
        """
        return self.__string

    def initial_string(self):
        """Gets unformatted string.

        Should be overriden by the derived aligners.

        Returns:
            unformatted string value.
        Raises:
            NotImplementedError: the base class has no implementation.
        """
        raise NotImplementedError()

    def prototype(self, string):
        """Returns the same kind aligner as this, but applied to the another
        string. Should be overriden by the concrete aligners.

        Args:
            string: a string to align.
        Returns:
            The BaseAligner object, aligning the given string.
        Raises:
            NotImplementedError: the base class has no implementation.
        """
        raise NotImplementedError()


class CenterAligner(BaseAligner):
    """Aligner class, which puts the string into the center of the line.

    Width of the line and symbol to fill an empty space are passed to the
    constructor.

    Attributes:
        __initial_string: saved unformatted initial string.
        __width: width of the line.
        __symbol: a symbol to fill spaces.
    """

    def __init__(self, string, width=75, symbol=' '):
        super().__init__(("{:" + symbol + "^" + str(width) +
                          "}").format(string))

        self.__initial_string = string
        self.__width = width
        self.__symbol = symbol

    def initial_string(self):
        """Gets unformatted string.

        Returns:
            unformatted string value.
        Raises:
            nothing.
        """
        return self.__initial_string

    def prototype(self, string):
        """Returns the same kind aligner as this, but applied to the another
        string.

        Args:
            string: a string to align.
        Returns:
            The CenterAligner object, aligning the given string.
        Raises:
            nothing.
        """
        return CenterAligner(string, self.__width, self.__symbol)


class RightAligner(BaseAligner):
    """Aligner class, which puts the string to the right with indentation.

    Indent value and symbol to fill an empty space are passed to the
    constructor.

    Attributes:
        __initial_string: saved unformatted initial string.
        __indent: an indent from the left border.
        __symbol: a symbol to fill spaces.
    """

    def __init__(self, string, indent=4, symbol=' '):
        super().__init__(("{:" + symbol + ">" + str(indent + len(string)) +
                          "}").format(string))

        self.__initial_string = string
        self.__indent = indent
        self.__symbol = symbol

    def initial_string(self):
        """Gets unformatted string.

        Returns:
            unformatted string value.
        Raises:
            nothing.
        """
        return self.__initial_string

    def prototype(self, string):
        """Returns the same kind aligner as this, but applied to the another
        string.

        Args:
            string: a string to align.
        Returns:
            The RightAligner object, aligning the given string.
        Raises:
            nothing.
        """
        return RightAligner(string, self.__indent, self.__symbol)


# testing


def main():
    """Performs testing and e.t.c.
    """

    value = CenterAligner("center", 10, '-').value
    #print(value)
    assert value == "--center--"

    value = CenterAligner("center", 10, '-').prototype("center").value
    assert value == "--center--"

    value = RightAligner("right", 4, '-').value
    #print(value)
    assert value == "----right"

    value = RightAligner("right", 4, '-').prototype("right").value
    assert value == "----right"


if __name__ == '__main__':
    main()
