import {useEffect, React} from 'react';
import Countup from './countup.js';
import Calendar from './Calendar.js'
import PushupPlot from './PushupPlot.js'
import './App.css';
import productScript from "./producthunt.js"

function App() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = productScript;
    script.async = true;
    document.body.appendChild(script);
  })

  return (
    <div className="App">
      <link href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.min.css" rel="stylesheet"></link>
      <div className="ph">
        <div className="sixteen wide center aligned column">
          <h2 className="column_title">Today's Product Hunt</h2>
          <div className="product_hunt">
          </div>
        </div>
      </div>

      <div className="pushup_wrapper">
        <div className="sixteen wide center aligned column">
          <h2 className="column_title">Analytics</h2>
          <PushupPlot/>
        </div>
      </div>

      <div className="lifemanage">
        <h2 className="column_title"> Life Management </h2>
        <Countup/>
        <Calendar/>
        {/* <iframe
          src="https://calendar.google.com/calendar/embed?height=600&amp;wkst=1&amp;bgcolor=%23ffffff&amp;ctz=America%2FNew_York&amp;src=YWxleGhxMTAwMEBnbWFpbC5jb20&amp;src=ZnIwNzJhb3R1Mm1mcjFsaHNsaW5qNGNoMGtAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&amp;src=bzJsOTJmYzgwbmFvdDduaDhmbWM0aWtsaDhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&amp;src=dXFncnFhM2szcm5rcGwzM3JqMzdicXU1bzRAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ&amp;src=YXF1YWNoQGJvdGtlZXBlci5jb20&amp;src=YXF1YWNoQG1pdC5lZHU&amp;color=%23cc003c&amp;color=%23039BE5&amp;color=%23EF6C00&amp;color=%234285F4&amp;color=%23F6BF26&amp;color=%23F09300&amp;mode=WEEK&amp;showNav=0&amp;showPrint=0&amp;showTabs=0&amp;showTitle=0&amp;showTz=0"
          width="800" height="600" frameBorder="0" scrolling="no"></iframe> */}
      </div>
    </div>
  );
}

export default App;
