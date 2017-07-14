//
// Provides a drop down box.
//

var userDropDown;
var userDropDownShadow;
var username;
var subject;

addCustomEventListener("FirstWindowLoad", userDropDownInit);

function userDropDownInit() {
  userDropDownShadow = document.createElement('div');
  userDropDownShadow.className = 'userDropDownShadow';
  document.body.appendChild(userDropDownShadow);

  userDropDown = document.createElement('div');
  userDropDown.setAttribute('id', 'userdropdown');
  userDropDown.style.display = 'none';
  userDropDown.onmouseout = function(event) {
    try {
      if (!isAncestorOf(userDropDown, event.relatedTarget)) {
	document.getElementById('userdropdown').style.display = 'none';
        userDropDownShadow.style.display = 'none';
      }
    } catch (e) {
      document.getElementById('userdropdown').style.display = 'none';
      userDropDownShadow.style.display = 'none';
    }
  };

  userDropDown.onclick = function(event) {
    document.getElementById('userdropdown').style.display = 'none';
    userDropDownShadow.style.display = 'none';
  };

  var inner = document.createElement('div');

  var image = document.createElement('img');
  image.setAttribute('width', 60);
  image.setAttribute('height', 80);
  image.id = 'tiqitUserImage';
  inner.appendChild(image);

  var dataDiv = document.createElement('div');
  inner.appendChild(dataDiv);

  var header = document.createElement('h3');
  header.id = 'tiqitUserFullName';
  dataDiv.appendChild(header);

  var link = document.createElement('img');
  link.src = 'images/drill-up.gif';
  link.title = 'Show Manager';
  link.alt = '[Up]';
  link.addEventListener('click', function(event) {
    username = null;
    setImage('nobody');
    getUserDetails('num=' + event.currentTarget.getAttribute('managernum'));
    event.stopPropagation();
  }, false);
  header.appendChild(link);

  link = document.createElement('a');
  link.title = 'Go to Directory profile';
  link.className = 'tiqitUserDirectory';
  header.appendChild(link);

  var email = document.createElement('p');
  email.id = 'tiqitUserEmail';
  dataDiv.appendChild(email);

  link = document.createElement('a');
  link.title = 'Send email';
  email.appendChild(link);

  var phone = document.createElement('span');
  phone.id = 'tiqitUserPhone';
  email.appendChild(phone);

  link = document.createElement('a');
  phone.appendChild(link);

  var job = document.createElement('p');
  job.id = 'tiqitUserJob';
  dataDiv.appendChild(job);

  var emph = document.createElement('em');
  job.appendChild(emph);

  var dept = document.createElement('p');
  dept.id = 'tiqitUserDept';
  dataDiv.appendChild(dept);

  emph = document.createElement('em');
  dept.appendChild(emph);

  userDropDown.appendChild(inner);
  document.body.appendChild(userDropDown);
}

function showUserDropDown(event, name) {
  if (!name) {
    name = event.target;
  }
  if (typeof(name) != 'string') {
    if (name.nodeName.toLowerCase() == 'input') {
      name = name.value;
    } else if (name.parentNode.input) {
      name = name.parentNode.input.value;
    } else {
      name = name.textContent;
    }
  }
  if (!name) {
    return;
  }

  username = name;

  var id = document.getElementById('Identifier');
  var title = document.getElementById('Headline');
  subject = '';

  if (id && title) {
    subject = '?Subject=' + escape(id.value + ' - ' + title.value);
    subject += '&Body=' + escape(document.baseURI + id.value);
  }

  loadUserData(name, name, 0, "Loading...", '', '', '', '');

  var posx = event.clientX - 3;
  var posy = event.clientY - 3;

  //alert("Window is " + window.innerWidth + "x" + window.innerHeight + " and we're placing at " + posx + "x" + posy);

  if (window.innerWidth - posx < 250) {
    posx = window.innerWidth - 250;
  }

  if (window.innerHeight - posy < 100) {
    posy = window.innerHeight - 100;
  }

  // Reset the width to auto
  userDropDown.style.minWidth = 'auto';

  userDropDownShadow.style.display = 'block';
  userDropDownShadow.style.left = ((posx + 10) + 'px');
  userDropDownShadow.style.top = ((posy + 10) + 'px');
  userDropDownShadow.style.width = userDropDown.clientWidth;
  userDropDownShadow.style.height = userDropDown.clientHeight;

  userDropDown.style.display = 'block';
  userDropDown.style.left = posx + 'px';
  userDropDown.style.top = posy + 'px';

  getUserDetails('name=' + name);
}

function checkImage() {
  var img = document.getElementById('tiqitUserImage');

  img.removeEventListener('load', checkImage, false);

  if (img.naturalWidth == 327 && img.naturalHeight == 401) {
    var image = new Image(327, 401);
    image.src = img.src;

    // So, doesn't seem hugely scientific, but this could be the empty image!
    // Set it back to the dir photo in case it is.
    img.src = Tiqit.config['userdetails']['photo_url'].replace('%s', username);
  }
}

function setImage(uname) {
  var newimg = document.createElement('img');
  newimg.src = Tiqit.config['userdetails']['photo_url'].replace('%s', username);
  newimg.title = name;
  newimg.alt = name;
  newimg.id = 'tiqitUserImage';
  newimg.width = 60;
  newimg.height = 80;

  var oldimg = document.getElementById('tiqitUserImage');
  oldimg.parentNode.replaceChild(newimg, oldimg);
}

function detailsError(event) {
  sendMessage(2, "Unable to get user details due to unexpected networking error.");
  loadUserData('unknown', 'Unknown', 0, 'Unknown', '', '', '', 0);
}

function getXmlContent(doc, tag) {
  var text = '';
  var tags = doc.getElementsByTagName(tag);
  for (var i = 0; i < tags.length; i++) {
    text += tags[i].textContent;
  }
  return text;
}

function detailsLoaded(event) {
  if (event.target.status == 200 && event.target.responseXML) {
    var uid = getXmlContent(event.target.responseXML, 'uname');
    var cn = getXmlContent(event.target.responseXML, 'cname');
    var employeeNumber = getXmlContent(event.target.responseXML, 'unum');
    var title = getXmlContent(event.target.responseXML, 'title');
    var vendorname = getXmlContent(event.target.responseXML, 'company');
    var description = getXmlContent(event.target.responseXML, 'dept');
    var telephonenumber = getXmlContent(event.target.responseXML, 'phone');
    var manageruid = getXmlContent(event.target.responseXML, 'manager');
    loadUserData(uid, cn, employeeNumber, title, vendorname, description, telephonenumber, manageruid);
  } else {
    sendMessage(2, "Failed to load user details. Error " + event.target.status + ".");
    loadUserData('unknown', 'Unknown', 0, 'Unknown', '', '', '', 0);
  }
}

function getUserDetails(query) {
  var req = new XMLHttpRequest();
  req.open("GET", 'userdetails.py?' + query, true);
  req.onload = detailsLoaded;
  req.onerror = detailsError;
  req.send(null);
}

function loadUserData(uname, name, num, job, vendor, desc, phone, manager) {
  if (!username) {
    username = uname;
  }
  if (username != uname) {
    return;
  }

  userDropDown.style.minWidth = userDropDown.clientWidth;

  var temp = document.getElementById('tiqitUserImage');
  temp.setAttribute('employeenumber', num);
  setImage(uname);

  temp = document.getElementById('tiqitUserFullName').lastChild;
  temp.a = 'tiqitUserDirectory';
  temp.href = Tiqit.config['userdetails']['directory_url'].replace('%s', username);
  temp.textContent = name;

  temp = document.getElementById('tiqitUserFullName').firstChild;
  temp.setAttribute('managernum', manager);

  temp = document.getElementById('tiqitUserEmail').firstChild;
  temp.href = 'mailto:' + uname + '@' + Tiqit.config['userdetails']['maildomain'] + subject;
  temp.textContent = uname;

  temp = document.getElementById('tiqitUserPhone').firstChild;
  temp.textContent = phone;
  if (phone) {
    temp.href = 'javascript:dial("' + name + '", "' + phone + '")';
  } else {
    temp.href = '';
  }

  temp = document.getElementById('tiqitUserJob').firstChild;
  if (vendor) {
    temp.textContent = job + ', ' + vendor;
  } else {
    temp.textContent = job;
  }

  temp = document.getElementById('tiqitUserDept').firstChild;
  temp.textContent = desc;

  setTimeout(resizeShadow, 1);
}

function resizeShadow() {
  var rect = userDropDown.getBoundingClientRect();
  if (document.body.offsetWidth - rect.left < userDropDown.clientWidth) {
    userDropDown.style.left = document.body.offsetWidth - userDropDown.clientWidth;
    userDropDownShadow.style.left = (document.body.offsetWidth - userDropDown.clientWidth + 10) + 'px';
  }

  if (window.innerHeight - rect.top < userDropDown.clientHeight) {
    userDropDown.style.top = window.innerHeight - userDropDown.clientHeight;
    userDropDownShadow.style.top = (window.innerHeight - userDropDown.clientHeight + 10) + 'px';
  }

  userDropDownShadow.style.width = userDropDown.clientWidth;
  userDropDownShadow.style.height = userDropDown.clientHeight;
}
