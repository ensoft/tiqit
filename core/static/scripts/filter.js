//
// Provides functionality to filter and group results in tables.
//

/*
 * What's in this file?
 *
 * Event Handlers:
 * - tiqitFilterHandleNewRow
 * - tiqitFilterHandleNewCol
 * - tiqitFilterHandleModCell
 * - tiqitFilterHandleDelRow
 *
 * Helper Functions:
 * - tiqitFilterFieldIncr
 * - tiqitFilterFieldDecr
 * - tiqitFilterUpdateOptions - update counts; show/hide options/selects
 * - tiqitRegroupAndFilter
 *
 * Filter Functions:
 * - tiqitFilterInit - onload setup of data structures
 * - tiqitFilterAddRow - add a new visible filter row
 * - tiqitFilterPrepare - prepare object for a filter run
 * - tiqitFilterDefault - per row filter function
 * - tiqitFilterTable - filter a whole table
 * - tiqitFilterClear - reset existing filter
 *
 * Grouping Functions:
 * - filterGroupBy
 */

// Event handlers
// Updates filters when changes are detected
//

function tiqitFilterFieldIncr(filters, field, value) {
  // Some fields we just don't care about
  if (!filters.fields[field]) {
    return;
  }

  if (filters.fields[field][value] === undefined) {
    filters.fields[field][value] = 0;
    // Also create a new <option> for this value
    var opt = document.createElement('option');
    opt.value = value;
    opt.appendChild(document.createTextNode(value));
    for (var i = 0; i < filters.filters.length; i++) {
      var clone = opt.cloneNode(true);
      filters.filters[i][field].appendChild(clone);
      selectSort(filters.filters[i][field]);
    }
  }

  // Increment the count
  filters.fields[field][value]++;
}

function tiqitFilterFieldDecr(filters, field, value) {
  // Only do anything if the number is actually positive
  if (filters.fields[field] && filters.fields[field][value]) {
    filters.fields[field][value]--;

    // Now if there are 0 more, we should hide the option
    // If furthermore there are 1 or less options now visible, hide the select
    // TBD: but not yet
  }
}

function tiqitFilterHandleTableChanged(event) {
  // Called at the end of any bulk changes to a table. Regroup tables.
  tiqitRegroupAndFilter(event.target.name);
}

function tiqitFilterHandleNewRow(event) {
  var row = event.target;
  var table = getAncestorOfType(row, 'TABLE');
  var tableName = table.id.replace(/\d*$/, '');
  var filters = document.getElementById(tableName + 'Filters');

  if (filters) {
    var head = table.tHead.rows[0];
    for (var i = 0; i < row.cells.length; i++) {
      if (row.cells[i].cellIndex >= head.cells.length) {
        continue;
      }
      var field = head.cells[row.cells[i].cellIndex].getAttribute('field');
      tiqitFilterFieldIncr(filters, field, row.cells[i].textContent);
    }

    tiqitFilterUpdateOptions(filters);
  }
}

function tiqitFilterHandleNewCol(event) {
  var field = allFields[event.target.field];
  var tableName = event.target.tableName;
  var filters = document.getElementById(tableName + 'Filters');

  // Only create a filter if the field is filterable (and there are filters)
  if (filters && field.filterable) {
    // At this stage, there are no values (we get told them by CellChanged
    // events) so just create the relevant objects
    filters.fields[field.shortname] = new Object();
    for (var i = 0; i < filters.filters.length; i++) {
      var sel = document.createElement('select');
      sel.name = field.shortname;
      sel.id = "" + tableName + "Filter" + field.shortname;
      sel.addEventListener('change', function(event) {
        tiqitRegroupAndFilter(tableName);
      }, false);

      var opt = document.createElement('option');
      opt.value = 'NOFILTER';
      opt.appendChild(document.createTextNode(sel.name));
      sel.appendChild(opt);

      filters.filters[i][field.shortname] = sel;
      filters.filters[i].push(sel);

      filters.rows[i].appendChild(sel);
      // We need a separator between the selectors
      filters.rows[i].appendChild(document.createTextNode(' '));
    }

    tiqitFilterUpdateOptions(filters);

    // If there's a grouper, then we need to add an entry there too
    if (filters.grouper) {
        var opt = document.createElement('option');
        opt.value = field.name;
        opt.appendChild(document.createTextNode(opt.value));

        filters.grouper[field.name] = opt;
        filters.grouper.appendChild(opt);
        selectSort(filters.grouper);
    }
  }
}

function tiqitFilterHandleModCell(event) {
  var row = event.target.row;
  var table = getAncestorOfType(row, 'TABLE');
  var tableName = table.id.replace(/\d*$/, '');
  var filters = document.getElementById(tableName + 'Filters');

  if (filters) {
    var head = table.tHead.rows[0];
    var field = head.cells[event.target.cell.cellIndex].getAttribute('field');
    if (event.target.oldValue !== undefined) {
        tiqitFilterFieldDecr(filters, field, event.target.oldValue);
    }
    tiqitFilterFieldIncr(filters, field, event.target.newValue);

    tiqitFilterUpdateOptions(filters);
  }

}

function tiqitFilterHandleDelRow(event) {
  var row = event.target;
  var table = getAncestorOfType(row, 'TABLE');
  var tableName = table.id.replace(/\d*$/, '');
  var filters = document.getElementById(tableName + 'Filters');

  if (filters) {
    // For each cell, count the cells down
    var head = table.tHead.rows[0];
    for (var i = 0; i < row.cells.length; i++) {
      var field = head.cells[i].getAttribute('field');
      var val = row.cells[i].tiqitEditing ? row.cells[i].tiqitVal : row.cells[i].textContent;

      tiqitFilterFieldDecr(filters, field, val);

      tiqitFilterUpdateOptions(filters);
    }
  }
}

//
// Filtering Support
// Filters tables, updates filter buttons, creates new filter rows
//

function tiqitFilterUpdateOptions(filters) {
  var anyDisplayed = false;
  for (var i = 0; i < filters.filters.length; i++) {
    for (var j = 0; j < filters.filters[i].length; j++) {
      var sel = filters.filters[i][j];
      var choices = 0;
      for (var k = 0; k < filters.filters[i][j].options.length; k++) {
        var opt = filters.filters[i][j].options[k];
        if (opt.value == 'NOFILTER') {
          continue;
        }

        // Count the choice before we check if we can skip updating the canvas
        if (filters.fields[sel.name][opt.value] > 0) {
          choices++;
        }

        // Skip this one if it's already right - otherwise it'll be expensive
        if (opt.tiqitFilterCount == filters.fields[sel.name][opt.value]) {
          continue;
        }

        // Draw the right number onto the canvas, and use it as the background
        filters.ctx.clearRect(0, 0,
                             filters.canvas.width, filters.canvas.height);
        filters.ctx.fillText(filters.fields[sel.name][opt.value],
                             filters.canvas.width / 2,
                             filters.canvas.height / 2,
                             filters.canvas.width);
        opt.style.background = 'url("' + filters.canvas.toDataURL() + '") right no-repeat';

        if (filters.fields[sel.name][opt.value] > 0) {
          opt.style.display = 'block';
        } else {
          opt.style.display = 'none';
          if (sel.value == opt.value) {
            sel.value = "NOFILTER";
            var evt = document.createEvent('Event');
            evt.initEvent('change', true, false);
            sel.dispatchEvent(evt);
          }
        }

        opt.tiqitFilterCount = filters.fields[sel.name][opt.value];
      }
      // Hide the whole select if there's only 1 thing to choose
      if (choices < 2) {
        sel.style.display = 'none';
      } else {
        sel.style.display = 'inline';
        anyDisplayed = true;
      }
    }
  }

  // Hide the entire filter bar if there are no choices.
  if (!anyDisplayed) {
    filters.style.display = 'none';
  } else {
    filters.style.display = '';
  }
}


function tiqitRegroupAndFilter(tableName) {
    filterGroupBy(tableName);
}

//
// Called to set up the properties of a filter line.
// This parses the contents of the filter line to create the objects, so should
// only be needed on first load of a page. Subsequently, it should use events
// to trigger updates.
//
function tiqitFilterInit(tableName) {
  // Only init if it has a filter row
  var filters = document.getElementById(tableName + 'Filters');

  if (filters) {
    filters.fields = new Object();
    filters.filters = new Array(new Array());
    filters.rows = new Array();
    filters.adder = document.getElementById(tableName + 'FilterAddRow');
    filters.grouper = document.getElementById(tableName + 'GroupBy');

    // We need a canvas to draw the numbers onto
    var canvas = document.createElement('canvas');
    canvas.width = 20;
    canvas.height = 16;
    var ctx = canvas.getContext('2d');
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.font = '11px sans-serif';
    filters.canvas = canvas;
    filters.ctx = ctx;

    var span = filters.getElementsByTagName('span');
    if (span.length == 0) {
      return;
    } else {
      span = span[0];
    }

    // Assume only a single row to start with
    var cols = span.getElementsByTagName('select');
    for (var i = 0; i < cols.length; i++) {
      filters.fields[cols[i].name] = new Object();
      filters.filters[0][cols[i].name] = cols[i];
      filters.filters[0].push(cols[i]);
      cols[i].addEventListener('change', function(event) {
        tiqitRegroupAndFilter(tableName);
      }, false);
    }

    filters.negative = document.getElementById(tableName + 'FilterNeg');
    filters.rows.push(span);

    // We also scan the existing tables to count each value
    var tables = getTables(tableName);
    for (var i = 0; i < tables.length; i++) {
      var head = tables[i].tHead.rows[0];
      for (var j = 0; j < tables[i].tBodies.length; j++) {
        for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
          var row = tables[i].tBodies[j].rows[k];
          for (var l = 0; l < row.cells.length; l++) {
            var field = head.cells[l].getAttribute('field');
            var val = row.cells[l].tiqitEditing ? row.cells[l].tiqitVal : row.cells[l].textContent;
            if (filters.fields[field]) {
              if (filters.fields[field][val] === undefined) {
                filters.fields[field][val] = 0;
              }
              filters.fields[field][val]++;
            }
          } 
        }
      }
    }

    // Now update the options to display how many items exist
    tiqitFilterUpdateOptions(filters);

    // See which fields we can group by
    if (filters.grouper) {
      for (var i = 0; i < filters.grouper.options.length; i++) {
        var opt = filters.grouper.options[i];
        filters.grouper[opt.value] = opt;
      }
    }

    // Now register for all events that can change values
    addCustomEventListener('RowAdded', tiqitFilterHandleNewRow);
    addCustomEventListener('NewCol', tiqitFilterHandleNewCol);
    addCustomEventListener('CellChanged', tiqitFilterHandleModCell);
    addCustomEventListener('RowDeleting', tiqitFilterHandleDelRow);
    addCustomEventListener('TableChanged', tiqitFilterHandleTableChanged);
  }
}

//
// Add a row to the filter line.
// The second row is 'ORd' with the first one.
//
function tiqitFilterAddRow(tableName) {
  var filters = document.getElementById(tableName + 'Filters');

  // Create a new row that mimics the first
  var row = document.createElement('div');
  var span = document.createElement('span');

  filters.rows.push(row);

  var newFilter = new Array();
  filters.filters.push(newFilter);

  for (var i = 0; i < filters.filters[0].length; i++) {
    var sel = document.createElement('select');
    sel.name = filters.filters[0][i].name;
    sel.addEventListener('change', function(event) {
      tiqitRegroupAndFilter(tableName);
    }, false);
    for (var j = 0; j < filters.filters[0][i].options.length; j++) {
      var opt = document.createElement('option');
      opt.value = filters.filters[0][i].options[j].value;
      opt.textContent = filters.filters[0][i].options[j].textContent;
      opt.style.display = filters.filters[0][i].options[j].style.display;

      sel.add(opt, null);
    }
    newFilter.push(sel);
    newFilter[sel.name] = sel;

    span.appendChild(sel);
  }

  row.appendChild(document.createTextNode('Or on:'));
  row.appendChild(span);

  filters.appendChild(row);
}

//
// This uses the filter line data and the table headers to create a filter object
// that can later be passed to tiqitFilterDefault to actually perform filtering.
//
function tiqitFilterPrepare(tableName) {
  var tables = getTables(tableName);

  var obj = new Object();
  obj.filters = document.getElementById(tableName + 'Filters');
  var mapping = new Object();
  obj.colForField = function(field) {
    if (mapping[field] !== undefined) {
      return mapping[field];
    } else {
      for (var i = 0; i < tables[0].tHead.rows[0].cells.length; i++) {
        var cell = tables[0].tHead.rows[0].cells[i];
        mapping[cell.getAttribute('field')] = cell.cellIndex;
        if (mapping[field] !== undefined) {
          return mapping[field];
        }
      }
      sendMessage(0, "Can't find field '" + field + "'");
    }
  }

  return obj;
}

//
// The default filter function passed to tiqitFilterTable.
// This requires a filter object created by tiqitFilterPrepare beforehand.
//
function tiqitFilterDefault(row, obj) {
  //
  // Each row is ORd. So only keep processing lines while its passing.
  //
  var show = true;
  for (var i = 0; i < obj.filters.filters.length; i++) {
    show = true;
    for (var j = 0; show && j < obj.filters.filters[i].length; j++) {
      var fil = obj.filters.filters[i][j];
      if (fil && fil.value != 'NOFILTER') {
        var col = row.cells[obj.colForField(fil.name)];
        var val = col.tiqitEditing ? col.tiqitEditor.input.value : col.textContent;
        if (fil.value != val) {
          show = false;
        }
      }
    }

    // If we're still showing, it matched at least one line
    if (show) {
      break;
    }
  }

  if (obj.filters.negative && obj.filters.negative.checked) {
      show = !show;
  }

  return show;
}

//
// The heart of the filtering.
// Uses the filterFunc to check each line, and show or hide it accordingly.
// Updates tables headers to indicate how many results are visible.
// The optional prepFunc is used to prepare a filter context also passed
// to each call of the filterFunc.
//
function tiqitFilterTable(tableName, filterFunc, prepFunc) {
  var tables = getTables(tableName);

  // Quick exit if there's nothing to do
  if (tables.length == 0) {
    return;
  }

  var filter;
  if (prepFunc) {
    filter = prepFunc(tableName);
  }

  // We need some variables
  var total = 0, showing = 0, oftable = 0, intable = 0;
  var show;

  for (var i = 0; i < tables.length; i++) {
    tables[i].style.display = 'table';
    oftable = 0;
    intable = 0;

    for (var j = 0; j < tables[i].tBodies.length; j++) {
      for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
        show = filterFunc(tables[i].tBodies[j].rows[k], filter);

        total++;
        intable++;

        if (show) {
          tables[i].tBodies[j].rows[k].style.display = 'table-row';
          showing++;
          oftable++;
        } else {
          tables[i].tBodies[j].rows[k].style.display = 'none';
        }
      }
    }

    // If no rows of this table are sowing, hide the table (unless it's the
    // only one).
    if (oftable == 0 && tables.length > 1) {
      tables[i].style.display = 'none';
    } else if (oftable != intable) {
      if (tables[i].caption) {
        tables[i].caption.filterCount.textContent = '(' + oftable + '/' + intable + ' entries match)';
      }
    } else {
      if (tables[i].caption) {
        tables[i].caption.filterCount.textContent = '(' + intable + ' entr' + (intable == 1 ? 'y)' : 'ies)');
      }
    }
  }

  var showCount = document.getElementById(tableName + 'FilterCount');

  if (showCount) {
    if (showing == total) {
      showCount.textContent = total + ' matching entr' + (total == 1 ? 'y' : 'ies');
      if (Tiqit.prefs['miscShowSearchName'] == 'false' || !tiqitSearchName) {
        document.title = total + " results - " + Tiqit.config['general']['sitetitle'];
      }
    } else {
      showCount.textContent = showing + '/' + total + ' matching entries';
      if (Tiqit.prefs['miscShowSearchName'] == 'false' || !tiqitSearchName) {
        document.title = showing + '/' + total + " results - " + Tiqit.config['general']['sitetitle'];
      }
    }
  }

  generateCustomEvent("TableFilter", tableName);
}

//
// Reset the filters.
// Removes any row beyond the first, removes any set filters.
//
function tiqitFilterClear(tableName) {
  var filters = document.getElementById(tableName + 'Filters');

  // Remove rows beyond the first
  while (filters.rows.length > 1) {
    var row = filters.rows.pop()
    row.parentNode.removeChild(row);
    filters.filters.pop();
  }

  // Reset each filter on the first row
  for (var i = 0; i < filters.filters[0].length; i++) {
    filters.filters[0][i].value = 'NOFILTER';
  }

  // Reset the negative to not
  filters.negative.checked = false;

  // Refilter
  tiqitRegroupAndFilter(tableName);
}


/*
 * Grouping functionality
 */

function filterGroupBy(tableName, select) {
  var tables = getTables(tableName);
  var container = document.getElementById(tableName + 'TableContainer');

  if (tables.length == 0) {
    // No results to group
    return;
  }

  // If we haven't been given the select, we can look it up by name
  if (!select) {
    select = document.getElementById(tableName + 'GroupBy');
  }

  // Get the headers, and make sure one of them is the one we want to group by
  var headers = tables[0].tHead.getElementsByTagName('th');
  var groupIndex = headers.length;
  var nofilter = !select || (select.value == 'NOFILTER');

  for (var i = 0; !nofilter && i < headers.length; i++) {
    if (headers[i].getAttribute('field') == select.value) {
      groupIndex = i;
      break;
    }
  }

  if (groupIndex >= headers.length && !nofilter) {
    alert("Can't group by field '" + select.value + "' as that field isn't displayed!");
    return;
  }

  var rows = new Array();
  var prikeys = new Array();

  for (var i = 0; i < tables.length; i++) {
    for (var j = 0; j < tables[i].tBodies.length; j++) {
      for (var k = 0; k < tables[i].tBodies[j].rows.length; k++) {
        // Don't display the column we are grouping by but display the rest.
        for (var l = 0; l < headers.length; l++) {
            tables[i].tBodies[j].rows[k].cells[l].style.display = "";
            tables[i].tHead.rows[0].cells[l].style.display = "";
        }    
        if (!nofilter) {
          tables[i].tBodies[j].rows[k].cells[groupIndex].style.display = "none";
          tables[i].tHead.rows[0].cells[groupIndex].style.display = "none";

          var val;
          if (tables[i].tBodies[j].rows[k].cells[groupIndex].tiqitEditing) {
            val = tables[i].tBodies[j].rows[k].cells[groupIndex].tiqitVal;
          } else {
            val = tables[i].tBodies[j].rows[k].cells[groupIndex].textContent;
          }
          if (!contains(prikeys, val)) {
            prikeys.push(val);
          }
        }

        rows.push(tables[i].tBodies[j].rows[k]);
      }
    }
  }

  if (nofilter) {
    prikeys.push('NOFILTER');
  }

  prikeys.sort();

  // Remove old tables now, before adding new ones, to prevent duplicate
  // element ids
  for (var i = 0; i < tables.length; i++) {
    tables[i].parentNode.removeChild(tables[i]);
  }

  // Create the new tables
  var newTables = new Array();

  // Reset the first table's sort state, so the new tables have no state
  if (tables.length > 0 && tables[0].sortIndex) {
      sortReset(tables[0])
  }

  // If there are no rows, then create no tables
  for (var i = 0; rows.length > 0 && i < prikeys.length; i++) {
    var table = document.createElement('table');
    table.id = nofilter ? tableName : tableName + (i + 1);
    table.className = 'tiqitTable';
    table.style.marginBottom = '2em';
    table.style.width = '100%';
    var caption = table.createCaption();
    var span = document.createElement('span');
    span.className = 'tiqitTableCount';
    caption.appendChild(span);
    caption.filterCount = span;
    table.appendChild(caption);
    if (!nofilter) {
      caption.appendChild(document.createTextNode(select.value + ': ' + prikeys[i]));
    } else {
      // Webkit positions the caption in a strange position. Append a
      // transparent span to work around this.
      var span = document.createElement("span");
      span.appendChild(document.createTextNode("."))
      span.style.opacity = "0";
      caption.appendChild(span);
    }

    var cols = document.createElement('colgroup');
    cols.setAttribute('span', tables[0].tHead.rows[0].cells.length);
    table.appendChild(cols);
    cols = document.createElement('colgroup');
    table.appendChild(cols);
    table.appendChild(tables[0].tHead.cloneNode(true));
    table.appendChild(document.createElement('tbody'));

    newTables[prikeys[i]] = table;

    container.appendChild(table);
  }

  // Add each row to the right table
  // This should persist both current sort order, and filtering
  for (var i = 0; i < rows.length; i++) {
    if (nofilter) {
      newTables['NOFILTER'].tBodies[0].appendChild(rows[i]);
    } else {
      var val;
      if (rows[i].cells[groupIndex].tiqitEditing) {
        val = rows[i].cells[groupIndex].tiqitVal;
      } else {
        val = rows[i].cells[groupIndex].textContent;
      }
      newTables[val].tBodies[0].appendChild(rows[i]);
    }
  }

  generateCustomEvent("TableRegroup", tableName);

  tiqitFilterTable(tableName, tiqitFilterDefault, tiqitFilterPrepare);
}

