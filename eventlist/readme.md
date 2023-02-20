## Summary of Event List
*The event list is always growing - please branch and add a pull request if you'd like to add more events!*

The event list contains all the solar wind observation events used in the study. The structure looks like this:
  ```
  time_start              | time_stop                | MMS   | THEMIS | ARTEMIS | OMNI
  ----------------------------------------------------------------------------
  YYYY-MM-ddThh:mm:ss.000Z| YYYY-MM-ddThh:mm:ss.000Z | inst. | inst.  | inst.   | inst.
  ````
  The following quantities are:
  - `time_start`: The start time (datetime obj) of the event for the *furthest* satellite. This includes a 30-minute sliding buffer time for the close satellite. The start time of analysis should be 30 minutes after this.
  - `time_stop`: The stop time of the event. This is the same for both of them.
  - `MMS`: The MMS instrument that should be used for the data.
  - `THEMIS`: The THEMIS instrument that should be used for the data.
  - `ARTEMIS`: The ARTEMIS instrument that should be used for the data.
  - `OMNI`: The OMNI instrument that should be used for the data.
