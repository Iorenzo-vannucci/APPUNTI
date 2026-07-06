#!/usr/bin/env python3
import time
import rpyc
import json
import queue
import chipwhisperer as cw
from socket import gaierror, timeout
from cyberchallenge_client._result import Result

# MUST config
# FIXME: Set timeout to 'None' of production use, or this value will override the user timeout
rpyc.core.protocol.DEFAULT_CONFIG["sync_request_timeout"] = None
# Mandatory, allows JSON serialization of complex objects
rpyc.core.protocol.DEFAULT_CONFIG['safe_attrs'].add('__dict__')


"""The default **mandatory** configuration linked to each capture request.

This dict specifies ALL the configuration keys associated to the capture request sent by the
CyberChallenge.it user. Keys added by the user other than the ones here specified will not be
considered by the server.

Keys:
    * num_traces (int): The number of traces to be captured by the ChipWhisperer device.
"""
default_capture_config = {
    "num_traces":   100
}

"""
The default **optional** configuration for the scope board, to be attached to a capture request.

    This dict specifies ALL the allowed configuration keys that may be used to configure the
    ChipWhisperer scope board. Keys added by the user other than the ones here specified will not be
    considered by the server.

    Keys: 
        See Official Documentation -> https://chipwhisperer.readthedocs.io/en/latest/api.html#chipwhisperer-nano-scope
"""
default_scope_config = {
    "io":
        {
            "tio1":        "serial_rx",
            "tio2":        "serial_tx",
            "tio3":        "high_z",
            "tio4":        "high_z",
            "pdid":        True,
            "pdic":        False,
            "nrst":        True,
            "clkout":      7500000.0,
            "cdc_settings":[1,1],
        },
    "adc":
        {
            "clk_src":  "int",
            "clk_freq": 7500000.0,
            "samples":  5000,
        },
    "glitch":
        {
            "repeat":      0,
            "ext_offset":  0,
        },
}


class Utility():
    """Class wrapping all the tools needed to start communicating with the server and to forward capture requests to it.
    """    

    def __init__(
        self,
        url_: str,
        port_: int,
        token_: str,
    ) -> None:
        """'Utility' class constructor.

        Initializes the 'Utility' class by specifying all the necessary information to start communicating with the server.

        Args:
            url_ (str): The URL (or IP address) of the CyberChallenge.it server
            port_ (int): The port of the service made available by the CyberChallenge.it server
            token_ (str): The user token uniquely associated to each student's personal account

        Raises:
            TypeError: Trying to assign a different type other than 'str' to 'url_'.
            TypeError: Trying to assign a different type other than 'int' to 'port_'.
            TypeError: Trying to assign a different type other than 'str' to 'token_'.
        """    
        if not isinstance(url_, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(url_)}'")
        if not isinstance(port_, int):
            raise TypeError(f"Expecting a 'int' type, received '{type(port_)}'")
        if not isinstance(token_, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(token_)}'")
        self.__url = url_
        self.__port = port_

        # __token is used to tag both the request and the corresponding result. This information is used by the 
        # dispatcher to assign to the correct user the correct result. We don't want Bob receiving the result of Alice.
        self.__token = token_

        # __tag2 is used to tag both the request and the corresponding result. This information is used by the 
        # dispatcher to assign to the correct user the correct result, compatible with the latest request sent. We 
        # don't want Bob collecting the old "result_1" if Bob sent the "request_2". Bob must instead receive "result_2"
        self.__tag2 = 0


    def __get_tracking_info(self, msg: str) -> None:
        """Function used by the dispatcher (server) to update the user about the status of the request sent.

        Args:
            msg (str): The latest server update on the latest capture request.
        """
        print(msg)


    @property
    def url(self) -> str:
        """Getter method, returns the URL (or IP address) associated to the CyberChallenge server.

        Returns:
            str: The URL (or IP address) associated to the CyberChallenge server.
        """        
        return self.__url

    @url.setter
    def url(self, value: str) -> None:
        """Setter method, sets the URL (or IP address) associated to the CyberChallenge server.

        Args:
            value (str): The string value to be assigned to the url.

        Raises:
            TypeError: Trying to assign a different type other than 'str' to 'url'.
        """        
        if not isinstance(value, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(value)}'")
        self.__url = value


    @property
    def port(self) -> int:
        """Getter method, returns the port associated to the service made available by the
        CyberChallenge server.

        Returns:
            int: The port associated to the service made available by the CyberChallenge server.
        """        
        return self.__port

    @port.setter
    def port(self, value: int) -> None:
        """Setter method, sets the port associated to the service made available by the
        CyberChallenge server.

        Args:
            value (int): The port associated to the service made available by the CyberChallenge server.

        Raises:
            TypeError: Trying to assign a different type other than 'int' to 'port'.
        """        
        if not isinstance(value, int):
            raise TypeError(f"Expecting a 'int' type, received '{type(value)}'")
        self.__port = value


    @property
    def token(self) -> str:
        """Getter method, returns the user token previously assigned to the 'Utility' class.

        Such token is uniquely and personally assigned to each student.

        Returns:
            str: The personal token assigned to each student.
        """        
        return self.__token

    @token.setter
    def token(self, value: str) -> None:
        """Setter emthod, sets the user token.

        Such token is uniquely and personally assigned to each student.

        Args:
            value (str): The personal token assigned to each student.

        Raises:
            TypeError: Trying to assign a different type other than 'str' to 'token'.
        """        
        if not isinstance(value, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(value)}'")
        self.__token = value


    def capture_request(
        self,
        # tag2,
        program_codename: str,
        reply_timeout: int,
        capture_config: dict[str, int],
        scope_config: dict[str, dict[str, object]] = None,
    ) -> tuple[bool, cw.project.Project]:
        """Function used to configure and forward a capture request to the CyberChallenge server.

        Args:
            program_codename (str): The unique codename used to identify the firmware to be executed the by target microcontroller.
            reply_timeout (int): The timeout (in seconds) before discarding the last request sent to the server. 
            capture_config (dict[str, int]): The **mandatory** dict containing all the configuration parameters associated to the current capture request.
            scope_config (dict[str,dict[str, object]], optional): The **optional** dict containing all the configuration parameters to be passed to ChipWhipserer's capture board before fulfilling the current capture request. Defaults to None.

        Raises:
            TypeError: Trying to assign a different type other than 'str' to 'program_codename'.
            TypeError: Trying to assign a different type other than 'int' to 'reply_timeout'.
            TypeError: Trying to assign a different type other than 'dict' to 'capture_config'.
            TypeError: Trying to assign a different type other than 'dict' to 'scope_config'.

        Returns:
            tuple[bool, cw.project.Project]: Tuple formed by a 'state' bool variable (indicating whether the capture request was fulfilled correctly or not) and a `project` variable, containing the result data sent collected by the ChipWhisperer board.
        """

        if not isinstance(program_codename, str):
            raise TypeError(f"Expecting a 'str' type, received '{type(program_codename)}'")
        if not isinstance(reply_timeout, int):
            raise TypeError(f"Expecting a 'int' type, received '{type(reply_timeout)}'")
        # Checks on 'capture_config': implemented here and proposed again in the dispatcher, just as a second check
        if capture_config is not None:
            try:
                if capture_config["num_traces"]:
                    if not isinstance(capture_config["num_traces"], int):
                        TypeError(f"Expecting a 'int' type, received '{type(capture_config['num_traces'])}'")
            except TypeError:
                # "num_traces" key does not exists
                raise
        else:
            # ERROR! User must define a capture_config dict!
            raise RuntimeError("User MUST specify a 'capture_config' dict!")
        # Checks on 'scope_config': implemented here (in a simplified form). Fully implemented in the dispatcher
        if scope_config is not None:
            if not isinstance(scope_config, dict):
                raise TypeError(f"Expecting a 'dict' type, received '{type(scope_config)}'")

        capture_start_time = time.time()

        project = cw.project.Project()

        exit_ = False
        state = False
        while not state and not exit_:
            try:
                # Increase the value of tag2 for every request sent
                self.__tag2 += 1
                conn = rpyc.connect(self.__url, self.__port, config=rpyc.core.protocol.DEFAULT_CONFIG)

                # Creating serialized packet
                capture_request_packet = [
                    self.__token,
                    self.__tag2,
                    program_codename,
                    reply_timeout,
                    capture_config,
                    scope_config,
                ]
                capture_request_packet_s = json.dumps(capture_request_packet)

                dispatcher_result = conn.root.capture_request(
                    capture_request_packet_s,
                    self.__get_tracking_info,
                )

                if dispatcher_result == "result_timeout":
                    # Special error code returned when timeout hit
                    raise TimeoutError

                if dispatcher_result == "queue_full":
                    # Special error code returned when timeout hit
                    raise queue.Full

                result_dict = json.loads(dispatcher_result)
                result = Result(
                    result_dict["_Result__token"],
                    result_dict["_Result__tag2"],
                    result_dict["_Result__traces"],
                )
                result.desimplify_traces()

                # Check if the token and the tag2 are the same
                # This issue should not happen!!
                if result.token != self.__token or result.tag2 != self.__tag2:
                # if result.token != self.__token:
                    # Error, they are different, invalidate this result
                    print(f"[ERROR] The result packet received is not related to the request sent: {result.token} vs. {self.__token}, {result.tag2} vs. {self.__tag2}")
                    # print(f"[ERROR] The result packet received is not related to the request sent: {result.token} vs. {self.__token}")
                    print("[ERROR] Discarding this result, please retry...")
                    state = False
                    exit_= True
                else:
                    # Check: if the number of traces obtained is equal to the number of traces requested
                    # This issue should not happen!!
                    if len(result.traces) != capture_config["num_traces"]:
                        # Error, they are different, invalidate this result
                        print(f"[ERROR] The number of traces received is different than the number of traces requested: {len(result.traces)} vs. {capture_config['num_traces']}")
                        print(f"[ERORR] To avoid this issue we suggest you increasing the timeout. Current timeout: {reply_timeout} seconds")
                        print("[ERROR] Discarding this result, please retry...")
                        state = False
                        exit_= True
                    else:
                        project.traces.extend(result.traces)
                        state = True
                        exit_ = True
            except (gaierror, timeout):
                print("DISPATCHER is unreachable, please check the URL or retry later...")
                time.sleep(1)
                state = False
                exit_ = True
            except (EOFError, ConnectionRefusedError, ZeroDivisionError):
                print("DISPATCHER is busy right now, please retry...")
                time.sleep(1)
                state = False
                exit_ = True
            # except TimeoutError:
            #     print("Timeout Error: DISPATCHER is taking too much to reply, please retry...")
            #     state = False
            #     exit_ = True
            except ValueError:
                # Checks not passed, device error etc
                print("Request checks not passed, device error etc.")
                state = False
                exit_ = True
            except TypeError:
                # Checks not passed
                print("Request checks not passed.")
                state = False
                exit_ = True
            except RuntimeError:
                # No capture_config passed to dispatcher (should not happen: the parameter is mandatory)
                print("No 'capture_config' handed to DISPATCHER.")
                state = False
                exit_ = True
            except IndexError:
                # List index out of range, dispatcher sees 0 (zero) devices connected
                print("DISPATCHER can't find any CW device!")
                state = False
                exit_ = True
            except KeyboardInterrupt:
                # Catch Ctrl-C, close the client
                # The thread opened on the dispatcher side will remain open
                # until the "reply_timeout" (or less) seconds pass.
                # When this timeout elapses, the dispatcher thread will close itself automatically
                # No better way to close the dispatcher thread immediately when Ctrl-C is hit has been found
                state = False
                exit_ = True
            except queue.Full:
                # Dispatcher's queue is full, and the blocking timeout has expired, returning this exception
                print("Queue Error: DISPATCHER is currently overloaded, please retry later...")
                state = False
                exit_ = True
            # TODO: Uncomment for production use
            except:
                print("Generic exception received")
                state = False
                exit_ = True
            finally:
                # https://stackoverflow.com/a/21317128
                # print("in finally")
                try:
                    # print("trying")
                    # print(f"{conn.closed}")
                    conn.close()
                    # print(f"{conn.closed}")
                except NameError:
                    print("DISPATCHER is down, no connection can be established!")
                    pass
                    # This happens when dispatcher is down and no connection can be established
                    # TODO: Comment below for production use
                    # print("Failed to close - NameError")
                    # Fail to connect, no "conn" object created
                except:
                    print("Failed to close - Other Exception")
                    # Failed to close

        if state:
            print(f"\n🟢 Capture completed! 🟢")
        else:
            print(f"\n🔴 ERROR: Capture NOT completed... 🔴")

        capture_time = time.time() - capture_start_time
        print(f"Capture terminated in: {capture_time:.2f} seconds")

        return (state, project)
