//
// Define the Field type
//

var allFields = new Array();
var allEditableFields = new Array();
var allSearchableFields = new Array();
var allViewableFields = new Array();

var dateFields = new Array();
var userFields = new Array();

function uniqueListofLists(a) {
    var seen = Object();

    for (var i = a.length - 1; i >= 0; i--) {
        if (seen[a[i]]) {
            a.splice(i, 1);
        } else {
            seen[a[i]] = true;
        }
    }

    return (a);
}

function crossLists(lista, listb) {
    var new_list;

    if (lista.length == 0) {
        new_list = listb;
    } else if (listb.length == 0) {
        new_list = lista;
    } else {
        new_list = [];
        for (a in lista) {
            for (b in listb) {
                new_list.push([lista[a], listb[b]]);
            }
        }
    }
    return (new_list);
}

TiqitField = function(name, shortname, longname, ftype, maxlen, displaylen, req, mvf, searchable, editable, viewable, filterable, volatile) {
  this.name = name;
  this.shortname = shortname;
  this.longname = longname;
  this.ftype = ftype;
  this.maxlen = maxlen;
  this.displaylen = displaylen;
  this.req = req;
  this.mvf = mvf;
  this.searchable = searchable;
  this.editable = editable;
  this.viewable = viewable;
  this.filterable = filterable;
  this.volatile = volatile;

  this.perparentvalues = new Object();
  this.parentfields = [];
  this.childfields = [];
  this.mandatoryif = new Object();
  this.bannedif = new Object();
  this.defaultsWith = [];
  this.defaultsFor = [];

  // Add to the various global arrays
  allFields[this.name] = this;
  if (this.viewable) {
    allViewableFields.push(this.name);
  }
  if (this.editable) {
    allEditableFields.push(this.name);
  }
  if (this.searchable) {
    allSearchableFields.push(this.name);

    // Set up relationships and values
    if (this.ftype == 'AcmeComponent') {
      this.rels = relAcmeComponent;
      this.values = null;
    } else if (this.ftype == 'Userid' && !this.mvf && !this.hasValues) {
      this.rels = relUser;
      this.values = null;
    } else if (this.ftype == 'Userid' && this.mvf) {
      this.rels = relUserMvf;
      this.values = null;
    } else if (contains(['Text', 'Component', 'ForeignID', 'Character', 'Varchar'], this.ftype) && !this.mvf) {
      this.rels = relText;
      this.values = null;
    } else if (contains(['Text', 'Component', 'ForeignID', 'Character', 'Varchar'], this.ftype) && this.mvf) {
      this.rels = relTextMvf;
      this.values = null;
    } else if (this.ftype == 'Boolean') {
      this.rels = new Array(relIs);
      this.values = [['True', 'Y'], ['False', 'N']];
    } else if (this.ftype == 'Date') {
      this.rels = relDate;
      this.values = null;
    } else if (this.ftype == 'DefectID') {
      this.rels = relText;
      this.values = null;
    } else if (this.ftype == 'Number') {
      this.rels = relNumber;
      this.values = null;
    } else {
      alert("Field '" + this.name + "' is of unknown type (" + this.ftype + ")");
    }
  } else {
    this.rels = new Array();
    this.values = null;
  }

  // We need to remember certain types of field
  if (this.ftype == 'Date') {
    dateFields.push(this);
  } else if (this.ftype == 'Userid') {
    userFields.push(this);
  }
};

TiqitField.prototype.getSearchValues = function(getParentValueFunction) {
  if (this.searchvals) {
    return this.searchvals;
  } else {
    return this.getValues(getParentValueFunction);
  }
};


TiqitField.prototype.hasParentDependency = function() {
    return Tiqit.objectHasKeys(this.perparentvalues);
};


TiqitField.prototype.getAllValues = function() {
    if (this.hasParentDependency()) {
        vals = [];
        for (key in this.perparentvalues) {
            for (value in this.perparentvalues[key]) {
                vals.push(this.perparentvalues[key][value]);
            }
        }
    } else {
        vals = this.values;
    }
    return vals;
};


/*
 * Returns a list of values supported by the given field.
 */
TiqitField.prototype.getValues = function(getParentValueFunction) {
    if (this.hasParentDependency()) {
        // Need to find all of the valid parent keys based on the parent values
        var parent_keys = [];
        for (var parent in this.parentfields) {
            var parent_vals = [];
            var parent_list = [];
            var parent_val = getParentValueFunction(this.parentfields[parent]);
            if (parent_val) {
                parent_vals.push(parent_val);
            } else {
                parent_list = allFields[this.parentfields[parent]].getAllValues();
                for (var pair in parent_list) {
                    parent_vals.push(parent_list[pair][0]);
                }
            }
            // We have a list of allowed parent values for this parent.
            // Combine it with previous found parent values to get the full
            // list of keys
            parent_keys = crossLists(parent_keys, parent_vals);
        }
            
        // Now use the parent keys to build up a list of allowed values
        var vals = [];
        for (var parent_key in parent_keys) {
            if (parent_keys[parent_key] in this.perparentvalues) {
                for (var val in this.perparentvalues[parent_keys[parent_key]]) {
                    vals.push(this.perparentvalues[parent_keys[parent_key]][val]);
                }
            }
        }
        values = uniqueListofLists(vals);

        // Concatenating value lists does not give a useful ordering, so if
        // concatenation actually occurred sort alphabetically.
        if (parent_keys.length > 1) {
            values.sort();
        }
        return values;
    } else if (this.values) {
        // return the valid values if we have some..
        return this.values;
    } else {
        // ..otherwise return an empty list
        return [];
    }
};

// Check a drop-down input's options to see if they are up to date
TiqitField.prototype.checkInputOptions = function(getParentValueFunction, input) {
  var vals;
  var old_vals = [];
  var valsAreSame = true;

  if (!this.hasParentDependency) {
    return true;
  }

  vals = this.getValues(getParentValueFunction);
  for (var i = 0; input.options && i < input.options.length; i++) {
    old_vals.push(input.options[i].textContent);
  }

  if (vals.length == old_vals.length) {
    for (var val in vals) {
      if (vals[val][1] != old_vals[val]) {
        valsAreSame = false;
        break;
      }
    }
  } else {
    valsAreSame = false;
  }

  return valsAreSame;
}

//
// Relationships
//
relIs = new Array('is', '=');
relIsNot = new Array('is not', '<>');
relStartsWith = new Array('starts with', 'startswith');
relEndsWith = new Array('ends with', 'endswith');
relContains = new Array('contains', 'contains');
relContainsNot = new Array('does not contain', 'doesnotcontain');
relAfter = new Array('is after', '>=');
relBefore = new Array('is before', '<=');
relWithinLast = new Array('is within last', 'withinlast');
relOneIs = new Array('one of is', '=');
relNoneIs = new Array('none of is', '!=');
relOneStartsWith = new Array('one of starts with', 'startswith');
relOneEndsWith = new Array('one of ends with', 'endswith');
relOneContains = new Array('one of contains', 'contains');
relNoneStartsWith = new Array('none of starts with', 'notstartswith');
relNoneEndsWith = new Array('none of ends with', 'notendswith');
relGreaterThan = new Array('is greater than', '>');
relLessThan = new Array('is less than', '<');
relSpecialIs = new Array('is', 'isoneof');
relSpecialIsNot = new Array('is not', 'isnotoneof');

relUser = new Array(relIs, relIsNot);
relAcmeComponent = new Array(relIs, relIsNot);
relText = new Array(relIs, relIsNot, relStartsWith, relEndsWith, relContains, relContainsNot);
relSelect = new Array(relIs, relIsNot);
relDate = new Array(relIs, relIsNot, relAfter, relBefore, relWithinLast);
relTextMvf = new Array(relOneIs, relNoneIs, relOneStartsWith, relOneEndsWith, relOneContains, relNoneStartsWith, relNoneEndsWith);
relUserMvf = new Array(relOneIs, relNoneIs);
relNumber = new Array(relIs, relIsNot, relLessThan, relGreaterThan);
relSpecial = new Array(relSpecialIs, relSpecialIsNot);

