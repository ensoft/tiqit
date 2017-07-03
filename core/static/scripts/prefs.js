function resetOrderNumbers(table) {
  for (var i = 1; i < table.rows.length; i++) {
    var row = table.rows[i];
    document.getElementById('viewOrder' + row.cells[0].textContent).value = row.rowIndex;
  }
}

function makeSortable() {
  var table = document.getElementById('viewTable');
  var tBody = table.tBodies[0];
  Sortable.create(tBody, {
    handle: '.hamburger-move',
    onUpdate: function(event) {
      resetOrderNumbers(table);
    }
  });
}
