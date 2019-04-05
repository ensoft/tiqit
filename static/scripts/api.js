//
// API
//


// TiqitApi
//
// The TiqitApi object is used for accessing Tiqit's programmer interface.
//
// baseUrl: (Optional.) The base URL of the Tiqit website to fetch data from.
//          If this argument is not specified, and the current document is not
//          a Tiqit website, this value will be taken from the document
//
//          If this argument is not specified, and the current document is a
//          Tiqit website, the base URL of the current document will be used.
function TiqitApi(baseUrl) {
    if (!baseUrl) {
        baseUrl = document.baseURI;
    }

    // Define an assert() function seeing as Javascript doesn't have one by
    // default.
    function AssertException(message) { 
        this.message = message;
    }
    AssertException.prototype.toString = function () {
          return 'AssertException: ' + this.message;
    }
    function assert(exp, message) {
        if (!exp) {
            throw new AssertException(message);
        }
    }

    // Recursive function for converting a searchTree to a query string. This
    // function just returns the parts of the query string related to the
    // search query.
    function searchTreeToURLRec(tree, level, startRow, parentOp) {
        var out = new Object();
        out.query = "";

        if (tree.op) {
            if (tree.op == "OR" && parentOp == "AND") {
                level++;
            }
            var leftOut = searchTreeToURLRec(tree.left, level, startRow, tree.op);
            out.query += leftOut.query;
            out.query += "opLevel" + leftOut.endRow + "=" + level + "&";
            out.query += "operation" + leftOut.endRow + "=" + encodeURIComponent(tree.op) + "&";
            var rightOut = searchTreeToURLRec(tree.right, level, leftOut.endRow + 1, tree.op);
            out.query += rightOut.query;
            out.endRow = rightOut.endRow;
        } else {
            out.query += "level" + startRow + "=" + level + "&";
            out.query += "field" + startRow + "=" + encodeURIComponent(tree.field) + "&";
            out.query += "rel" + startRow + "=" + encodeURIComponent(tree.rel) + "&";
            out.query += "val" + startRow + "=" + encodeURIComponent(tree.val) + "&";
            out.endRow = startRow;
        }

        return (out);
    }

    // Wrapper around XMLHttpRequest().
    function fetchURL(url, onload, onerror, timeout = -1, ontimeout = null) {
        var req = new XMLHttpRequest();
        req.open("GET", url, true);
        req.onload = onload;
        req.onerror = onerror;
        if (timeout > 0 && ontimeout != null) {
          req.timeout = timeout;
          req.ontimeout = ontimeout;
        }
        req.send(null);
    }

    // searchTreeToURL()
    //
    // Generate the a results URL given an expression tree, and other search
    // arguments.
    //
    // tree: An object representing the search expression. If the root of the
    //       expression is an operation, then tree.op and tree.left, and
    //       tree.right are set. tree.op is either "AND" or "OR", and tree.left
    //       and tree.right are other expression trees.
    //
    //       If the expression is just a simple relationship, then tree.field,
    //       tree.rel and tree.val describe the relationship.
    //
    // project: The project to search within.
    //
    // columns: Fields to show for matching bugs.
    //
    // sorts: An array listing fields to sort on. The first element is the
    //        primary sort, the second element the secondary sort, and so on.
    //
    // sortOrders: An array describing whether the corresponding element in
    //             sorts should be sorted ascending or descending. This array
    //             must be the same length as sorts, and each element must be
    //             either "ASC" or "DSC".
    //
    // buglist: (Optional.) An array of bugs to filter on.
    //
    // format: Format of the output data. Supported values are "xml", "html"
    //         and "csv".
    this.searchTreeToURL = function(tree, project, columns, sorts, sortOrders, buglist, format) {
        var treeOut = searchTreeToURLRec(tree, 0, 1, "");
        var query = treeOut.query;
        query += "opLevel" + treeOut.endRow + "=0&";
        query += "operation" + treeOut.endRow + "=AND&";
        query += "Project=" + encodeURIComponent(project) + "&";

        for (var i = 0; i < columns.length; i++) {
            query += "selection" + (i+1) + "=" + columns[i] + "&"; 
        }

        assert(sorts.length == sortOrders.length);
        for (var i = 0; i < sorts.length; i++) {
            query += "sort" + (i+1) + "=" + sorts[i] + "&";
            assert(sortOrders[i] == "ASC" || sortOrders[i] == "DSC");
            query += "sortOrder" + (i+1) + "=" + sortOrders[i] + "&";
        }

        if (buglist) {
            query += "buglist=";
            for (var i = 0; i < buglist.length; i++) {
                query += encodeURIComponent(buglist[i]);
                if (i < buglist.length - 1) {
                    query += encodeURIComponent(",");
                }    
            }
            query += "&";
        }

        query += "format=" + format;

        return baseUrl + "/results?" + query;
    }

    // resultsFromTree()
    //
    // Perform a search given an expression tree.
    //
    // onload: An onload function called when the search is complete. This
    // function must be compatible with the onload function used with
    // XMLHttpRequest().
    //
    // onerror: An onerror function called when the search fails. This
    // function must be compatible with the onload function used with
    // XMLHttpRequest().
    //
    // See TiqitApi.searchTreeToURL() for a description of this method's
    // other arguments.
    this.resultsFromTree = function(tree, project, columns, sorts, sortOrders, buglist, format, onload, onerror) {
        return fetchURL(this.searchTreeToURL(tree, project, columns, sorts, sortOrders, buglist, format), onload, onerror);
    }

    // historyForBugs()
    //
    // Fetch history information for an array of bugs.
    //
    // bugs: An array of bug ids.
    //
    // onload: An onload function called when the search is complete. This
    // function must be compatible with the onload function used with
    // XMLHttpRequest().
    //
    // onerror: An onerror function called when the search fails. This
    // function must be compatible with the onload function used with
    // XMLHttpRequest().
    //
    // timeout: ms before the function times out.
    //
    // ontimeout: function to call when history fetch times out.
    this.historyForBugs = function(bugs, onload, onerror, timeout = -1, ontimeout = null) {
        var url = baseUrl + "/history.py?buglist=";
        for (var i = 0; i < bugs.length; i++) {
            url += encodeURIComponent(bugs[i]);
            if (i < bugs.length - 1) {
                url += encodeURIComponent(",");
            }
        }
        return fetchURL(url, onload, onerror, timeout, ontimeout);
    }
}


