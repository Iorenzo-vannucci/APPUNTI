import numpy as np
import chipwhisperer as cw

class Result():
    """Class representing a 'Result' object.

    A 'Result' object is composed by a list collecting all the power traces recorded by the service
    and two tokens (one unique to each user, the other indicating a progressive number associated to
    the associated request) that tags the 'Result'. The first token is used to associate the 'Result' to
    the user that requested it. The second ('tag2') is used to associate the result to the correct
    request. The 'traces' object can assume two different topologies: the first, more complex,
    reflects the objects as supported by the ChipWhisperer library (numpy ndarrays). The second one
    represents the same data, but follows an easier representation, so to make
    serialization easier. The translation from one representation to the other is made possible by
    the methods 'simplify_traces' and 'desimplify_traces'.
    """
    def __init__(
        self,
        token_: str,
        tag2_: int,
        traces_: list,
    ) -> None:
        """Initializes a Result object.

        Args:
            token_ (str): The string value that tags the current Result
            tag2_ (int): The int value that furtherly tags the current Result
            traces_ (list): The list collecting all the power traces recorded by the service.

        Raises:
            TypeError: Trying to assign a different type other than 'str' to 'token_'. 
            TypeError: Trying to assign a different type other than 'int' to 'tag2_'. 
            TypeError: Trying to assign a different type other than 'list' to 'traces_'
        """        
        if not isinstance(token_, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(token_)}'")
        if not isinstance(tag2_, int):
            raise TypeError(f"Expecting a 'int' type, received '{type(tag2_)}'")
        if not isinstance(traces_, list):
            raise TypeError(f"Expecting a 'list' type, received '{type(traces_)}'")
        self.__token = token_
        self.__tag2 = tag2_
        self.__traces = traces_

    def simplify_traces(self) -> None:
        """Transform the 'traces' attribute so to make it JSON serializable.

        For every 'Trace' element in the 'traces' list, decompose it into a 'wave', 'textin',
        'textout', 'key' simplified tuple. The final 'traces' attribute will now consist of a
        list of tuples, allowing for an easy serialization using the JSON library.
        """
        # TODO: Find and manage the possible exceptions raised by this method
        traces_simplified = []
        for trace in self.__traces:
            # "wave" from numpy NDarray to Python list
            wave_list = trace.wave.tolist()
            # "textin", "textout" and "key" from CWByteArray to numpy NDArray to Python list
            textin_list = cw.util.bytearray2binarylist(trace.textin).tolist()
            try:
                textout_list = cw.util.bytearray2binarylist(trace.textout).tolist()
            except:
                trace_tuple = (wave_list, textin_list)
            else:
                trace_tuple = (wave_list, textin_list, textout_list)
            traces_simplified.append(trace_tuple)
        self.__traces = traces_simplified

    def desimplify_traces(self) -> None:
        """Transform the 'traces' attribute from a simple serializable representation to a more
        complex one, the same used by ChipWhisperer's library.

        For every 'tuple' element in the 'traces' list, decompose it and recreate the original 'wave', 'textin',
        'textout', 'key' subcomponents of the 'Trace' object, used by the ChipWhisperer library.
        """
        # TODO: Find and manage the possible exceptions raised by this method
        traces = []
        for trace_tuple in self.__traces:
            # "wave_list" from Python list to numpy NDarray
            wave = np.array(trace_tuple[0])
            # "textin", "textout" and "key" from CWByteArray to numpy NDArray to Python list
            textin = cw.util.hexStrToByteArray(cw.util.list2hexstr(cw.util.binarylist2bytearray(trace_tuple[1]), ","))
            try:
                textout = cw.util.hexStrToByteArray(cw.util.list2hexstr(cw.util.binarylist2bytearray(trace_tuple[2]), ","))
            except:
                textout = cw.util.hexStrToByteArray(cw.util.list2hexstr([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))
            key = cw.util.hexStrToByteArray(cw.util.list2hexstr([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]))

            traces.append(cw.Trace(wave, textin, textout, key))
        self.__traces = traces


    @property
    def token(self) -> str:
        """Getter method, returns the token that tags the current result.

        Returns:
            str: The user token that tags the current Result.
        """        
        return self.__token

    @token.setter
    def token(self, value: str) -> None:
        """Setter method, sets the token that tags the current result.

        Args:
            value (str): The string value to be assigned to the token

        Raises:
            TypeError: Trying to assign a different type other than 'str' to 'token'.
        """        
        if not isinstance(value, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(value)}'")
        self.__token = value


    @property
    def tag2(self) -> int:
        """Getter method, returns 'tag2', the second tag attached to the current result.

        Returns:
            int: The second tag attached to the current Result.
        """        
        return self.__tag2

    @tag2.setter
    def tag2(self, value: int) -> None:
        """Setter method, sets 'tag2', the second tag attached to the current result.

        Args:
            value (int): The string value to be assigned to the second tag

        Raises:
            TypeError: Trying to assign a different type other than 'int' to 'tag2'.
        """        
        if not isinstance(value, int):
            raise TypeError(f"Expecting a 'int' type, received '{type(value)}'")
        self.__tag2 = value


    @property
    def traces(self) -> list:
        """Getter method, returns the results obtained from the service.

        Returns:
            list: The list collecting all the power traces recorded by the service.
        """        
        return self.__traces

    @traces.setter
    def traces(self, value: list) -> None:
        """Setter method, sets the list collecting all the power traces recorded by the service.

        Args:
            value (list): The list of power traces

        Raises:
            TypeError: Trying to assign a different type other than 'list' to 'traces'.
        """        
        if not isinstance(value, list):
            raise TypeError(f"Expecting a 'list' type, received '{type(value)}'")
        self.__traces = value