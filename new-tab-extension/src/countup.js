import { useEffect, useState, React } from 'react';

function setAge(birthday, setYear, setFractionYear) {
  var today = Date.now()
  var birthday_ms = new Date(birthday).getTime()
  var res = ((today - birthday_ms) / 365 / 24 / 3600 / 1000).toFixed(15)
  setYear(res.substring(0, 2))
  setFractionYear(res.substring(2))
}

function Countup() {
  const [year, setYear] = useState(new Date().toLocaleString())
  const [fractionYear, setFractionYear] = useState(new Date().toLocaleString())

  useEffect(() => {
    setInterval(() => {
      if (document.hasFocus()) {
        setAge("2001/01/12", setYear, setFractionYear)
      }
    }, 1000);

    setAge("2001/01/12", setYear, setFractionYear)
  })

  return (
    <div id="countup">
      <div className="countup_time">

        <div className="countup_title">AGE:</div>
        <div className="countup_major_minor">

        <div className="countup_major">{year}</div>
        <div className="countup_minor">{fractionYear}</div>
        </div>
      </div>
    </div>
  )
}

export default Countup;
