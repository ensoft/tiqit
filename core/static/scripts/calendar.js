//
// Calendar
//

_daysOfWeek = new Array('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun');

_monthNames = new Array('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December');

function zeropad(num) {
  if (num < 10) {
    return '0' + num;
  } else {
    return '' + num;
  }
}

Date.prototype.getDateOnly = function() {
  var millis = this.getTime();
  return new Date(millis - (millis % 86400000));
};

Date.prototype.getTimeOnly = function() {
  var millis = this.getTime();
  return new Date(millis % 86400000);
};

Date.prototype.setDateOnly = function(date) {
  this.setFullYear(date.getFullYear());
  this.setMonth(date.getMonth());
  this.setDate(date.getDate());
};

Date.prototype.setTimeOnly = function(date) {
  this.setHours(date.getHours());
  this.setMinutes(date.getMinutes());
  this.setSeconds(date.getSeconds());
};

// Constructor

TiqitCalendar = function(format) {
  this.initialDate = null;

  if (!format) {
    format = 'mm/dd/yyyy hh:mm:ss';
  }
  this.format = format;

  var div = document.createElement('div');
  div.className = 'tiqitCalendar';
  div.calendar = this;
  this.calendar = div;

  var section = document.createElement('div');
  section.className = 'tiqitCalendarHead';
  div.appendChild(section);

  var item = document.createElement('span');
  item.className = 'tiqitCalendarNav';
  section.appendChild(item);

  var img = document.createElement('img');
  img.title = 'Go back one month';
  img.src = 'images/navi-left-tiny.png';
  img.addEventListener('click', TiqitCalendar.goBackOneMonth, false);
  img.calendar = this;
  item.appendChild(img);

  img = document.createElement('img');
  img.title = 'Reset date';
  img.src = 'images/navi-center-tiny.png';
  img.addEventListener('click', TiqitCalendar.resetDate, false);
  img.calendar = this;
  item.appendChild(img);

  img = document.createElement('img');
  img.title = 'Go forward one month';
  img.src = 'images/navi-right-tiny.png';
  img.addEventListener('click', TiqitCalendar.goForwardOneMonth, false);
  img.calendar = this;
  item.appendChild(img);

  if (format.indexOf('hh:mm') != -1) {
    item = document.createElement('span');
    item.className = 'tiqitCalendarTimeToggler';
    section.appendChild(item);

    img = document.createElement('img');
    img.title = 'Toggle clock';
    img.src = 'images/clock-small.png';
    img.addEventListener('click', TiqitCalendar.toggleClock, false);
    img.calendar = this;
    item.appendChild(img);
  }

  item = document.createElement('span');
  item.className = 'tiqitCalendarTitle';
  this.title = item;
  section.appendChild(item);

  section = document.createElement('table');
  this.table = section;
  div.appendChild(section);

  for (var i = 0; i < 7; i++) {
    item = document.createElement('col');
    section.appendChild(item);
  }

  section.createTHead();
  section.tHead.insertRow(-1);

  for (var i = 0; i < 7; i++) {
    item = document.createElement('th');
    item.appendChild(document.createTextNode(_daysOfWeek[i]));
    section.tHead.rows[0].appendChild(item);
  }

  section.appendChild(document.createElement('tbody'));
  for (var i = 0; i < 6; i++) {
    item = section.tBodies[0].insertRow(-1);

    for (var j = 0; j < 7; j++) {
      var cell = item.insertCell(-1);
      cell.addEventListener('click', TiqitCalendar.selectDate, false);
      cell.calendar = this;
    }
  }

  section = document.createElement('div');
  section.className = 'tiqitCalendarClock';
  section.style.display = 'none';
  this.clock = section;
  div.appendChild(section);

  section.appendChild(document.createTextNode('Time: '));

  item = document.createElement('span');
  item.className = 'tiqitCalendarClockElement';
  item.addEventListener('click', TiqitCalendar.changeTime, false);
  item.calendar = this;
  this.hours = item;
  section.appendChild(item);

  section.appendChild(document.createTextNode(':'));

  item = document.createElement('span');
  item.className = 'tiqitCalendarClockElement';
  item.addEventListener('click', TiqitCalendar.changeTime, false);
  item.calendar = this;
  this.minutes = item;
  section.appendChild(item);

  item = document.createElement('select');
  item.name = 'tz';
  this.tz = item;
  section.appendChild(item);

  var option = document.createElement('option');
  option.appendChild(document.createTextNode('GMT (+0)'));
  item.appendChild(option);

  this.showDate(new Date());
};

// Static Methods (Event Handlers)

TiqitCalendar.selectDate = function(event) {
  var cal = event.target.calendar;

  if (!cal.date) {
    cal.date = new Date(event.target.year, event.target.month, event.target.textContent);
  } else {
    cal.date.setDate(event.target.textContent);
    cal.date.setMonth(event.target.month);
    cal.date.setYear(event.target.year);
  }
  if (!cal.setDate(cal.date) && cal.input) {
    fireEvent('change', cal.input);
  }
};

TiqitCalendar.goBackOneMonth = function(event) {
  var cal = event.target.calendar;
  var month = cal.shownDate.getMonth();
  var year = cal.shownDate.getFullYear();

  if (month == 0) {
    month = 11;
    year -= 1;
  } else {
    month -= 1;
  }

  cal.shownDate.setMonth(month);
  cal.shownDate.setFullYear(year);

  cal.showDate(cal.shownDate);
};

TiqitCalendar.goForwardOneMonth = function(event) {
  var cal = event.target.calendar;
  var month = cal.shownDate.getMonth();
  var year = cal.shownDate.getFullYear();

  if (month == 11) {
    month = 0;
    year += 1;
  } else {
    month += 1;
  }

  cal.shownDate.setMonth(month);
  cal.shownDate.setFullYear(year);

  cal.showDate(cal.shownDate);
};

TiqitCalendar.changeTime = function(event) {
  var cal = event.target.calendar;

  var val = parseInt(event.target.textContent, 10);

  if (event.shiftKey) {
    val -= 1;
  } else {
    val += 1;
  }

  event.target.textContent = val;

  cal.shownDate.setHours((parseInt(cal.hours.textContent, 10) + 24) % 24);
  cal.shownDate.setMinutes((parseInt(cal.minutes.textContent, 10) + 60)% 60);

  if (cal.date) {
    cal.date.setTimeOnly(cal.shownDate);
    cal.setDate(cal.date);
  } else {
    cal.showDate(cal.shownDate);
  }
};

TiqitCalendar.toggleClock = function(event) {
  var cal = event.target.calendar;

  if (cal.clock.style.display == 'none') {
    cal.clock.style.display = 'block';
  } else {
    cal.clock.style.display = 'none';
  }

  TiqitCalendar.resizeShadow(cal);
};

TiqitCalendar.resetDate = function(event) {
  var cal = event.target.calendar;

  cal.setDate(cal.initialDate);
};

TiqitCalendar.showPopup = function(event) {
  var cal = event.target.calendar;

  var pos = getClientPos(event.target);
  var posx = pos[0];
  var posy = pos[1] + event.target.offsetHeight;

  if (window.innerWidth - posx < 250) {
    posx = window.innerWidth - 250;
  }

  if (window.innerHeight - posy < 100) {
    posy = window.innerHeight - 100;
  }

  cal.shadow.style.display = 'block';
  cal.shadow.style.left = ((posx + 10) + 'px');
  cal.shadow.style.top = ((posy + 10) + 'px');
  cal.shadow.style.width = cal.calendar.clientWidth;
  cal.shadow.style.height = cal.calendar.clientHeight;

  cal.calendar.style.display = 'block';
  cal.calendar.style.left = posx + 'px';
  cal.calendar.style.top = posy + 'px';

  setTimeout(TiqitCalendar.resizeShadow, 1, cal);
};

TiqitCalendar.resizeShadow = function(calendar) {
  calendar.shadow.style.width = calendar.calendar.clientWidth;
  calendar.shadow.style.height = calendar.calendar.clientHeight;
};

// Methods

TiqitCalendar.prototype.attach = function(_arg) {
  var parent = document.body;
  if (_arg) {
    parent = _arg;
  }

  this.calendar.style.display = 'block';
  parent.appendChild(this.calendar);

  this.initialDate = new Date();
};


// Return either:
//   - The parsed date string, an integer number of millis since the epoch.
//   - null if the date is not valid.
TiqitCalendar.prototype.parseDate = function(dateStr) {
  var dateRE = /^(\d{1,2})\/(\d{1,2})\/(\d{4})(.*)$/;
  var millis;

  // If the format is UK, then we need to convert the date first.
  if (this.format[0] === 'd') {
    dateStr = dateStr.replace(dateRE, "$2/$1/$3$4")
  }

  millis = Date.parse(dateStr);
  return millis ? millis : null;
};


TiqitCalendar.prototype.attachPopup = function(input, trigger) {
  // When its a drop down, we want some other stuff
  this.shadow = document.createElement('div');
  this.shadow.className = 'tiqitCalendarShadow';
  this.shadow.style.display = 'none';

  this.calendar.style.display = 'none';
  this.calendar.addEventListener('mouseout', function(event) {
    var hide = false;
    var cal = event.currentTarget.calendar;
    try {
      if (!isAncestorOf(event.currentTarget, event.relatedTarget)) {
//          !isAncestorOf(cal.input, event.relatedTarget) &&
//          !isAncestorOf(cal.trigger, event.relatedTarget)) {
        hide = true;
      }
    } catch (e) {
      hide = true;
    }
    if (hide) {
      cal.calendar.style.display = 'none';
      cal.shadow.style.display = 'none';
    }
  }, false);

  input.addEventListener('change', function(event) {
    if (event.currentTarget.value) {
      var millis = event.currentTarget.calendar.parseDate(event.currentTarget.value);
      if (millis !== null) {
        var date = new Date(millis);
        event.currentTarget.calendar.setDate(date);
      }
    }
  }, false);

  document.body.appendChild(this.shadow);
  document.body.appendChild(this.calendar);

  trigger.calendar = this;
  input.calendar = this;
  this.input = input;
  trigger.addEventListener('click', TiqitCalendar.showPopup, false);

  var millis = this.parseDate(this.input.value);
  if (millis !== null) {
    var date = new Date(millis);
    this.initialDate = date;
    this.setDate(date);
  }
};

TiqitCalendar.prototype.displayTime = function() {
  this.hours.textContent = zeropad(this.shownDate.getHours());
  this.minutes.textContent = zeropad(this.shownDate.getMinutes());
};

/*
 * Returns true if the calendar has an input field and the value in that field
 * was changed, false otherwise.
 */
TiqitCalendar.prototype.setDate = function(date) {
  if (!date || date == new Date(NaN)) {
    this.date = null;
    this.showDate(this.initialDate);
  } else {
    this.date = new Date(date.getTime());
    this.showDate(this.date);
  }

  if (this.input) {
    var oldval = this.input.value;
    if (this.date) {
      if (this.format == 'mm/dd/yyyy hh:mm:ss') {
        this.input.value = zeropad(this.date.getMonth() + 1) + '/' +
            zeropad(this.date.getDate()) + '/' +
            zeropad(this.date.getFullYear()) + ' ' +
            zeropad(this.date.getHours()) + ':' +
            zeropad(this.date.getMinutes()) + ':' +
            zeropad(this.date.getSeconds());
      } else if (this.format == 'dd/mm/yyyy hh:mm:ss') {
        this.input.value = zeropad(this.date.getDate()) + '/' +
            zeropad(this.date.getMonth() + 1) + '/' +
            zeropad(this.date.getFullYear()) + ' ' +
            zeropad(this.date.getHours()) + ':' +
            zeropad(this.date.getMinutes()) + ':' +
            zeropad(this.date.getSeconds());
      } else if (this.format == 'dd/mm/yyyy') {
        this.input.value = zeropad(this.date.getDate()) + '/' +
            zeropad(this.date.getMonth() + 1) + '/' +
            zeropad(this.date.getFullYear());
      } else if (this.format == 'mm/dd/yyyy') {
        this.input.value = zeropad(this.date.getMonth() + 1) + '/' +
            zeropad(this.date.getDate()) + '/' +
            zeropad(this.date.getFullYear());
      } else {
        this.input.value = this.date.toString();
      }
    } else {
      this.input.value = '';
    }
    if (this.input.value != oldval) {
      fireEvent('change', this.input);
      return true;
    }
  }

  return false;
}

TiqitCalendar.prototype.showDate = function(date) {
  if (!date || date.getTime() == NaN) {
    date = new Date();
  }

  var now = new Date();

  this.shownDate = new Date(date.getTime());
  this.title.textContent = _monthNames[date.getMonth()] + ' ' + date.getFullYear();

  // Find a Monday that is on or before the current date
  var month = date.getMonth();
  var first = new Date(date.getTime());
  first.setDate(1);
  var day = first.getDay();
  var diff = (day + 6) % 7;

  var curr = new Date(first.getTime());
  curr.setDate(curr.getDate() - diff);

  for (var i = 0; i < (7 * 6); i++) {
    var cell = this.table.tBodies[0].rows[parseInt(i / 7)].cells[i % 7];
    cell.textContent = curr.getDate();
    cell.month = curr.getMonth();
    cell.year = curr.getFullYear();
    if (cell.month != month) {
      cell.className = 'othermonth';
    } else {
      cell.className = '';
    }
    if (this.date &&
        curr.getDateOnly().getTime() == this.date.getDateOnly().getTime()) {
      cell.className += ' selected';
    }
    if (curr.getDateOnly().getTime() == now.getDateOnly().getTime()) {
      cell.className += ' today';
    }
    curr.setDate(curr.getDate() + 1);
  }

  this.displayTime();
};
