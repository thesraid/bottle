<html>
<head><style>
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
  padding: 18px;
  width: 100%;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.active, .collapsible:hover {
  background-color: #555;
}

.content {
  padding: 0 18px;
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
</style></head>

<body>
  
%import json

<!-- View Running SubOrgs -->
  <div class="w3-container" id="services" style="margin-top:75px">
    <h1 class="w3-xxxlarge w3-text-red">Running</h1>
    <hr style="width:50px;border:5px solid red" class="w3-round"> 

%for doc in dbOutput:                   # for jsonOutput 1
% if doc['status'] != 'running':
%  continue
% end
% heading = doc['subOrgName']
% dbId = doc['_id']

<button class="collapsible">{{heading}}</button>
<div class="content" align="left">

%  for k, v in sorted(doc.items()):              # for doc 2
%    if (k == "jobID"):                         # if k 3
      {{k}} : <a href="/viewJob/{{v}}">{{v}}<br/></a>
%   elif (k == "_id"):
      {{k}} : <a href="/viewSubOrg/_id/{{v}}">{{v}}<br/></a>
%   elif (k == "subOrgName"):
      {{k}} : <a href="/viewSubOrg/subOrgName/{{v}}">{{v}}<br/></a>
%    else:
       {{k}} : {{v}}<br/>
%    end                                     #if k end 3
%  end                                   # end for doc 2
</div>
<p>&nbsp;</p>
% end                                   # end for dbOutput 1
    </p>
  </div>


<!-- View Failed SubOrgs -->
  <div class="w3-container" id="services" style="margin-top:75px">
    <h1 class="w3-xxxlarge w3-text-red">Failed</h1>
    <hr style="width:50px;border:5px solid red" class="w3-round"> 

%for doc in dbOutput:                   # for jsonOutput 1
% if doc['status'] != 'failed':
%  continue
% end
% heading = doc['subOrgName']
% dbId = doc['_id']

<button class="collapsible">{{heading}}</button>
<div class="content" align="left">

%  for k, v in sorted(doc.items()):              # for doc 2
%    if (k == "jobID"):                         # if k 3
      {{k}} : <a href="/viewJob/{{v}}">{{v}}<br/></a>
%   elif (k == "_id"):
      {{k}} : <a href="/viewSubOrg/_id/{{v}}">{{v}}<br/></a>
%   elif (k == "subOrgName"):
      {{k}} : <a href="/viewSubOrg/subOrgName/{{v}}">{{v}}<br/></a>
%    else:
       {{k}} : {{v}}<br/>
%    end                                     #if k end 3
%  end                                   # end for doc 2
<a href = "/readySubOrg/subOrgName/{{heading}}">Mark as Ready</a><br/>
</div>
<p>&nbsp;</p>
% end                                   # end for dbOutput 1
    </p>
  </div>

<!-- View Free SubOrgs -->
  <div class="w3-container" id="services" style="margin-top:75px">
    <h1 class="w3-xxxlarge w3-text-red">Free</h1>
    <hr style="width:50px;border:5px solid red" class="w3-round"> 

%for doc in dbOutput:                   # for jsonOutput 1
% if doc['status'] != 'free':
%  continue
% end
% heading = doc['subOrgName']
% dbId = doc['_id']

<button class="collapsible">{{heading}}</button>
<div class="content" align="left">

%  for k, v in sorted(doc.items()):              # for doc 2
%    if (k == "jobID"):                         # if k 3
      {{k}} : <a href="../viewJob/{{v}}">{{v}}<br/></a>
%   elif (k == "_id"):
      {{k}} : <a href="/viewSubOrg/_id/{{v}}">{{v}}<br/></a>
%   elif (k == "subOrgName"):
      {{k}} : <a href="/viewSubOrg/subOrgName/{{v}}">{{v}}<br/></a>
%    else:
       {{k}} : {{v}}<br/>
%    end                                     #if k end 3
%  end                                   # end for doc 2
</div>
<p>&nbsp;</p>
% end                                   # end for dbOutput 1
    </p>
  </div>

<!-- View Other SubOrgs -->
  <div class="w3-container" id="services" style="margin-top:75px">
    <h1 class="w3-xxxlarge w3-text-red">Other</h1>
    <hr style="width:50px;border:5px solid red" class="w3-round"> 

%for doc in dbOutput:                   # for jsonOutput 1
% if (doc['status'] == 'free') or (doc['status'] == 'running') or (doc['status'] == 'failed'):
%  continue
% end
% heading = doc['subOrgName']
% dbId = doc['_id']

<button class="collapsible">{{heading}}</button>
<div class="content" align="left">

%  for k, v in sorted(doc.items()):              # for doc 2
%    if (k == "jobID"):                         # if k 3
      {{k}} : <a href="../viewJob/{{v}}">{{v}}<br/></a>
%   elif (k == "_id"):
      {{k}} : <a href="/viewSubOrg/_id/{{v}}">{{v}}<br/></a>
%   elif (k == "subOrgName"):
      {{k}} : <a href="/viewSubOrg/subOrgName/{{v}}">{{v}}<br/></a>
%    else:
       {{k}} : {{v}}<br/>
%    end                                     #if k end 3
%  end                                   # end for doc 2
</div>
<p>&nbsp;</p>
% end                                   # end for dbOutput 1
    </p>
  </div>

<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>

</body>
</html>


%rebase base