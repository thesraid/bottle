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


%import json
% # Cycle through the json file as in comes in as a list
%for doc in dbOutput:                   # for jsonOutput 1
% heading = ((doc['startDate'])[:-9] + " | " + doc['course'] + " | " + doc['instructor'] + " | " + doc['tag'] + " | " + doc['jobStatus'])
% jobId = doc['_id']

%if summary:
<button class="collapsible">{{heading}}</button>
<div class="content">
%else:
<h2>{{heading}}</h2>
%end

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

%    elif (k == "errorInfo") and not summary:
<tr><td>{{k}}</td><td>
% for error in doc[k]:
 {{error}}</br></br>
% end
</td>
</tr>

%    elif (k == "successInfo") and not summary:
<tr><td>{{k}}</td><td>
% for error in doc[k]:
 {{error}}</br></br>
% end
</td>
</tr>

%    elif (k == "notifications") and not summary:
<tr><td>{{k}}</td><td>
% for error in doc[k]:
 {{error}}</br></br>
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



% # If the key is finished Date then add an option to extend the labs
%   elif (k == "finishDate") and not summary:
       <tr><td>{{k}}</td><td>{{v}} <a href="/extendJob/{{jobId}}" title="Time in UTC | This will disable the suspending of labs">Extend by 3 hours</a></td></tr>
%    elif summary and (k not in ['sender', 'instructor', 'region', 'startDate', 'finishDate', 'timezone', 'numberOfSubOrgs']):
%      pass
%    else:
%      if (k in ['startDate', 'finishDate']):
%        v = v[:-9]
%      end
       <tr><td>{{k}}</td><td>{{v}}</td></tr>

%    end                                     #if k end 3

%  end                                   # end for doc 2
</table>
% # If the variable delete is true this indicates that this job can be deleted. 
% if delete and not summary:
   <a href="../deleteJob/{{jobId}}" style="color: rgb(255,0,0)">Delete</a>
% elif not summary:
   <a href="../stopJob/{{jobId}}" style="color: rgb(255,0,0)">Stop Running Job</a>
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
