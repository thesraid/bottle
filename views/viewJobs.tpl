<html>
<head><style>
.collapsible {
  background-color: #777;
  color: white;
  cursor: pointer;
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
  display: none;
  overflow: hidden;
}
</style></head>

<body>
  
  
  <!-- View Jobs -->
  <div class="w3-container" id="services" style="margin-top:75px">
    <h1 class="w3-xxxlarge w3-text-red"><b>View {{pageName}}</b></h1>

%summary = False
%if pageName != "Job":
% summary = True
%end

%if summary:
.
%end

%import json
% # Cycle through the json file as in comes in as a list
%for doc in dbOutput:                   # for jsonOutput 1
% heading = ((doc['startDate'])[:-9] + " | " + doc['course'] + " | " + doc['tag'] + " | " + doc['jobStatus'])
% jobId = doc['_id']


<button class="collapsible">{{heading}}</button>
<div class="content">

<table>
%  for k, v in sorted(doc.items()):              # for doc 2
% delete = False

% # Only show the delete link for jobs that are pending, failed or finished
% if (doc['jobStatus'] == "pending") or (doc['jobStatus'] == "failed") or (doc['jobStatus'] == "finished"):
%   delete = True
% end

% # If the key is _id then add a link to the job page for that ID
%    if (k == "_id"):      # if k 3
      <tr><td>{{k}}</td><td><a href="../viewJob/{{jobId}}">{{v}}</b></a></td></tr>
%
% # If the key is subOrgs then add a link to the subOrg page
%    elif (k == "subOrgs"):
<tr><td>{{k}}</td><td>
% for org in doc[k]:
 <a href="../viewSubOrg/subOrgName/{{org}}"><b>{{org}}</b></a>
% end
</td>
</tr>
% # If the key is FailedSubOrgs then add a link to the subOrg page
%    elif (k == "failedSubOrgs"):
<tr><td>{{k}}</td><td>
% for org in doc[k]:
 <a href="../viewSubOrg/subOrgName/{{org}}"><b>{{org}}</b></a>
% end
</td>
</tr>
% # If the key is finsihed Date and it's in the scheduled Jobs page then add an option to extend the labs
%   elif (k == "finishDate") and (pageName == "scheduledJobs"):
       <tr><td>{{k}}</td><td>{{v}} <a href="/extendJob/{{jobId}}" title="This will disable the suspending of labs">Extend by 3 hours</a></td></tr>
%    else:
       <tr><td>{{k}}</td><td>{{v}}</td></tr>
%    end                                     #if k end 3

%  end                                   # end for doc 2
</table>
% # If the variable delete is true this indicates that this job can be deleted. 
% if delete:
   <a href="../deleteJob/{{jobId}}" style="color: rgb(255,0,0)">Delete</a>
% end

</div>
<p>&nbsp;</p>
% end                                   # end for dbOutput 1
    </p>
  </div>

<!-- Script for collapsing the entries -->
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
