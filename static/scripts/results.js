
//
// Table sorting
//

// Remove sort-state from a table (but do not do any re-ordering).
function sortReset(table) {
    function resetCells(cells) {
        for (var i = 0; i < cells.length; i++) {
            cells[i].sortIndex = null;
            cells[i].className = '';
        }
    }

    resetCells(table.getElementsByClassName("sortAsc"));
    resetCells(table.getElementsByClassName("sortDesc"));
}

function sortResults(event) {
  // Find out what column index we're at, and save it in the table.
  var table = getAncestorOfType(event.target, 'TABLE');
  var header = getAncestorOfType(event.target, 'TH');
  var colIndex = header.cellIndex;
  var field = allFields[header.getAttribute('field')];

  if (table.tHead.rows[0].cells[table.sortIndex]) {
    table.tHead.rows[0].cells[table.sortIndex].className = '';
  }

  if (table.sortIndex == colIndex) {
    table.sortOrder = !table.sortOrder;
  } else {
    table.sortOrder = true;
  }

  table.sortIndex = colIndex;

  if (table.sortOrder) {
    table.tHead.rows[0].cells[table.sortIndex].className = 'sortAsc';
  } else {
    table.tHead.rows[0].cells[table.sortIndex].className = 'sortDesc';
  }

  // Now make a copy of the rows, and sort them.
  var newRows = new Array();
  for (var i = 0; i < table.tBodies[0].rows.length; i++) {
    newRows.push(table.tBodies[0].rows[i]);
  }

  if (field.ftype == 'Number') {
    newRows.sort(sortFunctionInt);
  } else if (contains(['Date', 'DateOnly'], field.ftype)) {
    newRows.sort(sortFunctionDate);
  } else {
    newRows.sort(sortFunction);
  }

  for (i = 0; i < newRows.length; i++) {
    table.tBodies[0].appendChild(newRows[i]);
  }
}

function sortFunction(a, b) {
  var table = a.parentNode.parentNode;

  var cellA = a.cells[table.sortIndex];
  var cellB = b.cells[table.sortIndex];

  cellA = cellA.tiqitEditing ? cellA.tiqitVal : cellA.textContent;
  cellB = cellB.tiqitEditing ? cellB.tiqitVal : cellB.textContent;

  if (cellA == cellB) {
    return 0;
  }

  if (table.sortOrder) {
    if (cellA < cellB) {
      return -1;
    } else {
      return 1;
    }
  } else {
    if (cellA < cellB) {
      return 1;
    } else {
      return -1;
    }
  }
}

function sortFunctionInt(a, b) {
  var table = a.parentNode.parentNode;

  var cellA = a.cells[table.sortIndex];
  var cellB = b.cells[table.sortIndex];

  cellA = parseInt(cellA.tiqitEditing ? cellA.tiqitVal : cellA.textContent);
  cellB = parseInt(cellB.tiqitEditing ? cellB.tiqitVal : cellB.textContent);

  if (cellA == cellB) {
    return 0;
  }

  if (table.sortOrder) {
    if (cellA < cellB) {
      return -1;
    } else {
      return 1;
    }
  } else {
    if (cellA < cellB) {
      return 1;
    } else {
      return -1;
    }
  }
}

var dateRE = /^(\d{2})\/(\d{2})\/(\d{4})/;
function sortFunctionDate(a, b) {
  var table = a.parentNode.parentNode;

  var cellA = a.cells[table.sortIndex];
  var cellB = b.cells[table.sortIndex];

  cellA = cellA.tiqitEditing ? cellA.tiqitVal : cellA.textContent;
  cellB = cellB.tiqitEditing ? cellB.tiqitVal : cellB.textContent;

  // Rearrange the date fields from MM/DD/YYYY
  // to YYYYMMDD that way dictionary sort == date sort
  cellA = cellA.replace(dateRE,"$3$1$2");
  cellB = cellB.replace(dateRE,"$3$1$2");

  if (table.sortOrder) {
    if (cellA < cellB) {
      return -1;
    } else {
      return 1;
    }
  } else {
    if (cellA < cellB) {
      return 1;
    } else {
      return -1;
    }
  }
  return 0;
}

//
// Refine Query
//

function refineQuery() {
  var tables = getTables('results');
  var row;

  if (tables.length == 0) {
    // No results to refine!
    alert("There are no results to search within!");
    return;
  }

  var bugs = new Array();

  for (var i = 0; i < tables.length; i++) {
    for (var j = 0; j < tables[i].tBodies.length; j++) {
      for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
        row = tables[i].tBodies[j].rows[k];
        if (row.style.display == 'table-row') {
          bugs.push(row.id);
        }
      }
    }
  }

  document.location.href = 'search?buglist=' + bugs.join(',');
}
