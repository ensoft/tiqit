// Create a control for selecting fields. It will contain a series of <select>
// elements with id "selectionN", suitable for embedding in a form.
function createFieldsSelector(prefix) {
  var colnames = new Array("Field", "Editable", "Actions")
  var selectO = document.getElementById(prefix + 'Selector');
  
  var fieldTable = document.createElement('table');
  selectO.fieldTable = fieldTable;

  fieldTable.setAttribute('class', 'tiqitTable tiqitFieldSelectorTable');
  fieldTable.createTHead();
  fieldTable.appendChild(document.createElement('tbody'));
  fieldTable.tHead.insertRow(-1);

  var add = document.createElement('img');
  add.src = 'images/plus-small.png';
  add.title = 'Insert field above';
  add.alt = '[Add]';
  add.className = 'addIcon'
  
  var td = document.createElement('td');
  td.setAttribute('colspan', 3);

  td.appendChild(add);

  fieldTable.createTFoot();
  fieldTable.tFoot.insertRow(-1);
  fieldTable.tFoot.rows[0].appendChild(td);
  for (i in colnames) {
    var colname = colnames[i];
    var th = document.createElement('th');
    th.appendChild(document.createTextNode(colname));
    fieldTable.tHead.rows[0].appendChild(th);
  }

  return fieldTable;
}

// Create a <select> element containing all the selectable fields
function createFieldSelector(name, num) {
  var newS, opt;

  newS = document.createElement('select');
  newS.setAttribute('id', name + num);
  newS.setAttribute('name', name + num);
  newS.addEventListener('change', Tiqit.search.checkGroupBy, false);
  for (f in allViewableFields) {
    opt = document.createElement('option');
    opt.setAttribute('value', allViewableFields[f]);
    opt.appendChild(document.createTextNode(allFields[allViewableFields[f]].longname));

    newS.appendChild(opt);
  }

  return newS;
}

// Create an "Editing?" check box.
function createFieldSelectionEditable(editname, num) {
  var cb = document.createElement('input');

  cb.name = editname + num;
  cb.id = editname + num;
  cb.type = 'checkbox';

  return cb;
}

// Return the row for a given field selection.
function getFieldSelectionTableRow(name, num) {
  return document.getElementById('field' + name + 'Row' + num);
}

function renumberFieldSelectionRow(name, editname, row, newNum) {
  row.num = newNum;
  row.selector.setAttribute('id', name + newNum);
  row.selector.setAttribute('name', name + newNum);
  row.checkbox.setAttribute('id', editname + newNum);
  row.checkbox.setAttribute('name', editname + newNum);
  row.setAttribute('id', 'field' + name + 'Row' + newNum);
}

function moveFieldSelectionRow(name, editname, oldNum, newNum) {
  if (oldNum == newNum) {
    return;
  }

  // Temporarily Remove the row being moved
  var numRows = numFieldSelections(name);
  var row = getFieldSelectionTableRow(name, oldNum);
  var parent = row.parentNode;
  parent.removeChild(row);

  // Renumber rows between min(newNum,oldNum) and max(newNum,oldNum)
  if (oldNum < newNum) {
    for (var i = oldNum + 1; i <= newNum; i++) {
      renumberFieldSelectionRow(name, editname,
                                getFieldSelectionTableRow(name, i), i - 1);
    }
  } else {
    for (var i = oldNum - 1; i >= newNum; i--) {
      renumberFieldSelectionRow(name, editname,
                                getFieldSelectionTableRow(name, i), i + 1);
    }
  }
  renumberFieldSelectionRow(name, editname, row, newNum);

  // Put the row back in.
  if (newNum == numRows) {
    parent.appendChild(row);
  } else {
    var nextRow = getFieldSelectionTableRow(name, newNum + 1);
    parent.insertBefore(row, nextRow);
  }
}

function setNumSelections(prefix) {
  var selectO = document.getElementById(prefix + 'Selector');
  var countelement = document.getElementById(prefix + 'Count');
  countelement.value = selectO.fieldTable.tBodies[0].rows.length;
}

function numFieldSelections(prefix) {
  var selectO = document.getElementById(prefix + 'Selector');

  return selectO.fieldTable.tBodies[0].rows.length;
}

// Return an element containing all the action icons for a field.
function createFieldSelectionActions(name, editname, num, row) {
  var actions =  document.createElement('div');
  actions.setAttribute('class', 'tiqitActions');

  var move = document.createElement('img');
  move.src = 'images/hamburger-blue.png';
  move.title = 'Move field';
  move.alt = '[Move]';
  move.className = 'hamburger-move';

  var remove = document.createElement('img');
  remove.src = 'images/delete-cross-small.png';
  remove.title = 'Remove field';
  remove.alt = '[Remove]';
  remove.addEventListener('click', function() {
    if (numFieldSelections(name) == 1) {
      alert("Don't try to remove all the fields, punk");
    } else {
      moveFieldSelectionRow(name, editname, row.num, numFieldSelections(name));
      row.parentNode.removeChild(row);
      setNumSelections(name);
    }
  }, false);

  actions.appendChild(remove);
  actions.appendChild(move);

  return actions;
}

// Insert a new field selection with the given number. Pass -1 to insert at
// the end.
function addFieldSelection(name, editname, num) {
  var selectO = document.getElementById(name + 'Selector');
  var row = selectO.fieldTable.tBodies[0].insertRow(-1);

  // Use the Sortable library to allow drag'n'drop
  var tbody = selectO.fieldTable.tBodies[0];
  if (tbody && !tbody.sortable) {
      Sortable.create(tbody, {
        handle: '.hamburger-move',
        onMove: function(event) {
          moveFieldSelectionRow(name, editname, event.dragged.num, event.related.num);
        }
      });

      var add = selectO.getElementsByClassName('addIcon')[0];
      if (add) {
          add.addEventListener('click', function() {
            addFieldSelection(name, editname, -1);
            setNumSelections(name);
          }, false);
      }
      tbody.sortable = true;
  }

  row.selector = createFieldSelector(name, numFieldSelections(name));
  row.checkbox = createFieldSelectionEditable(editname, numFieldSelections(name));
  row.setCheckboxEnabled = function() {
    row.checkbox.disabled = !allFields[row.selector.value].editable;
  }
  row.selector.addEventListener('change', row.setCheckboxEnabled, false);
  row.setCheckboxEnabled();

  row.insertCell(-1).appendChild(row.selector);
  row.insertCell(-1).appendChild(row.checkbox);
  row.insertCell(-1).appendChild(createFieldSelectionActions(name, editname, numFieldSelections(name), row));
  row.num = numFieldSelections(name);
  row.setAttribute("id", "field" + name + "Row" + numFieldSelections(name));

  if (num !== undefined && num != -1) {
    moveFieldSelectionRow(name, editname, numFieldSelections(name), num);
  }
}

// Set the value of a particular field selector
function setFieldSelection(name, num, field) {
  document.getElementById(name + num).value = field;
  getFieldSelectionTableRow(name, num).setCheckboxEnabled();
}

// Set whether a particular field is editable
function setFieldEditing(editname, num, editing) {
  document.getElementById(editname + num).checked = editing;
}

