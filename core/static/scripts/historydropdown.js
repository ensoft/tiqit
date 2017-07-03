//
// History drop-down box
// 

var historyDropDownMaxTextLength = 25;

// repositionPopup()
//
// Position the popup so it is to the left of it's icon,
function repositionPopup(popup, icon) {
  var commonAncestor = popup.offsetParent;
  var iconAncestor = icon;

  var left = 0;
  var top = 0;
  while (iconAncestor != commonAncestor) {
    left += iconAncestor.offsetLeft;
    top += iconAncestor.offsetTop;
    iconAncestor = iconAncestor.offsetParent;
  }

  popup.style.top = (top - 16) + "px";
  popup.style.right = (commonAncestor.offsetWidth - left - 16) + "px";
}


// createHistoryTable()
//
// Create an empty table to put the history in,
function createHistoryTable() {
  var table = document.createElement('table');
  var fields = new Array("When", "Who", "What", "Action");

  table.setAttribute('id', 'historyTable');
  table.setAttribute('class', 'tiqitTable historyDropDownNarrowTable');

  var tableHead = document.createElement('thead');
  var row = document.createElement('tr');
  for (i in fields) {
    var th = document.createElement('th');
    th.appendChild(document.createTextNode(fields[i]));
    row.appendChild(th);
  }
  tableHead.appendChild(row);

  var tableBody = document.createElement('tbody');
  table.body = tableBody;

  table.appendChild(tableHead);
  table.appendChild(tableBody);

  return table;
}


// historyDataFailed()
//
// Set the ticker to an error icon, and output an error message.
function historyDataFailed(content) {
  if (content.ticker != null) {
    content.ticker.img.src = 'static/images/error.png';
    content.ticker.img.alt = '[Error]';
    content.ticker.text.textContent = "Unable to get history due to a networking error. Reactivate the popup to retry.";
  }
  content.error = true;
}


// historyDataFromXML()
//
// Extract an array of history items from an XML document. Each element of the
// array is a hash of (field name, field value) pairs.
// 
// Return: The extracted history data.
// 
// doc: The XML document to extract data from.
function historyDataFromXML(doc) {
  var historyItemNodes = doc.getElementsByTagName('historyitem');
  var history = new Array();

  for (var i = 0; i < historyItemNodes.length; i++) {
    var historyItemNode = historyItemNodes[i];
    var fieldNodes = historyItemNode.childNodes;
    var historyItem = new Array();
    for (var j = 0; j < fieldNodes.length; j++) {
      if (fieldNodes[j].nodeType === Node.ELEMENT_NODE) {
        var fieldName = fieldNodes[j].tagName;
        var fieldValue = fieldNodes[j].textContent;
        historyItem[fieldName] = fieldValue;
      }
    }
    history.push(historyItem);
  }

  return history;
}


// historyDataDisplay()
// 
// Create an element to represent some history data.
// 
// Return: The created element.
// 
// history: The history data.
function historyDataDisplay(history, highlightAfter) {
  // Create empty table with headings "When", "Who", "What", "Action"
  var table = createHistoryTable();

  // Helper functions
  function createTableCell(content) {
    var td = document.createElement('td');
    td.appendChild(content);
    return td;
  }
  function createValueText(text) {
    var strong = document.createElement('strong');
    if (text.length > historyDropDownMaxTextLength) {
      shortText = text.substr(0, historyDropDownMaxTextLength - 1) + "...";
      strong.title = text;
    } else {
      shortText = text;
    }
    strong.appendChild(document.createTextNode(shortText));
    return strong;
  }

  var oldHistoryRows = new Array();

  // Add each history item, one per row.
  for (i in history) {
    var historyItem = history[i];
    var row = document.createElement('tr');

    row.appendChild(createTableCell(
      document.createTextNode(historyItem['Date'])));
    row.appendChild(createTableCell(
      getFieldDisplay("Engineer", historyItem['User'])));
    row.appendChild(createTableCell(
      document.createTextNode(historyItem['Field'])));

    var actionCell = document.createElement('td');
    if (historyItem['Operation'] == 'Delete') {
      // Produce "Deleted <Old Value>"
      actionCell.appendChild(document.createTextNode("Deleted "));
      actionCell.appendChild(createValueText(historyItem['OldValue']));
      actionCell.appendChild(document.createTextNode("."));
    } else if (historyItem['Operation'] == 'New Record') {
      if (historyItem['NewValue'] == "") {
        // Produce "Created."
        actionCell.appendChild(document.createTextNode("Created."));
      } else {
        // Produce "Created as <New Value>."
        actionCell.appendChild(document.createTextNode("Created as "));
        actionCell.appendChild(createValueText(historyItem['NewValue']));
        actionCell.appendChild(document.createTextNode("."));
      }
    } else if (historyItem['Operation'] == 'Modify') {
      if (historyItem['OldValue'] == "") {
        // Produce "Set to <New Value>."
        actionCell.appendChild(document.createTextNode("Set to "));
        actionCell.appendChild(createValueText(historyItem['NewValue']));
        actionCell.appendChild(document.createTextNode("."));
      } else {
        // Produce "Changed from <Old Value> to <New Value>."
        actionCell.appendChild(document.createTextNode("Changed from "));
        actionCell.appendChild(createValueText(historyItem['OldValue']));
        actionCell.appendChild(document.createTextNode(" to "));
        actionCell.appendChild(createValueText(historyItem['NewValue']));
        actionCell.appendChild(document.createTextNode("."));
      }
    } else {
      // This shouldn't happen. Just display the operation.
      actionCell.appendChild(
        document.createTextNode(historyItem['Operation']));
    }

    var historyItemDate = new Date(historyItem['Date']);

    if (historyItemDate.getTime() > highlightAfter.getTime()) {
      // Highlight rows which changed since last time the marks were cleared.
      row.style.opacity = 1;
      row.style.outline = 'solid red 2px';
      row.style.backgroundColor = 'rgb(255, 240, 220)';
    } else if (i >= 5) {
      // Hide rows which haven't changed, AND appeared more than 5 items ago.
      row.style.display = 'none';
      oldHistoryRows.push(row);
    }

    row.appendChild(actionCell);
    table.body.appendChild(row);
  }

  // Add an icon to toggle full/recent history.
  var headers = table.getElementsByTagName('th');
  var lastHeader = headers[headers.length - 1];
  var expandImg = document.createElement('img');
  expandImg.src = 'images/down-down-small.png';
  expandImg.alt = '[Toggle Full/Recent History]';
  expandImg.title = 'Toggle full/recent history';
  expandImg.className = 'tiqitFullHistoryToggleIcon';
  lastHeader.appendChild(expandImg);
  var showOldRows = false;
  expandImg.addEventListener("click", function() {
    showOldRows = !showOldRows;
    for (var i in oldHistoryRows) {
      var row = oldHistoryRows[i];
      row.style.display = showOldRows ? 'table-row' : 'none';
    }
    expandImg.src = showOldRows ? 'images/up-small.png' : 'images/down-down-small.png' ;
  }, false);

  return table;
}

function createTickerForBug(bugid) {
  var ticker = document.createElement('div');
  ticker.img = document.createElement('img')
  ticker.setAttribute('class', 'historyDropDownTicker');

  ticker.img.src = 'static/images/loading-horizontal.gif';
  ticker.img.alt = '[Loading]';
  ticker.text = document.createTextNode('Loading history...');
  ticker.appendChild(ticker.text);
  ticker.appendChild(document.createElement('br'));
  ticker.appendChild(ticker.img);

  return ticker;
}

// createHistoryContentForBug()
//
// Create history content to be displayed in the drop down.
function createHistoryContentForBug(bugid, icon, highlightAfter) {
  var content = document.createElement('div');
  content.setAttribute('class', 'historyDropDownContent');
  content.error = false;

  // Ticker, will be replaced when the result comes back.
  content.ticker = createTickerForBug(bugid);
  content.appendChild(content.ticker);
  content.table = null;
  icon.className = 'tiqitHistoryDropDownIconLoading';

  // Request the data
  var req = new XMLHttpRequest();
  var tiqitApi = new TiqitApi();
  function onload(event) {
      icon.className = 'tiqitHistoryDropDownIcon';
      if (event.target.status == 200 && event.target.responseXML) {
        if (content.ticker != null) {
          content.removeChild(content.ticker);
          content.ticker = null;
        }
        var history = historyDataFromXML(event.target.responseXML);
        var historyElement = historyDataDisplay(history, highlightAfter);
        content.appendChild(historyElement);
      } else {
        historyDataFailed(content);
      }
    };
  function onerror(event) {
    icon.className = 'tiqitHistoryDropDownIcon';
    historyDataFailed(content);
  };
  tiqitApi.historyForBugs([bugid], onload, onerror);
  return content;
}


function historyDropDownBugUpdated(historyDropDownMenu) {
  var popup = historyDropDownMenu.popup;
  if (popup.content !== undefined) {
    popup.removeChild(popup.content);
    popup.content = undefined;
  }
}


function createHistoryDropDownMenu(bugid, highlightAfter, onClearHandler) {
  var menu = document.createElement('div');
  var icon = document.createElement('img');
  var popup = document.createElement('div');

  icon.bugid = bugid;
  icon.title = 'Clear marks for this bug.';
  icon.src = 'images/transparent-1x1.png';
  icon.addEventListener('click', function(e) {
    onClearHandler(e);
  }, false);
  icon.className = 'tiqitHistoryDropDownIcon';

  popup.style.right = '0px';
  popup.style.top = '0px';
  popup.className = 'tiqitHistoryDropDownPopup'

  menu.appendChild(popup);
  menu.appendChild(icon);
  menu.popup = popup;
  menu.icon = icon;
  menu.className = "tiqitHistoryDropDownMenu";

  icon.addEventListener("mouseover", function(e) {
    repositionPopup(popup, icon);

    // If a previous attempt to load the data failed destroy the popup content
    // and try again.
    if (popup.content && popup.content.error) {
      popup.removeChild(popup.content);
      delete popup.content;
    }

    if (!popup.content) {
      popup.content = createHistoryContentForBug(bugid, icon, highlightAfter);
      popup.appendChild(popup.content);
    }
  }, false);

  return menu;
}
