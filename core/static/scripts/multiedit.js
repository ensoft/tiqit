//
// Multiple edits support. Yay. At last.
//

function regroupHandler(event) {
  var tableName = event.target;
  var tables = getTables(tableName);

  if (tables.length == 0) {
    return;
  }

  for (var i = 0; i < tables.length; i++) {
    // Now we add the new drop down to the table
    var parent, item;

    parent = tiqitTableAddSubmenu(tables[i], 'images/edit-small.png', '[Edit]', 'Display the edit menu');
    tables[i].tiqitMultiEditMenu = parent;

    item = tiqitTableAddAction(tables[i], 'images/save-16x16.png', '[Save]', 'Save all changes in this table', saveAll);
    item.style.display = 'none';
    tables[i].tiqitChanged = 0;
    tables[i].tiqitTableSaver = item;

    item = tiqitTableAddAction(tables[i], 'images/undo-16x16.png', '[Revert]', 'Revert all changes', revertAll);
    item.style.display = 'none';
    tables[i].tiqitTableUndoer = item;

    setTableCellChangedCount(tables[i]);

    tiqitTableAddSubmenuItem(parent, 'Field editing options');
    tiqitTableAddSubmenuItem(parent, 'Edit all fields', toggleAllFields);
    tiqitTableAddSubmenuItem(parent, 'Lock edits by field', toggleFieldLock);

    tiqitTableAddSubmenuItem(parent, 'Edit selected fields');

    for (var j = 0; j < tables[i].tHead.rows[0].cells.length; j++) {
      var head = tables[i].tHead.rows[0].cells[j];
      var field = head.getAttribute('field');
      if (head.style.display != 'none' && contains(allEditableFields, field)) {
        tiqitTableAddSubmenuItem(parent, field, toggleFieldHandler);
      }
    }

    // Add a double click event handler unless disabled in preferences
    if (Tiqit.prefs['miscDisableDblclkEdit'] == undefined ||
        Tiqit.prefs['miscDisableDblclkEdit'] == 'false') {
      tables[i].addEventListener('dblclick', function(event) {
        var cell = getAncestorOfType(event.target, 'TD');
        if (cell) {
          var row = getAncestorOfType(cell, 'TR');
          if (!row.tiqitSaving) {
            var table = getAncestorOfType(row, 'TABLE');
            var colIndex = cell.cellIndex;
            var field = table.tHead.rows[0].cells[colIndex].getAttribute('field');
            if (contains(allEditableFields, field)) {
              if (cell.tiqitEditing) {
                stopEditingCell(row, cell, field);
              } else {
                startEditingCell(row, cell, field);
              }
            }
          }
        }
      }, false);
    }
  }
}

function filterHandler(event) {
  // When the filter changes, we need to go through and update the editable
  // fields. In particular, clear edits for rows that no longer care, and
  // make editable those that do.
  var tableName = event.target;
  var tables = getTables(tableName);

  if (tables.length == 0) {
    return;
  }

  for (var i = 0; i < tables.length; i++) {
    for (var j = 0; j < tables[i].tBodies.length; j++) {
      for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
        var row = tables[i].tBodies[j].rows[k];
        for (var l = 0; l < row.cells.length; l++) {
          var cell = row.cells[l];
          var head = tables[i].tHead.rows[0].cells[l];

          // If there is no head, then it's not a real cell (action cell)
          if (head) {
            if (cell.tiqitEditing) {
              // We have to stop editing if the row is now hidden
              if (row.style.display == 'none') {
                stopEditingCell(row, cell, head.getAttribute('field'));
              }
            } else {
              // We have to start editing if the row is visible and the column
              // is being edited.
              if (row.style.display != 'none' && head.tiqitEditing) {
                startEditingCell(row, cell, head.getAttribute('field'));
              }
            }
          }
        }
        if (row.style.display == 'none') {
          row.tiqitEditing = false;
        }
      }
    }
  }
}

function tiqitMultiEditNewColHandler(event) {
  var tables = getTables(event.target.tableName);
  var tables = getTables('results');
  var colIndexParent = null;
  var colIndexTarget = null;
  var parent_cell = null;
  var field = allFields[event.target.field];

  for (var i = 0; i < tables.length; i++) {
    // Don't do the head of each table as we don't need attributes or editing
    // on this
    var table = tables[i];
    for (var l = 0; l < table.tBodies.length; l++) {
      var tBody = table.tBodies[l];
      for (var j = 0; j < tBody.rows.length; j++) {
        // First add a new attribute for all the parents and bannedIf fields
        // of this field so that it gets filled in when the data is retrieved
        for (bannedif in field.bannedif) {
          // If we already have an attribute leave it until we get the update 
          // (which may change the value)
          // Otherwise add one so it is saved when the update is received
          if (!tBody.rows[j].hasAttribute(bannedif)) {
              tBody.rows[j].setAttribute(bannedif, '');
          }
        }
        go_editing = false;
        for (parent in field.parentfields) {
            parent = field.parentfields[parent];
          // If we already have an attribute leave it until we get the update 
          // (which may change the value)
          // Otherwise add one so it is saved when the update is received
          if (!tBody.rows[j].hasAttribute(parent)) {
              tBody.rows[j].setAttribute(parent, '');
          }
          // Now if the parent is present and editing we should go editable as 
          // well (if we are an editable field)
          if (!go_editing && contains(allEditableFields, field.name)) {
            colIndexParent = null;
            for (var k = 0; k < table.tHead.rows[0].cells.length; k++) {
              if (table.tHead.rows[0].cells[k].getAttribute('field') == parent) {
                colIndexParent = k;
                break;
              }
            }
            parent_cell = null;
            if (colIndexParent) {
                parent_cell = tBody.rows[j].cells[colIndexParent];
            }
            if (parent_cell && parent_cell.tiqitEditing) {
                go_editing = true;
            }
          }
        }
        if (go_editing) {
            for (var k = 0; k < table.tHead.rows[0].cells.length; k++) {
              if (table.tHead.rows[0].cells[k].getAttribute('field') == field.name) {
                colIndexTarget = k;
                break;
              }
            }
            startEditingCell(tBody.rows[j], tBody.rows[j].cells[colIndexTarget], field.name);
        }
      }
    }
  }

  if (field.editable) {
    for (var i = 0; i < tables.length; i++) {
      tiqitTableAddSubmenuItem(tables[i].tiqitMultiEditMenu, event.target.field, toggleFieldHandler);
    }
  }
}

addCustomEventListener('TableRegroup', regroupHandler);
addCustomEventListener('TableFilter', filterHandler);
addCustomEventListener('NewCol', tiqitMultiEditNewColHandler);

//
// Event Handlers
//

function cancelRowSave(row) {
  row.tiqitSaving = false;
  row.style.backgroundColor = null;
  for (var i = 0; i < row.cells.length; i++) {
    if (row.cells[i].tiqitEditing) {
      if (!isCellBanned(row.cells[i])) {
        row.cells[i].tiqitEditor.input.disabled = false;
      }
    }
  }

  row.tiqitRowSaver.src = 'images/save-16x16.png';
  row.tiqitRowSaver.title = 'Save changes to this bug';
  row.tiqitRowSaver.alt = '[Save]';
}

function rowSaveFailed(event, row) {
  sendMessage(2, "Failed to save changes to " + row.id +". Likely this is due to a networking issue.");
  cancelRowSave(row);
}

function rowSaved(event, row) {
  if (event.target.status == 200 && event.target.responseXML) {
    var bugs = event.target.responseXML.getElementsByTagName('bug');
    for (var i = 0; i < bugs.length; i++) {
      var row = document.getElementById(bugs[i].getAttribute('identifier'));
      var table = getAncestorOfType(row, 'TABLE');
      var fields = event.target.responseXML.getElementsByTagName('field');
      cancelRowSave(row);
      row.setAttribute('lastupdate', bugs[i].getAttribute('lastupdate'));
      for (var j = 0; j < fields.length; j++) {
        for (var k = 0; k < table.tHead.rows[0].cells.length; k++) {
          var head = table.tHead.rows[0].cells[k];
          var field = head.getAttribute('field');
          if (field == fields[j].getAttribute('name')) {

            // Tell folks about the change
            var tgt = new Object();
            tgt.row = row;
            tgt.cell = row.cells[k];
            tgt.oldValue = row.cells[k].tiqitVal;
            tgt.newValue = fields[j].textContent;

            row.cells[k].tiqitVal = fields[j].textContent;
            stopEditingCell(row, row.cells[k], field);
            generateCustomEvent('CellChanged', tgt);
            if (head.tiqitEditing) {
              startEditingCell(row, row.cells[k], field);
            }

            var tgt = new Object();
            tgt.name = 'results';
            generateCustomEvent('TableChanged', tgt);
            break;
          }
        }
      }
    }
  } else if (event.target.responseXML) {
    var msgs = event.target.responseXML.getElementsByTagName('message');
    for (var i = msgs.length - 1; i >= 0; i--) {
      sendMessage(msgs[i].getAttribute('type'), msgs[i].textContent);
    }
    cancelRowSave(row);
  } else {
    sendMessage(2, "Failed to save changes to " + row.id + ": " + event.target.status);
    cancelRowSave(row);
  }
}

function doRowSave(row) {
  var table = getAncestorOfType(row, 'TABLE');
  var fields = new Array();

  var newval;
  var query = 'multiedit.py?Identifier=' + row.id;
  query += '&Sys-Last-Updated=' + row.getAttribute('lastupdate');

  // Go through and remove the editors, but display the new values and save the
  // old value in case of failure. Also build the query string, of course
  // If its already disabled we should not save it as it is not valid for this
  // bug
  for (var i = 0; i < row.cells.length; i++) {
    if (row.cells[i].tiqitEditing
        && !row.cells[i].tiqitEditor.input.disabled) {
      fields.push(table.tHead.rows[0].cells[i].getAttribute('field'));
      query += '&' + table.tHead.rows[0].cells[i].getAttribute('field');
      query += '=' + row.cells[i].tiqitEditor.input.value;

      row.cells[i].tiqitEditor.input.disabled = true;
    }
  }

  query += '&fields=' + fields.join(',');

  // Make this row uneditable
  row.tiqitSaving = true;
  row.style.backgroundColor = '#e8fddd';

  var req = new XMLHttpRequest();
  req.open('GET', query, true);
  req.onload = function(event) {
    rowSaved(event, row);
  }
  req.onerror = function(event) {
    rowSaveFailed(event, row);
  }
  req.send(null);

  row.tiqitRowSaver.src = 'images/saver.gif';
  row.tiqitRowSaver.title = 'Saving...';
  row.tiqitRowSaver.alt = 'Saving...';
}

function saveRow(event) {
  var row = getAncestorOfType(event.currentTarget, 'TR');
  doRowSave(row);
}

function saveAll(event) {
  var table = getAncestorOfType(event.currentTarget, 'TABLE');

  for (var i = 0; i < table.tBodies.length; i++) {
    for (var j = 0; j < table.tBodies[i].rows.length; j++) {
      if (table.tBodies[i].rows[j].tiqitChanged > 0) {
        doRowSave(table.tBodies[i].rows[j]);
      }
    }
  }
}

function revertAll(event) {
  var table = getAncestorOfType(event.currentTarget, 'TABLE');

  for (var i = 0; i < table.tBodies.length; i++) {
    for (var j = 0; j < table.tBodies[i].rows.length; j++) {
      var row = table.tBodies[i].rows[j];
      if (row.tiqitChanged > 0 && !row.tiqitSaving) {
        for (var k = 0; k < row.cells.length; k++) {
          var cell = row.cells[k];
          if (cell.tiqitEditing) {
            if (cell.tiqitChanged) {
              cell.tiqitEditor.input.value = cell.tiqitVal;
              clearCellChanged(cell);
            }
          }
        }
      }
    }
  }
}

function fieldChanged(event) {
  var cell = getAncestorOfType(event.currentTarget, 'TD');
  var table = getAncestorOfType(cell, 'TABLE');

  if (cell.tiqitVal == event.currentTarget.value) {
    clearCellChanged(cell);
  } else {
    markCellChanged(cell);
  }

  if (table.tiqitEditingLocked) {
    // Righty ho - see if any other cells in that column need updating
    // Temporarily disable locked editing to prevent excessive recursion
    table.tiqitEditingLocked = false;
    var row = getAncestorOfType(cell, 'TR');
    var colIndex = cell.cellIndex;
    for (var i = 0; i < table.tBodies.length; i++) {
      for (var j = 0; j < table.tBodies[i].rows.length; j++) {
        var otherRow = table.tBodies[i].rows[j];
        var otherCell = table.tBodies[i].rows[j].cells[colIndex];
        if (!otherRow.tiqitSaving && otherCell.tiqitEditing) {
          if (otherCell.tiqitEditor.input.value != event.currentTarget.value) {
            otherCell.tiqitEditor.input.value = event.currentTarget.value;
            fireEvent('change', otherCell.tiqitEditor.input);
          }
        }
      }
    }
    table.tiqitEditingLocked = true;
  }
}

//
// Keep track of number of edits
//

function markCellChanged(cell) {
  var row = getAncestorOfType(cell, 'TR');
  var table = getAncestorOfType(cell, 'TABLE');

  cell.style.outline = 'solid blue 2px';

  if (!cell.tiqitChanged) {
    cell.tiqitChanged = true;

    if (row.tiqitChanged == 0) {
      row.tiqitRowSaver.style.visibility = 'visible';
    }

    row.tiqitChanged++;

    if (table.tiqitChanged == 0) {
      table.tiqitTableSaver.style.display = 'inline';
      table.tiqitTableUndoer.style.display = 'inline';
    }

    table.tiqitChanged++;
  }
}

function clearCellChanged(cell) {
  var row = getAncestorOfType(cell, 'TR');
  var table = getAncestorOfType(cell, 'TABLE');

  if (cell.tiqitChanged) {
    cell.style.outline = 'none';

    row.tiqitChanged--;

    if (row.tiqitChanged == 0) {
      row.tiqitRowSaver.style.visibility = 'hidden';
    }

    table.tiqitChanged--;

    if (table.tiqitChanged == 0) {
      table.tiqitTableSaver.style.display = 'none';
      table.tiqitTableUndoer.style.display = 'none';
    }

    cell.tiqitChanged = false;
  }
}

// setTableCellChangedCount
//
// Count the number of changed cells in a table. Used after a regroup when
// the table may be newly created, thus the cell changed count needs to
// calculated from scratch.
//
// This function assumes the table's rows' counts are correct.
function setTableCellChangedCount(table) {
  table.tiqitChanged = 0;

  for (var i = 0; i < table.tBodies.length; i++) {
    for (var j = 0; j < table.tBodies[i].rows.length; j++) {
      var row = table.tBodies[i].rows[j];

      if (row.tiqitChanged) {
          table.tiqitChanged += row.tiqitChanged;
      }
    }
  }

  if (table.tiqitChanged == 0) {
    table.tiqitTableSaver.style.display = 'none';
    table.tiqitTableUndoer.style.display = 'none';
  } else {
    table.tiqitTableSaver.style.display = 'inline';
    table.tiqitTableUndoer.style.display = 'inline';
  }
}


//
// Edit Utility funcs
//

function stopEditingCell(row, cell, colName) {
  if (cell.tiqitChanged) {
    clearCellChanged(cell);
  }

  if (cell.tiqitEditing) {
    var parent = cell;
    var spans = getElementsByClassName('tiqitTextValue', cell);
    if (spans.length > 0) {
      parent =  spans[0];
    }

    while (parent.firstChild) {
      parent.removeChild(parent.firstChild);
    }

    parent.appendChild(getFieldDisplay(colName, cell.tiqitVal));
    cell.tiqitVal = null;
    cell.tiqitEditing = false;
    cell.tiqitEditor = null;

    stopEditingRow(row);
    sanitiseRow(row);
  }
}


function getFieldValueCommon(row, field) {
  var table = getAncestorOfType(row, 'TABLE');
  var colIndex;
  var cell;
  var parent;
  var spans;
  var value;

  // Get the field value off the page for this field 
  // If the field is not on the page use the attributes to find its value
  for (var i = 0; i < table.tHead.rows[0].cells.length; i++) {
    if (table.tHead.rows[0].cells[i].getAttribute('field') == field) {
      colIndex = i;
      break;
    }
  }
  if (colIndex) {
    // If we are editing this cell, then get the value from the editor
    // If not then get the original values
    cell = row.cells[colIndex];
    if (cell.tiqitEditing) {
      value = cell.tiqitEditor.input.value;
    } else {
      parent = cell;
      spans = getElementsByClassName('tiqitTextValue', cell);
      if (spans.length > 0) {
        parent =  spans[0];
      }
      // Save the current value
      value = parent.textContent;
    }
  } else {
    value = row.getAttribute(field);
  }

  return value;
}


function isCellBanned(cell) {
  var table = getAncestorOfType(cell, 'TABLE');
  var row = getAncestorOfType(cell, 'TR');
  var field;
  var banned = false;

  // Only check for cells that are actually fields in the table (not action
  //  buttons etc)
  if (cell.cellIndex < table.tHead.rows[0].cells.length) {
    field = allFields[table.tHead.rows[0].cells[cell.cellIndex].getAttribute('field')];
    for (bannedif in field.bannedif) {
      value = getFieldValueCommon(row, bannedif);
      if (contains(field.bannedif[bannedif], value)) {
        banned = true;
        break;
      }
    }
  }
  return banned;
}


function updateRowBanned(event) {
  var cell = getAncestorOfType(event.currentTarget, 'TD');
  var row = getAncestorOfType(cell, 'TR');
  // For each cell in the row, check whether it should be disabled

  for (var i = 0; i < row.cells.length; i++) {
    if (row.cells[i].tiqitEditing) {
      row.cells[i].tiqitEditor.input.disabled = isCellBanned(row.cells[i]);
    }
  }
}


function generateEditor(bugID, value, field) {
  // Generate a new editor for this bug and field with the specified value
  // selected initially
  var editor = getFieldEditor(function(f) {return getFieldValueMultiedit(f, bugID)}, field, 'tiqitEditor' + field + bugID, value);

  editor.input.addEventListener('change', fieldChanged, false);
  editor.input.addEventListener('keyup', fieldChanged, false);
  editor.input.addEventListener('change', updateChildrenMultiedit, false);
  editor.input.addEventListener('change', updateRowBanned, false);

  return editor
}


function regenerateEditor(cell, bugID, field) {
  var old_editor = cell.tiqitEditor;
  var parent = old_editor.parentNode;
  var editor;
  var original_value;
  var valsAreSame = true;

  // Regenerate the editor for this cell and field name for this bug
  // by removing the old one and generating a new one with the allowed values
  // This can be optimised by checking that the values are actually different
  // before regeneration
  original_value = old_editor.defaultValue;
  valsAreSame = allFields[field].checkInputOptions(
          function(f) {return getFieldValueMultiedit(f, bugID)}, old_editor);

  if (!valsAreSame) {
    editor = generateEditor(bugID, cell.tiqitEditor.value, field);

    editor.input.value = old_editor.defaultValue;
    editor.input.defaultValue = old_editor.defaultValue;
    parent.removeChild(old_editor);
    parent.appendChild(editor);
    cell.tiqitEditor = editor;
    if (editor.value != original_value) {
      markCellChanged(cell);
    } else {
      clearCellChanged(cell);
    }
  }
}


function updateChildrenMultiedit(event) {
  var ev = new Object();
  var child;
  var colIndex;
  var old_value;
  var cell = getAncestorOfType(event.currentTarget, 'TD');
  var table = getAncestorOfType(cell, 'TABLE');
  var row = getAncestorOfType(cell, 'TR');
  var field = allFields[table.tHead.rows[0].cells[cell.cellIndex].getAttribute('field')];
  var child_cell;

  for (child in field.childfields) {
    // Generate a new dropdown box with the correct allowed values based
    // on the new value of the field:

    // Get the old dropdown off the page
    // Need the column number of this child, plus the row of the current
    // field being edited
    colIndex = null;
    for (var i = 0; i < table.tHead.rows[0].cells.length; i++) {
      if (table.tHead.rows[0].cells[i].getAttribute('field') == field.childfields[child]) {
        colIndex = i;
        break;
      }
    }
    child_cell = null;
    if (colIndex) {
      child_cell = row.cells[colIndex];
    }

    if (child_cell) {
      if (child_cell.tiqitEditing) {
        old_value = child_cell.tiqitEditor.value;
        regenerateEditor(child_cell, row.id, field.childfields[child])
        // If the new selected value in the dropdown is different from the 
        // old one then update this fields children recursively (i.e.
        // the grandchildren of the current field
        if (child_cell.tiqitEditor.value != old_value) {
          ev.currentTarget = child_cell.tiqitEditor;
          updateChildrenMultiedit(ev);
        }
      } else {
        // If there is a cell but no editor then make it editable for
        // the user as they will probably need to change it
        startEditingCell(getAncestorOfType(child_cell, 'TR'), child_cell, field.childfields[child]);
      }
    }
  }
}


function getFieldValueMultiedit(field, bugID) {

  var row = document.getElementById(bugID);

  value = getFieldValueCommon(row, field);

  return (value);
}


function startEditingCell(row, cell, colName) {
  var editor;

  if (row.tiqitSaving) {
    // Can't edit this row. It's being saved.
    return;
  }

  var parent = cell;
  var spans = getElementsByClassName('tiqitTextValue', cell);
  if (spans.length > 0) {
    parent =  spans[0];
  }

  // Save the current value
  cell.tiqitVal = parent.textContent;

  while (parent.firstChild) {
    parent.removeChild(parent.firstChild);
  }

  editor = generateEditor(row.id, cell.tiqitVal, colName)
  editor.input.defaultValue = cell.tiqitVal;
  parent.appendChild(editor);

  cell.tiqitEditing = true;
  cell.tiqitEditor = editor;

  // Maybe this cell should be banned immediately
  editor.input.disabled = isCellBanned(cell);

  startEditingRow(row);
}


function sanitiseRow(row) {
  // Sanitise the row. Regenerate any editors based on any newly saved 
  // parent values and disable editors where
  // necessary
  var table = getAncestorOfType(row, 'TABLE');

  for (var i = 0; i < row.cells.length; i++) {
    if (row.cells[i].tiqitEditing) {
      var field = table.tHead.rows[0].cells[i].getAttribute('field');
      regenerateEditor(row.cells[i], row.id, field)
      row.cells[i].tiqitEditor.input.disabled = isCellBanned(row.cells[i]);
    }
  }
}

function stopEditingRow(row) {
  row.tiqitEditing--;

  if (row.tiqitEditing <= 0) {
    row.tiqitRowSaver.parentNode.removeChild(row.tiqitRowSaver);
    row.tiqitRowSaver = null;
    row.tiqitEditing = 0;
    row.tiqitChanged = 0;
  }
}

function startEditingRow(row) {
  if (!row.tiqitEditing) {
    if (contains(updatedBugs, row.id)) {
      clearMarksForBug(row);
    }

    var img = document.createElement('img');
    img.tiqitEditingRowSaver;
    img.src = 'images/save-16x16.png';
    img.alt = '[Save]';
    img.title = 'Save changes to this bug';
    img.addEventListener('click', saveRow, false);
    img.style.visibility = 'hidden';

    row.tiqitActionsMenu.appendChild(img);

    row.tiqitRowSaver = img;

    row.tiqitEditing = 1;
    row.tiqitChanged = 0;
  } else {
    row.tiqitEditing++;
  }
}

//
// Edit handlers
//

function toggleAllFields(event) {
  var list = getAncestorOfType(event.target, 'UL');
  var inputs = list.getElementsByTagName('INPUT');

  var checked = event.currentTarget.checked;

  for (var i = 0; i < inputs.length; i++) {
    if (inputs[i].tiqitHandler == toggleFieldHandler) {
      var oldChecked = inputs[i].checked;
      inputs[i].checked = checked;
      if (oldChecked != checked) {
        fireEvent('change', inputs[i]);
      }
    }
  }
}

function toggleFieldLock(event) {
  var table = getAncestorOfType(event.currentTarget, 'TABLE');
  table.tiqitEditingLocked = event.currentTarget.checked;
  //sendMessage(1, 'Edit lock status is now: ' + event.currentTarget.checked);
}

function toggleFieldHandler(event) {

  //sendMessage(1, event.target.parentNode.textContent + ' is now ' + event.currentTarget.checked);

  if (event.currentTarget.checked) {
    startEditingField(getAncestorOfType(event.currentTarget, 'TABLE'), event.currentTarget.parentNode.textContent);
  } else {
    stopEditingField(getAncestorOfType(event.currentTarget, 'TABLE'), event.currentTarget.parentNode.textContent);
  }
}

function stopEditingField(table, colName) {
  var colIndex = -1;

  for (var i = 0; i < table.tHead.rows[0].cells.length; i++) {
    if (table.tHead.rows[0].cells[i].getAttribute('field') == colName) {
      colIndex = i;
      break;
    }
  }

  if (colIndex == -1) {
    // wtf?
    sendMessage(2, "No field named '" + colName + "' in the table. Can't stop editing.");
    return;
  }

  for (var i = 0; i < table.tBodies.length; i++) {
    for (var j = 0; j < table.tBodies[i].rows.length; j++) {
      var row = table.tBodies[i].rows[j];
      if (!row.tiqitSaving && row.style.display != 'none') {
        stopEditingCell(row, row.cells[colIndex], colName);
      }
    }
  }

  table.tHead.rows[0].cells[colIndex].tiqitEditing = false;
}

function startEditingField(table, colName) {
  /*
   * So, what do we need to do? Well, we need to get the table, and find out
   * which column it is we are editing. We then need to iterate over each
   * row, ensure it is actually displayed, and Do Stuff.
   *
   * What stuff? I hear you ask. Well, firstly we should clear any marks on it.
   * Next, we should save the current value (in the cell). Then we should
   * generate a suitable editing object, and replace the current contents with
   * that. Finally, we should add a save icon to the end of the relevant row,
   * mark the row as being edited (so that updateresults can find out and not
   * overwrite), and show the global save icon (if it is currently hidden).
   *
   * Easy peasy, right?
   */

  var colIndex = -1;

  for (var i = 0; i < table.tHead.rows[0].cells.length; i++) {
    if (table.tHead.rows[0].cells[i].getAttribute('field') == colName) {
      colIndex = i;
      break;
    }
  }

  if (colIndex == -1) {
    // wtf?
    sendMessage(2, "No field named '" + colName + "' in the table. Can't start editing.");
    return;
  }

  for (var i = 0; i < table.tBodies.length; i++) {
    for (var j = 0; j < table.tBodies[i].rows.length; j++) {
      var row = table.tBodies[i].rows[j];
      if (row.style.display != 'none') {
        if (!row.tiqitSaving && !row.cells[colIndex].tiqitEditing) {
          startEditingCell(row, row.cells[colIndex], colName);
        }
      }
    }
  }

  table.tHead.rows[0].cells[colIndex].tiqitEditing = true;
}

//
// Some fields might want to be editable from the very start
//

function tiqitMultiEditInit() {
  var args = parseQueryString(tiqitSearchQuery);
  var tables = getTables('results');
  for (var key in args) {
    if (key.substring(0, 4) == 'edit' && args[key]) {
      // Get the value out
      var num = parseInt(key.substring(4));
      var field = args['selection' + num];

      for (var i = 0; i < tables.length; i++) {
        startEditingField(tables[i], field);
      }
    }
  }
}

addCustomEventListener("FirstWindowLoad", function() {
  setTimeout(tiqitMultiEditInit, 1);
});
