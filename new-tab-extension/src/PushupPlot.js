import {React, useEffect, useState} from 'react';
import Plotly from "plotly.js"
import createPlotlyComponent from 'react-plotly.js/factory';
const Plot = createPlotlyComponent(Plotly);

var WEEKDAYS = ["Mon", "Tues", "Wed", "Thu", "Fri", "Sat", "Sun"]

var Airtable = require('airtable');
var base = new Airtable({apiKey: 'keyXJnM7PboM0o2aI'}).base('apppukxJK1fMLPF9l');


function PushupPlot() {
    const [weekdayOrder, setWeekday_order] = useState([]);
    const [weekdayCounts, setWeekday_counts] = useState([]);

    useEffect(() => {
        var now = new Date();
        var tomorrowDayIndex = now.getDay() % 7;

        var weekday_order = [];
        var weekday_counts = [];

        for (var i = 0; i < 7; i++){
            weekday_order.push(WEEKDAYS[(tomorrowDayIndex + i) %  7]);
            weekday_counts.push(0);
        }

        base('Pushups').select({
            // Selecting the first 3 records in Grid view:
            maxRecords: 10,
            view: "Grid view"
        }).eachPage(function page(records, fetchNextPage) {
            // This function (`page`) will get called for each page of records.
        
            records.forEach(function(record) {
                var amount = record.get("Amount");
                var weekday = WEEKDAYS[record.get("Weekday") - 1];
                console.log(weekday);
        
                var indx = weekday_order.indexOf(weekday);
                if (indx < 0) {
                    weekday_order.push(weekday);
                    weekday_counts.push(amount);
                }
                else {
                    weekday_counts[indx] += amount;
                }
                
            });
        
            // To fetch the next page of records, call `fetchNextPage`.
            // If there are more records, `page` will get called again.
            // If there are no more records, `done` will get called.
            fetchNextPage();
        
        }, function done(err) {
            console.log(weekday_order);
            console.log(weekday_counts);
            if (err) { console.error(err); return; }

            setWeekday_order(weekday_order);
            setWeekday_counts(weekday_counts);
        });
    }, [])

    return (
        <div id="pushup">
            <Plot
            data={[
                {type: 'bar', x: weekdayOrder, y: weekdayCounts},
            ]}
            layout={ {width: 480, height: 360, title: 'Weekly Pushup Count'} }
            />
        </div>
    );
}

export default PushupPlot;