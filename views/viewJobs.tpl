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
  
  
  <!-- View Jobs -->
  <div class="w3-container" id="services" style="margin-top:75px">
    <h1 class="w3-xxxlarge w3-text-red"><b>View {{pageName}}</b></h1>
    <hr style="width:50px;border:5px solid red" class="w3-round">


%import json
%delete = False
%for doc in dbOutput:                   # for jsonOutput 1
% heading = doc['tag']
% jobId = doc['_id']
% if (doc['jobStatus'] == "pending") or (doc['jobStatus'] == "failed") or (doc['jobStatus'] == "finished"):
%   delete = True
% end

<button class="collapsible">{{heading}}</button>
<div class="content" align="left">

%  for k, v in sorted(doc.items()):              # for doc 2
%    if (k == "_id"):      # if k 3
      <a href="../viewJob/{{jobId}}"><b>{{k}} : {{v}} </b></a><br/>
%    elif (k == "subOrgs"):
{{k}} : </br>
% for org in doc[k]:
 :&nbsp; <a href="../viewSubOrg/subOrgName/{{org}}"><b>{{org}}</b></a><br/>
% end
%    else:
       {{k}} : {{v}}<br/>
%    end                                     #if k end 3

%  end                                   # end for doc 2
% if delete:
   <a href="../deleteJob/{{jobId}}" style="color: rgb(255,0,0)">Delete</a>
% end
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