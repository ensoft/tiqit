//
// This is just a helper module that sets up tables for use by some of the
// other features.
//

//
// This file defines the following properties for elements:
//
// TABLE:
// - tiqitActionsMenu: a <span> in the <caption>. Left aligned, always visible
//
// TR:
// - tiqitActionsMenu: a <td> at the end.

function tiqitTableReInit(tableName) {
  var tables = getTables(tableName);

  for (var i = 0; i < tables.length; i++) {
    // Add a span for 'actions' to the table caption
    var span = document.createElement('span');
    span.className = 'tiqitTableActions';
    tables[i].caption.insertBefore(span, tables[i].caption.firstChild);
    tables[i].caption.tiqitActionsMenu = span;
    span.style.zIndex = 1000 - i;

    // Now for each row, add an actions column
    for (var j = 0; j < tables[i].tBodies.length; j++) {
      for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
        var row = tables[i].tBodies[j].rows[k];

        tiqitTableRowInit(row);
      }
    }
  }
}

function tiqitTableRowInit(row) {
  if (!row.tiqitActionsMenu) {
    var cell = row.insertCell(-1);
    cell.className = 'tiqitTableRowActions';

    row.tiqitActionsMenu = cell;
  }
}

function tiqitTableInit(tableName, filterable, groupable) {
  tiqitTableReInit(tableName);
  if (groupable) {
    filterGroupBy(tableName);
  } else if (filterable) {
    filterTable(tableName);
  }
}

addCustomEventListener('RowAdded', function(event) {
  tiqitTableRowInit(event.target);
});

addCustomEventListener('TableRegroup', function(event) {
  tiqitTableReInit(event.target);
});

//
// Table Menu functions
//
// These set up items in the per-table (in-caption) menu

function tiqitTableAddAction(table, img, alt, title, handler) {
  var span = table.caption.tiqitActionsMenu;
  var item;

  if (!span) {
    sendMessage(0, "Trying to add action to table '" + table.id + "' but it has no actions menu.");
    return;
  }

  item = document.createElement('img');
  item.src = img;
  item.alt = alt;
  item.title = title;
  item.className = 'tiqitTableMenuItem';
  item.addEventListener('click', handler, false);
  span.appendChild(item);

  return item;
}

function tiqitTableAddSubmenu(table, img, alt, title) {
  var span = table.caption.tiqitActionsMenu;

  if (!span) {
    sendMessage(0, "Trying to add menu to table '" + table.id + "' but it has no actions menu.");
    return;
  }

  var parent = document.createElement('div');
  parent.className = 'tiqitTableMenuItemWithMenu tiqitTableMenuItem';
  span.appendChild(parent);

  var item = document.createElement('img');
  item.src = img;
  item.alt = alt;
  item.title = title;
  parent.appendChild(item);

  item = document.createElement('div');
  item.className = 'tiqitTableMenuItemMenu';
  parent.appendChild(item);

  parent = item;

  // Close icon
  item = document.createElement('img');
  item.src = 'images/close-12.png';
  item.alt = '[x]';
  item.title = 'Close menu';
  item.addEventListener('click', tiqitTableCloseMenu, false);
  parent.appendChild(item);

  // Now the actual list
  item = document.createElement('ul');
  parent.appendChild(item);

  parent = item;

  return parent;
}

function tiqitTableAddSubmenuItem(menu, text, handler) {
  var li = document.createElement('li');
  var label = document.createElement('label');
  var cb = document.createElement('input');
  cb.type = 'checkbox';
  if (handler) {
    cb.addEventListener('change', handler, false);
    cb.tiqitHandler = handler;
  } else {
    li.className = 'tiqitTableMenuTitle';
  }
  label.appendChild(cb);
  label.appendChild(document.createTextNode(text));
  li.appendChild(label);

  menu.appendChild(li);

  li.tiqitCheckbox = cb;

  return li;
}

//
// Menu helper functions
//

function tiqitTableResetMenu(event) {
  event.target.parentNode.style.display = null;
}
function tiqitTableCloseMenu(event) {
  event.target.parentNode.style.display = 'none';
  setTimeout(tiqitTableResetMenu, 100, event);
}

//
// Utility functions
//

// getTables()
// 
// Return all tables with a particular ID.
// 
// tableName: The ID to search for.
// 
function getTables(tableName) {
  var tables = new Array();

  var resTable = document.getElementById(tableName);

  if (resTable) {
    tables.push(resTable);
    resTable = null;
  } else {
    var allTs = document.getElementsByTagName('table');

    for (var i = 0; i < allTs.length; i++) {
      if (allTs[i].id.indexOf(tableName) == 0) {
        tables.push(allTs[i]);
      }
    }
  }

  return tables;
}

