//
// AJAX magic to get results updates in the background.
//

var currentTimer;
var updatedBugs = new Array();

function clearUpdates(event) {
  var needregroup = false;
  while (updatedBugs.length > 0) {
    var row = document.getElementById(updatedBugs[0]);

    needregroup = clearMarksForBug(row) || needregroup;
  }

  // Clean up now
  if (needregroup) {
    filterGroupBy('results');
  }
}

// clearAutomaticRefresh
//
// Resume automatic refresh and start a refresh now.  Undoes what happens when
// network connectivity issues occur
//
function clearAutomaticRefresh(event) {
    startMonitoring();
    refreshNow();
    removeMessage(event);
}

// filterUpdated()
//
// Clears current filters and shows just the bugs with change markers on them.
//
function filterUpdated(event) {
  tiqitFilterClear('results');
  tiqitFilterTable('results', function (row) {
    return row.tiqitHistoryMenu;
  });
}

// markBug()
//
// Put a history drop down and clear marks button next to a bug.
// 
// bugid: The bug being marked.
// highlightAfter: Events in the history will appear highlighted if they occur
//   after this Date.
function markBug(bugid, highlightAfter) {
  var row = document.getElementById(bugid);

  // Add/update the history drop down menu.
  if (!contains(updatedBugs, bugid)) {
    if (Tiqit.prefs['miscHidePerRowAutoUpdateClear'] == 'false') {
      var historyMenu = createHistoryDropDownMenu(
        bugid,
        highlightAfter,
        function() {
          clearMarksForBug(row);
        }
      );
      row.tiqitActionsMenu.insertBefore(historyMenu, row.tiqitActionsMenu.firstChild);
      row.tiqitHistoryMenu = historyMenu;
    }

    updatedBugs.push(bugid);
  } else {
    var historyMenu = row.getElementsByClassName('tiqitHistoryDropDownMenu')[0];
    historyDropDownBugUpdated(historyMenu);
  }
  // Sanitise the row based on all of the new values.
  sanitiseRow(row);
}

function clearMarks(event) {
  var row = event.target.parentNode.parentNode;
  if (clearMarksForBug(row)) {
    filterGroupBy('results');
  }
}

function clearMarksForBug(row) {
  needregroup = false;

  if (row.isRemoved) {
    // Let folks know before we actually remove it
    generateCustomEvent('RowDeleting', row);
    row.parentNode.removeChild(row);
    needregroup = true;
  } else {
    row.style.outline = 'none';
    row.style.backgroundColor = 'transparent';
    row.title = null;
    for (var j = 0; j < row.cells.length; j++) {
      row.cells[j].style.outline = 'none';
      row.cells[j].style.backgroundColor = 'transparent';
      row.cells[j].title = null;
    }

    if (row.tiqitHistoryMenu) {
      row.tiqitHistoryMenu.parentNode.removeChild(row.tiqitHistoryMenu);
      row.tiqitHistoryMenu = null;
    }

    if (row.tiqitClearRowMarker) {
      row.tiqitClearRowMarker.parentNode.removeChild(row.tiqitClearRowMarker);
      delete row.tiqitClearRowMarker;
    }
  }

  arrayRemove(updatedBugs, row.id);

  var message = document.getElementById('tiqitResultsUpdateMessage');
  if (updatedBugs.length == 0) {
    var clearer = document.getElementById('tiqitClearUpdates');
    clearer.style.display = 'none';

    if (message) {
      message.parentNode.removeChild(message);
    }
  } else {
    if (message) {
      updateResultsUpdateMessage(message);
    }
  }

  return (needregroup);
}


// Make a row's cells transparent if the row has been removed.
function setRowOpacity(row) {
  var targetOpacity = row.isRemoved ? '0.25' : '1.0';
  if (row.tiqitOpacity != targetOpacity) {
    for (var i = 0; i < row.cells.length ; i++) {
      if (row.cells[i] && row.tiqitActionsMenu != row.cells[i]) {
        row.cells[i].style.opacity = targetOpacity;
      }
    }
    row.tiqitOpacity = targetOpacity;
  }
}


function updateResultsUpdateMessage(message) {
  for (var i = message.childNodes.length - 1; i >= 0; i--) {
    if (message.childNodes[i].nodeType == Node.TEXT_NODE) {
      message.removeChild(message.childNodes[i]);
    }
  }

  if (updatedBugs.length == 1) {
    message.appendChild(document.createTextNode("1 bug has changed since your last bookmark."));
  } else {
    message.appendChild(document.createTextNode(updatedBugs.length + ' bugs have changed since your last bookmark.'));
  }
}

function resetRefresh() {
  var note = document.getElementById('tiqitRefreshNow');
  note.removeChild(note.lastChild);
  note.appendChild(document.createTextNode('Refresh results now'));
  note.onclick = refreshNow;
  note.title = 'Check for changes to the current query now';
  note.style.textDecoration = 'underline';
  note.style.color = 'blue';
  note.firstChild.src = 'images/refresh-small.png';

  document.getElementById('tiqitResultsAutoUpdate').getElementsByTagName('img')[0].src = 'images/clock-small.png';
}

function onError(event) {
  message = sendMessage(2, "Unable to load updated results due to unexpected networking error. Automatic updates have been suspended.");

  var clear = document.createElement('img');
  clear.addEventListener('click', clearAutomaticRefresh, false);
  clear.src = 'images/tick-small.png';
  clear.setAttribute('title', 'Start automatic updates and refresh results now');
  clear.style.cssFloat = 'right';

  message.insertBefore(clear, message.firstChild);

  stopMonitoring();
  resetRefresh();
}


// Use a heuristic to correct dates that are either positively or negatively 
// offset by 3 hours.
function fixTimestamps(bugs) {
  var numPositiveOffset = 0;
  var numNegativeOffset = 0;
  var numCompared = 0;
  var threeHours = 1000 * 60 * 60 * 3;

  // Count the bugs that are offset by exactly +/- 3hrs.
  // For efficiency reasons compare at most 10 bugs.
  for (var i = 0; i < bugs.length && numCompared < 10; i++) {
    var bugid = bugs[i].getAttribute('identifier');
    var oldLine = document.getElementById(bugid);

    if (oldLine) {
      var oldTime = Date.parse(oldLine.getAttribute('lastupdate'));
      var newTime = Date.parse(bugs[i].getAttribute('lastupdate'));

      if (oldTime + threeHours == newTime) {
        numPositiveOffset++;
      } else if (oldTime - threeHours == newTime) {
        numNegativeOffset++;
      }
      numCompared++;
    }
  }

  // Apply the offset if the above count suggests we should.
  var correctionAmount = 0;
  if (numCompared > 0) {
    if (numPositiveOffset > numCompared / 2) {
      correctionAmount = -threeHours;
    } else if (numNegativeOffset > numCompared / 2) {
      correctionAmount = threeHours;
    }
  }

  if (correctionAmount != 0) {
    for (var i = 0; i < bugs.length; i++) {
      var correctedDate = new Date(Date.parse(bugs[i].getAttribute('lastupdate')) + correctionAmount);
      var lastupdate = "" + 
        zeropad(correctedDate.getMonth() + 1) + '/' +
        zeropad(correctedDate.getDate()) + '/' +
        zeropad(correctedDate.getFullYear()) + ' ' +
        zeropad(correctedDate.getHours()) + ':' +
        zeropad(correctedDate.getMinutes()) + ':' +
        zeropad(correctedDate.getSeconds());

      bugs[i].setAttribute('lastupdate', lastupdate);
      var fields = bugs[i].getElementsByTagName('field');
      for (var j = 0; j < fields.length; j++) {
        if (fields[j].getAttribute('name') == 'Sys-Last-Updated') {
          fields[j].textContent = lastupdate;
        }
      }
    }
  }
}

// processUpdatedBugList()
//
// Update the results table with new information.
// 
// bugs: <bug> elements of the updated table.
function processUpdatedBugList(bugs) {
  var newBugs = new Array();
  var content = document.getElementById('tiqitContent');
  var changes = updatedBugs.length;
  var now = new Date();
  var anyChanged = false;

  // Fix the backend returning dates mysteriously offset by 3 hours.
  fixTimestamps(bugs);

  // Get list of all tables containing bugs. We'll need this later.
  var tables = getTables('results');

  // Map field names onto a column of the tables
  var mapping = new Array();
  function colForField(field) {
    if (mapping[field]) {
      return mapping[field];
    } else {
      for (var i = 0; i < tables[0].tHead.rows[0].cells.length; i++) {
        var cell = tables[0].tHead.rows[0].cells[i];
        if (cell.getAttribute('field') == field) {
          mapping[field] = cell.cellIndex;
          return mapping[field];
        }
      }
    }
    return -1;
  }

  // Now for every new bug, look for differences.
  for (var i = 0; i < bugs.length; i++) {
    var bugid = bugs[i].getAttribute('identifier');
    newBugs.push(bugid);
    var oldLine = document.getElementById(bugid);
    var fields = bugs[i].getElementsByTagName('field');

    if (oldLine) {
      for (var j = 0; j < fields.length; j++) {
        var field = fields[j].getAttribute('name');
        var colIndex = colForField(field);
        // If there is an attribute for this field, then update it.
        if (oldLine.hasAttribute(field)) {
            oldLine.setAttribute(field, fields[j].textContent.trim());
        }
        
        // Now check whether this field is displayed
        if (colIndex != -1) {
          // There may be a span of class tiqitTextValue containing the value
          var parent = oldLine.cells[colIndex];
          if (oldLine.cells[colIndex].getElementsByClassName('tiqitTextValue').length > 0) {
            parent =  oldLine.cells[colIndex].getElementsByClassName('tiqitTextValue')[0];
          }
         
          var cellChanged = false;
          var newlyLoaded = false
          var suppress = false;
          var oldVal;
          if (oldLine.cells[colIndex].tiqitEditing) {
            oldVal = oldLine.cells[colIndex].tiqitEditor.input.value;
          } else {
            oldVal = parent.textContent;
          }
         
          var newVal = fields[j].textContent.trim();

          if (oldLine.cells[colIndex].tiqitChanged) {
            // This field has changed. We need to mark it purple
            // Don't update anything though.
            oldLine.cells[colIndex].style.outline = 'solid purple 2px';
            sendMessage(0, oldLine.id + " has changed but you are editing a field. Revert your changes, refresh the bug list, then try again.");
            suppress = true;
          }
         
          // If the field is disabled do not display any updates for it
          if (oldLine.cells[colIndex].tiqitEditor
              && oldLine.cells[colIndex].tiqitEditor.input.disabled) {
              suppress = true;
          }

          if (!suppress && (!newVal || oldVal != newVal) &&
              parent.getElementsByClassName('tiqitSaver')[0]) {
            newlyLoaded = true
          }

          if (oldVal != newVal && !suppress) {
            //sendMessage(0, bugid + ": Change to field " + field + ". Old value is '" + oldVal + "' and the new value is '" + newVal + "'.");
         
            if (oldLine.cells[colIndex].tiqitEditing) {
              oldLine.cells[colIndex].tiqitEditor.input.value = newVal;
              oldLine.cells[colIndex].tiqitVal = newVal;
            } else {
              while (parent.firstChild) {
                parent.removeChild(parent.firstChild);
              }
              parent.appendChild(getFieldDisplay(field, newVal));
            }
         
            // Some fields we may not actually want to display the changes for
            if (!allFields[field].volatile &&
                !oldLine.cells[colIndex].tiqitUpdateSuppress) {
              oldLine.cells[colIndex].style.outline = 'solid red 2px';
              oldLine.cells[colIndex].style.backgroundColor = 'rgb(255, 240, 220)';
         
              // If there isn't a title yet, add one
              if (!oldLine.cells[colIndex].title) {
                oldLine.cells[colIndex].title = 'Value was initially "' + oldVal + '"';
              }
         
              markBug(bugid,
                      new Date(oldLine.getAttribute('lastupdate')));
            } else {
              delete oldLine.cells[colIndex].tiqitUpdateSuppress;
              //sendMessage(1, "Suppressing update to " + bugid + " for field " + fields[j].getAttribute('name'));
            }

            cellChanged = true;
          } else if (!suppress && !newVal) {
            // There is no new value. Make sure there's nothing (like a 'loading'
            // icon) in the cell.
            //sendMessage(1, "No change (or suppressed) for bug " + bugid + ". Old val is: " + oldVal + "; New val is: " + newVal);
            var saver = parent.getElementsByClassName('tiqitSaver')[0];
            if (saver) {
              parent.removeChild(saver);
            }
          }

          // Tell folks about the change. Detect the case where a cell has just
          // loaded.
          if (cellChanged || newlyLoaded) {
            var tgt = new Object();
            tgt.row = oldLine;
            tgt.cell = oldLine.cells[colIndex];
            if (newlyLoaded) {
                tgt.oldValue = undefined;
            } else {
                tgt.oldValue = oldVal;
            }
            tgt.newValue = newVal;
            generateCustomEvent('CellChanged', tgt);
            anyChanged = true;
          }
        }
      }

      // If none of the visible fields have changed, but a hidden one has
      // then display a dashed line
      if (bugs[i].getAttribute('lastupdate') != oldLine.getAttribute('lastupdate')) {
        if (!contains(updatedBugs, bugid)) {
          oldLine.style.outline = 'dashed red 2px';
          oldLine.style.backgroundColor = 'rgb(255, 240, 220)';
          oldLine.title = 'A field not displayed in this query has changed';
        }
        markBug(bugid,
                new Date(oldLine.getAttribute('lastupdate')));

        // Also update the marked lastupdate time so we don't keep marking
        // this bug as changed.
        if (!suppress) {
          oldLine.setAttribute('lastupdate', bugs[i].getAttribute('lastupdate'));
        }
      }

      // Also remove any opacity, in case this bug had previously gone and
      // is now back.
      if (oldLine.isRemoved) {
        oldLine.isRemoved = false;
        oldLine.style.outline = 'solid red 2px';
        oldLine.style.backgroundColor = 'rgb(255, 240, 220)';
      }
    } else {
      // This is a brand new bug. Add a new line for it.
      // We'll re-filter and group at the end, so just stick it in first
      // table.
      var cell, span;

      // If there were no bugs previously then the table will have a placeholder
      // row to ensure the table is still rendered. This placeholder is no
      // longer needed as we now have bugs to show
      // If the table contains a placeholder row, delete it
      var placeholder = document.getElementById("resultsTablePlaceholderRow")
      if (placeholder) {
        placeholder.parentNode.removeChild(placeholder);
      }

      // Similarly, remove the no results warning if it exists
      var pNoResWarn = document.getElementById("noResultsWarning")
      if (pNoResWarn) {
          pNoResWarn.remove();
      }

      var row = tables[0].tBodies[0].insertRow(-1);
      row.style.outline = 'solid red 2px';
      row.style.backgroundColor = 'rgb(255, 240, 220)';
      row.id = bugid;
      row.setAttribute('lastupdate', bugs[i].getAttribute('lastupdate'));
      row.title = 'This bug appeared in your query at about ' + zeropad(now.getHours()) + ':' + zeropad(now.getMinutes());

      // Ensure fields are in the right place! Since they can be moved around,
      // we can't just add them in the order they are returned.
      // Be careful to check for gaps. These could be fields just added, but
      // not present in this update. Add an empty cell for them.
      var cells = new Array();

      for (var j = 0; j < fields.length; j++) {
        var field = fields[j].getAttribute('name');
        var colIndex = colForField(field);
        cell = document.createElement('td');
        span = document.createElement('span');
        span.className = 'tiqitTextValue';
        span.appendChild(getFieldDisplay(field, fields[j].textContent.trim()));
        cell.appendChild(span);

        cells[colIndex] = cell;
      }

      // Now add the new cells to the row
      for (var j = 0; j < cells.length; j++) {
        // Here's where we insert blank cells
        if (!cells[j]) {
          cells[j] = row.insertCell(-1);
        } else {
          row.appendChild(cells[j]);
        }
      }

      generateCustomEvent("RowAdded", row);

      markBug(bugid,
              new Date(row.getAttribute('lastupdate')));
      anyChanged = true;
    }
  }

  // So we've modified changed bugs, and added new ones. Remove old ones now.
  for (var i = 0; i < tables.length; i++) {
    for (var j = 0; j < tables[i].tBodies.length; j++) {
      for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
        var bugid = tables[i].tBodies[j].rows[k].id;
        if (!contains(newBugs, bugid)) {
          // Lost a bug!
          //sendMessage(0, "Bug has disappeared! " + bugid);
          tables[i].tBodies[j].rows[k].isRemoved = true;
          tables[i].tBodies[j].rows[k].title = 'This bug disappeared from your query at about ' + zeropad(now.getHours()) + ':' + zeropad(now.getMinutes());

          markBug(bugid,
                  new Date(tables[i].tBodies[j].rows[k]
                           .getAttribute('lastupdate')));
          anyChanged = true;
        }
        setRowOpacity(tables[i].tBodies[j].rows[k]);
      }
    }
  }

  if (anyChanged) {
    // Do bulk "table changed" event, if anything changed.
    var tgt = new Object();
    tgt.name = 'results';
    generateCustomEvent('TableChanged', tgt);
  }

  //sendMessage(1, "Loaded updated data at " + now.getHours() + ":" + now.getMinutes() + "." + now.getSeconds() + ". There are now " + event.target.responseXML.getElementsByTagName('bug').length + " bugs.");

  if (updatedBugs.length > changes) {
    // Display a message allowing them to cancel.
    var message = document.getElementById('tiqitResultsUpdateMessage');

    if (!message) {
      message = sendMessage(1, "Bug list updated");
      message.id = 'tiqitResultsUpdateMessage';

      var clear = document.createElement('img');
      clear.addEventListener('click', clearUpdates, false);
      clear.src = 'images/tick-small.png';
      clear.setAttribute('title', 'Clear marks on updated bugs');
      clear.style.cssFloat = 'right';

      var filter = document.createElement('img');
      filter.addEventListener('click', filterUpdated, false);
      filter.src = 'images/filter-small.png';
      filter.title = 'Clear current filters and show only changed bugs';
      filter.style.cssFloat = 'right';

      message.insertBefore(clear, message.firstChild);
      message.insertBefore(filter, message.firstChild);
    }

    updateResultsUpdateMessage(message);

    var clearer = document.getElementById('tiqitClearUpdates');
    clearer.style.display = 'list-item';
  }

  updateLastUpdateTime(now);
}

function updateLastUpdateTime(now) {
  var last = document.getElementById('tiqitLastUpdateTime');
  last.textContent = 'Last updated at ' + zeropad(now.getHours()) + ':' + zeropad(now.getMinutes());
}

function onLoad(event) {
  if (event.target.status == 200 && event.target.responseXML) {
    var bugs = event.target.responseXML.getElementsByTagName('bug');
    var msgs = event.target.responseXML.getElementsByTagName('message');

    Tiqit.handleXMLMessages(event.target.responseXML);

    // Occasionally, the backend breaks. This will produce a message, but no
    // results. Let's assume that if msgs.length > 0 but bugs.length == 0 then
    // things broke, and we should just wait for the next update.
    if (bugs.length > 0 || msgs.length == 0) {
      processUpdatedBugList(bugs);
    }

    // Some other people might care about this update
    generateCustomEvent("BugListRefreshed", event.target);

  } else {
    sendMessage(2, "Failed to load updated data. Error " + event.target.status + '. A retry has been scheduled.');
  }

  if (currentTimer) {
    currentTimer = null;
    startMonitoring();
  }

  resetRefresh();
}

function startMonitoring() {
  if (currentTimer) {
    return;
  }

  currentTimer = setTimeout(refreshNow, 1800000);

  var note = document.getElementById('tiqitAutoRefreshToggle');
  note.removeChild(note.lastChild);
  note.appendChild(document.createTextNode('Stop automatic refresh'));
  note.onclick = stopMonitoring;
  note.firstChild.src = 'images/stop-small.png';
  note.title = 'Stop automatically refreshing this query';
}

function stopMonitoring() {
  if (currentTimer) {
    clearTimeout(currentTimer);
    currentTimer = null;

//    var note = document.getElementById('tiqitRefreshNow');
//    note.removeChild(note.lastChild);
//    note.appendChild(document.createTextNode('Refresh results now'));
//    note.onclick = refreshNow;
//    note.title = 'Check for changes to the current query now';
//    note.firstChild.src = 'images/refresh-small.png';

    note = document.getElementById('tiqitAutoRefreshToggle');
    note.removeChild(note.lastChild);
    note.appendChild(document.createTextNode('Start automatic refresh'));
    note.onclick = startMonitoring;
    note.firstChild.src = 'images/play-small.png';
    note.title = 'Start automatically refreshing this query';
  }
}

function refreshNow() {
  if (currentTimer) {
    clearTimeout(currentTimer);
  }

  var note = document.getElementById('tiqitRefreshNow');
  note.removeChild(note.lastChild);
  note.appendChild(document.createTextNode('Refreshing...'));
  note.onclick = null;
  note.title = 'Refreshing query results. Please wait...';
  note.style.textDecoration = 'none';
  note.style.color = 'black';
  note.firstChild.src = 'images/refresh-loading.gif';

  document.getElementById('tiqitResultsAutoUpdate').getElementsByTagName('img')[0].src = 'images/loading.gif';

  //var url = window.location.protocol + '//' + window.location.host + window.location.pathname ;
  //if (window.location.search) {
  //  url += window.location.search.replace('&format=normal', '') + '&format=xml';
  //} else {
  //  url += '?format=xml';
  //}
  var url = document.baseURI + 'results?' + tiqitSearchQuery.replace('&format=normal', '') + '&format=xml&requested_by=tiqit_update_results';

  var req = new XMLHttpRequest();
  //currentRequest.onprogress = onProgress;
  req.open("GET", url, true);
  req.onload = onLoad;
  req.onerror = onError;
  req.send(null);

  generateCustomEvent("BugListRefresh", null);
}

function initAutoUpdateMenu() {
  var menu = document.createElement('div');
  menu.id = 'tiqitResultsAutoUpdate';
  menu.className = 'tiqitMenu';

  var img = document.createElement('img');
  img.src = 'images/clock-small.png';
  img.alt = '[Update]';
  menu.appendChild(img);

  var list = document.createElement('ul');
  menu.appendChild(list);

  var item = document.createElement('li');
  item.id = 'tiqitLastUpdateTime';
  list.appendChild(item);

  item = document.createElement('li');
  item.id = 'tiqitRefreshNow';
  item.className = 'tiqitMenuAction';
  item.addEventListener('click', refreshNow, false);
  item.title = 'Check for changes to the current query now';
  list.appendChild(item);

  img = document.createElement('img');
  img.src = 'images/refresh-small.png';
  img.alt = '[Refresh]';
  item.appendChild(img);

  item.appendChild(document.createTextNode('Refresh results now'));

  item = document.createElement('li');
  item.id = 'tiqitAutoRefreshToggle';
  item.className = 'tiqitMenuAction';
  item.onclick = startMonitoring;
  item.title = 'Start automatically refreshing this query';
  list.appendChild(item);

  img = document.createElement('img');
  img.src = 'images/play-small.png';
  img.alt = '[Toggle]';
  item.appendChild(img);

  item.appendChild(document.createTextNode('Start automatic refresh'));

  item = document.createElement('li');
  item.id = 'tiqitClearUpdates';
  item.className = 'tiqitMenuAction';
  item.addEventListener('click', clearUpdates, false);
  item.title = 'Clear marks on updated bugs';
  item.style.display = 'none';
  list.appendChild(item);

  img = document.createElement('img');
  img.src = 'images/tick-small.png';
  img.alt = '[Accept]';
  item.appendChild(img);

  item.appendChild(document.createTextNode('Clear updates'));

  var container = document.getElementById('tiqitMenus');
  container.appendChild(menu);

  updateLastUpdateTime(new Date());
}

addCustomEventListener("FirstWindowLoad", initAutoUpdateMenu);

var images = new Array('images/refresh-small.png', 'images/tick-small.png', 'images/delete-small.png', 'images/play-small.png', 'images/refresh-loading.gif', 'images/error-small.png', 'images/clock-small.png');
var imgs = new Array();

function preloadImages() {
  var img;
  for (var i = 0; i < images.length; i++) {
    img = new Image(16, 16);
    img.src = images[i];
    imgs.push(img);
  }
}

addCustomEventListener("FirstWindowLoad", preloadImages);

addCustomEventListener("FirstWindowLoad", function() {
  if (Tiqit.prefs['miscNeverAutoRefreshResults'] == 'false') {
    startMonitoring();
  }
});
