import { useEffect, useState, React } from 'react';
import axios from 'axios';
import FullCalendar from '@fullcalendar/react'
import timeGridPlugin from '@fullcalendar/timegrid'


function Calendar() {
  const [eventsList, setEventsList] = useState({})

  useEffect(() => {
    // axios.get('https://cors-anywhere.herokuapp.com/http://gcal-webhook.herokuapp.com/day')
    axios.get('http://gcal-webhook.herokuapp.com/day')
      .then((response) => {
        console.log("response", response.data['records']);
        var events = response.data['records']

        var newEventsList = []

        for (var i in events) {
          var title = events[i].fields.Name
          var end = new Date(events[i].fields.endTime)
          var end_copy = new Date(events[i].fields.endTime)
          var duration = events[i].fields.duration
          var status = events[i].fields.Status
          
          var start = new Date(end_copy.setMinutes(end_copy.getMinutes() - duration * 60.0))

          if (status === "Done") {
            var bgColor = "#FBBC04"
            var borderColor = "#FDDE82"
          }
          else {
            var bgColor = "#4285F4"
            var borderColor = ""
          }

          var event_ = {
            "title": title,
            "start": start.toISOString(),
            "end": end.toISOString(),
            "backgroundColor": bgColor,
            "borderColor": borderColor
          }
          newEventsList.push(event_)
        }
        console.log(newEventsList)
        setEventsList(newEventsList)
      })
  }, [])

  return (
    <div id="calendarWrapper">
      <FullCalendar
        plugins={[timeGridPlugin]}
        initialView="timeGridDay"
        nowIndicator={true}
        scrollTime={(new Date(Date.now()).getHours()-2).toString() + ":00"}
        headerToolbar={{
          left: '',
          right: 'timeGridDay, timeGridFourDay'
        }}
        views={{
          "timeGridFourDay": {
            duration: { days: 4 },
            type: 'timeGrid',
            buttonText: '4 day'
          }
        }}
        height="600px"
        events={eventsList}
      />
    </div>
  )
}

export default Calendar