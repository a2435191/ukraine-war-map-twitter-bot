from constants import DATA_PATH
from typing import Dict, Any
import traceback
import json
from log import get_logger, log_fn_enter_and_exit

LOGGER = get_logger(__name__)

class PermanentDataUpdater:
    """Update the data found in DATA_PATH using the enter-exit format.
    """
    @property
    @log_fn_enter_and_exit(LOGGER)
    def old_timestamp(self) -> float:
        """The old timestamp found in DATA_PATH.

        Returns:
            float: The last updated timestamp according to the .json file.
        """
        return self._data['latest_timestamp']
    
    @log_fn_enter_and_exit(LOGGER)
    def __init__(self, new_data: Dict[str, Any]):
        """Only constructor for PermanentDataUpdater.

        Args:
            new_data (Dict[str, Any]): Data that will be updated in the .json file on __exit__.
        """
        self._new_data = new_data
          
    @log_fn_enter_and_exit(LOGGER)  
    def __enter__(self) -> "PermanentDataUpdater":
        """Load data from DATA_PATH.

        Returns:
            PermanentDataUpdater: This instance.
        """
        with open(DATA_PATH) as fh:
            self._data: Dict[str, Any] = json.load(fh)
        return self
       
    @log_fn_enter_and_exit(LOGGER)     
    def __exit__(self, exception_type: type, exception: Exception, traceback: traceback) -> None:
        """Dump new data provided in the constructor back into DATA_PATH. Note that this also
        updates the internal state of the PermanentDataUpdater.

        Args:
            exception_type (type)\n 
            exception (Exception)\n
            traceback (traceback)\n
        """
        self._data.update(self._new_data)
        with open(DATA_PATH, "w") as fh:
            json.dump(self._data, fh, indent=2)