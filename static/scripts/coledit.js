//
// Add/remove results columns.
//

Tiqit.coledit = (function() {

function tiqitColsCreateNewColMenuItem(existingFields, eleType = 'li', withlabel=false) {
  var li = document.createElement(eleType);
  if (withlabel) {
    var label = document.createElement('label');
    label.for = "addnewcol-select";
    label.appendChild(document.createTextNode("Add New Column "));
    li.appendChild(label);
  }
  var sel = document.createElement('select');
  sel.id = 'addnewcol-select'

  var opt = document.createElement('option');
  opt.appendChild(document.createTextNode('Choose a field'));
  opt.value = '';
  sel.appendChild(opt);

  for (var i in allViewableFields) {
    var field = allViewableFields[i];

    if (!contains(existingFields, field)) {
      opt = document.createElement('option');
      opt.value = field;
      opt.appendChild(document.createTextNode(field));
      sel.appendChild(opt);
    }
  }

  sel.addEventListener('change', tiqitColsAddNewCol, false);

  li.appendChild(sel);

  return li;
}

function tiqitColsRegroupHandler(event) {
  var tableName = event.target;
  var tables = getTables(tableName);

  if (tables.length == 0) {
    return;
  }

  tiqitColsCreateMenus(tables);
}

function tiqitColsCreateMenus(tables) {
  for (var i = 0; i < tables.length; i++) {
    var parent, item;

    var parent = tables[i].tiqitColMenu;

    if (parent) {
      while (parent.childNodes.length > 0) {
        parent.removeChild(parent.firstChild);
      }
    } else {
      parent = tiqitTableAddSubmenu(tables[i], 'images/column_preferences-small.png', '[Cols]', 'Display the column select menu');
      parent.className = 'tiqitColEditMenu';
      tables[i].tiqitColMenu = parent;
    }

    tiqitTableAddSubmenuItem(parent, 'Select Visible Columns');

    var existingCols = new Array();
    for (var j = 0; j < tables[i].tHead.rows[0].cells.length; j++) {
      var head = tables[i].tHead.rows[0].cells[j];
      var field = head.getAttribute('field');

      item = tiqitTableAddSubmenuItem(parent, field, tiqitColToggleFieldVisible);
      if (head.style.display != 'none') {
        item.tiqitCheckbox.checked = true;
      }

      var img = document.createElement('img');
      img.src = 'images/up-blue-small.png';
      img.title = 'Move column up';
      img.className = 'tiqitColEditMoverUp';
      img.addEventListener('click', tiqitColMoveUp, false);

      item.insertBefore(img, item.firstChild);

      var img = document.createElement('img');
      img.src = 'images/down-blue-small.png';
      img.title = 'Move column down';
      img.className = 'tiqitColEditMoverDown';
      img.addEventListener('click', tiqitColMoveDown, false);

      item.insertBefore(img, item.firstChild);

      existingCols.push(field);
    }

    let existingnewcol = document.getElementById('addnewcol');
    if (existingnewcol != null) {
      // Clear any existing content
      while (existingnewcol.hasChildNodes()) {
        existingnewcol.removeChild(existingnewcol.firstChild);
      }
      item = tiqitColsCreateNewColMenuItem(existingCols, 'div', true);
      item.style.float = "right";
      existingnewcol.appendChild(item);
    } else {
      item = tiqitTableAddSubmenuItem(parent, 'Add New Column');

      item = tiqitColsCreateNewColMenuItem(existingCols);
      parent.appendChild(item);
    }
  }
}

addCustomEventListener('TableRegroup', tiqitColsRegroupHandler);

//
// Event Handlers
//

function tiqitColsAddNewCol(event) {
  //sendMessage(1, "Adding new column: " + event.currentTarget.value);
  var field = event.currentTarget.value;
  // Make sure something has been selected
  if (field) {
    // Several things to do:
    // - Create a new column in every row of every table
    // - Re-create the add col Menu
    // - Do some magic to make the auto-updater know about the new field
    // - Force a background reload to get the first info
    // - Suppress initial diffs for this col (but only this col)

    var tables = getTables('results');
    var newIndex = -1;
    for (var i = 0; i < tables.length; i++) {
      var cell = document.createElement('th');
      cell.setAttribute('field', field);
      var item = document.createElement('a');
      // Use attributes rather than explicit events as we will clone this field
      // on regrouping using cloneNode. cloneNode does not copy event handlers,
      // but does copy attributes.
      item.setAttribute('onclick', 'sortResults(event);');
      item.appendChild(document.createTextNode(allFields[field].shortname));
      cell.appendChild(item);

      if (newIndex == -1) {
        newIndex = tables[i].tHead.rows[0].cells.length + 1;
      }

      tables[i].tHead.rows[0].appendChild(cell);

      for (var j = 0; j < tables[i].tBodies.length; j++) {
        for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
          var row = tables[i].tBodies[j].rows[k];
          cell = document.createElement('td');
          cell.tiqitUpdateSuppress = true;

          var img = document.createElement('img');
          img.src = 'images/saver.gif';
          img.alt = '[Loading]';
          img.title = 'Fetching initial. Please wait...';
          img.width = 16;
          img.height = 16;
          img.style.display = 'block';
          img.style.margin = 'auto';
          img.className = 'tiqitSaver';
          cell.appendChild(img);

          row.insertBefore(cell, row.lastChild);
        }
      }
    }

    tiqitColsCreateMenus(tables);

    tiqitSearchQuery += '&selection' + newIndex + '=' + field;

    // Tell the world about it
    var tgt = new Object();
    tgt.field = field;
    tgt.tableName = 'results';
    generateCustomEvent('NewCol', tgt);

    refreshNow();
  }
}

function tiqitColToggleFieldVisible(event) {
  var table = getAncestorOfType(event.currentTarget, 'TABLE');
  var field = event.currentTarget.parentNode.textContent;

  // Find the relevant column
  var colIndex = -1;
  for (var i = 0; i < table.tHead.rows[0].cells.length; i++) {
    var head = table.tHead.rows[0].cells[i];
    if (head.getAttribute('field') == field) {
      colIndex = i;
      break;
    }
  }

  if (colIndex == -1) {
    sendMessage(2, "Can't find column with name '" + field + "'.");
    return;
  }

  var display = event.currentTarget.checked ? '' : 'none';

  // Right. Let's go through every row in the table
  for (var i = 0; i < table.rows.length; i++) {
    table.rows[i].cells[colIndex].style.display = display;
  }
}

function tiqitColMoveUp(event) {
  var col = getAncestorOfType(event.target, 'LI');
  var field = col.textContent;

  // Move the column in each table.
  // Find the index in the first table only
  var tables = getTables('results');

  var colIndex = -1;
  for (var i = 0; i < tables[0].tHead.rows[0].cells.length; i++) {
    var head = tables[0].tHead.rows[0].cells[i];
    if (head.getAttribute('field') == field) {
      colIndex = i;
      break;
    }
  }

  if (colIndex == -1) {
    sendMessage(2, "Can't find column with name '" + field + "'.");
    return;
  }

  if (colIndex == 0) {
    sendMessage(2, "Can't move the first column any further up.");
    return;
  }

  // Let's do it
  for (var i = 0; i < tables.length; i++) {
    for (var j = 0; j < tables[i].rows.length; j++) {
      var cell = tables[i].rows[j].cells[colIndex];
      tables[i].rows[j].insertBefore(cell, cell.previousSibling);
    }
  }

  // Now let's update the menus
  tiqitColsCreateMenus(tables);
}

function tiqitColMoveDown(event) {
  var col = getAncestorOfType(event.target, 'LI');
  var field = col.textContent;

  // Move the column in each table.
  // Find the index in the first table only
  var tables = getTables('results');

  var colIndex = -1;
  for (var i = 0; i < tables[0].tHead.rows[0].cells.length; i++) {
    var head = tables[0].tHead.rows[0].cells[i];
    if (head.getAttribute('field') == field) {
      colIndex = i;
      break;
    }
  }

  if (colIndex == -1) {
    sendMessage(2, "Can't find column with name '" + field + "'.");
    return;
  }

  if (colIndex == (tables[0].tHead.rows[0].cells.length - 1)) { 
    sendMessage(2, "Can't move the last column any further down.");
    return;
  }

  // Let's do it
  for (var i = 0; i < tables.length; i++) {
    for (var j = 0; j < tables[i].rows.length; j++) {
      var cell = tables[i].rows[j].cells[colIndex];
      if (tables[i].rows[j].lastChild == cell.nextSibling) {
        tables[i].rows[j].appendChild(cell);
      } else {
        tables[i].rows[j].insertBefore(cell, cell.nextSibling.nextSibling);
      }
    }
  }

  // Now let's update the menus
  tiqitColsCreateMenus(tables);
}

})();
