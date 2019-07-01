<h2>Output</h2>
% import json

<div align="left">
<button onclick="goBack()">Go Back</button>
<br>
<script>
function goBack() {
  window.history.back();
}
</script>

%# This template is called by webAPI.py

%# It is passed the following
%# output : The course details in JSON format
%# region : List of regiosn from config.py 
%# timezone : List of timezones from config.py
%# instructors : List of instructors from config.py
%# user : The currently logged in user

%# This page will render the class JSON and prompt for the correct input.
%# It will evently be sent to the scheduleClass API and the class scheduled

%# Get the name of the cloud this course is for
% cloud = (output['environment'])
<br>
<form action="/submitClass" method="post" accept-charset="utf-8">
<table>

%# The following are required for every request and are not stored in the course document in the database

%# The sender is the person submitting the request. 
<tr><td>sender:</td><td><input type="text" name="sender" value="{{user['user']}}" readonly></td></tr>

%# The instructor is the person running the class. A list of valid instructors is read from config.py
<tr><td>instructor:</td><td><select name="instructor">
%for item in instructors:
<option value={{item}}>{{item}}</option>
% end

%# The nuber of subOrgs is the number of student positions. Limited to 21 here but the API limit may be different (View RequestHandler.py)
<tr><td>numberOfSubOrgs</td><td><select name="numberOfSubOrgs">
% for num in range(1,21):
<option value={{num}}>{{num}}</option>
% end
</select></td></tr>

%# Should a sensor be requested for the class or not
<tr><td>sensor</td><td><select name="sensor"><option value="yes">yes</option><option value="no">no</option></select></td></tr>

%# The region that the subOrg should be deployed into. List of valid regions for each cloud type are read from config.py
%# Only show regions for the cloud that this course will be deployed into. The cloud for this course is stored in theo course json
<tr><td>region</td><td><select name="region">
  %for item in region:
  % for x in item:
  %  if x == cloud:
  %   for loc in item[cloud]:
        <option value="{{loc}}">{{loc}}</option>
  %   end
  %  end
  % end  
  %end
</select></td></tr>

%# Show the available timezones passed in as a list from config.py
<tr><td>timezone</td><td><select name="timezone">
  %for zone in timezone:
      <option value="{{zone}}">{{zone}}</option>
  %end
</select></td></tr>


%# Add a tag to identify the course. Retrict the tag format so that it is compatiable with all clouds. 
<tr><td>tag</td><td><input type="text" name="tag" pattern="[a-zA-Z][-a-zA-Z0-9]*" placeholder="Example: ANYDC-WET-Apr29-Apr30-joriordan" required></td></tr>

%# Choose start, finsih and suspend options. Again these arne't in the course so can't be dynamically created. 
<tr><td>startDate</td><td><input type="date" name="startDate"></td><td><input type="checkbox" name="startDate" value="now"> Now</td></tr>
<tr><td>finishDate</td><td><input type="date" name="finishDate"></td></tr>
<tr><td>suspend</td><td><select name="suspend"><option value="yes">yes</option><option value="no">no</option></select></td></tr>

%# The course JSON was passed in as a variable called output. Cycle through each key, value pair and ask for input. 
%# There are different types of inputs. Some are simple text imputs while some are lists that need to be presented to the user to choose from.
% for k, v in sorted(output.items()):
%#print (k, v)

%# List of course keys, read from the course JSON from the database, that we don't want to pass to the API
% if k in ["_id", "sensorParameters", "courseTemplate", "environment", "resumeScriptName", "sensorTemplate", "startScriptName", "suspendScriptName", "finishScriptName"]:
% pass

%# We don't need to display the course name as it's already been chosen by the user. But we still need to submit the course name to the API
%elif k == "courseName":
<input type="hidden" name="course" value="{{v}}"/>

%# If the key is cloudFormationParameters then it will be a nested JSON
% elif k == "cloudFormationParameters":
<tr><td> &nbsp; </td><td> &nbsp; </td></tr>
<tr><td><b>Cloud Parameters</b></td><td> &nbsp; </td></tr>

%# The value of cloudFormationParameters is a nested JSON. Iterate through it
% for x in v:

%# If cloudFormationParameters is a prompt type then present a text box
% if x['paramType'] == 'plugin-prompt':
<tr><td>{{x['paramKey']}}</td><td><input type="text" name="{{x['paramKey']}}"></td></tr>
% elif x['paramType'] == 'prompt':
<tr><td>{{x['paramKey']}}</td><td><input type="text" name="{{x['paramKey']}}"></td></tr>

%# If cloudFormationParameters is static type display it but don't allow the user to edit
% elif x['paramType'] == 'plugin-static':
<tr><td>{{x['paramKey']}}</td><td>{{x['paramValue']}}</td></tr>
% elif x['paramType'] == 'static':
<tr><td>{{x['paramKey']}}</td><td>{{x['paramValue']}}</td></tr>

%# If cloudFormationParameters is a list type then present a drop down box with each list choice
% elif x['paramType'] == 'list':
<tr><td>{{x['paramKey']}}</td><td> 
<select name="{{x['paramKey']}}">
% for z in x['paramValidInput']:
<option value={{z}}>{{z}}</option>
% end
</select></td></tr>

% elif x['paramType'] == 'plugin-list':
<tr><td>{{x['paramKey']}}</td><td>
<select name="{{x['paramKey']}}">
% for z in x['paramValidInput']:
<option value={{z}}>{{z}}</option>
% end
</select></td></tr>

% end


% end



%# The value of notifications is a nested JSON. Iterate through it

% elif k == "notifications":
<tr><td><b> &nbsp; </b></td><td> &nbsp; </td></tr>
<tr><td><b>Notifications:</b></td><td> &nbsp; </td></tr>

%# To be used to group hidden ones together. These will be displayed seperatly at the bottom of the page as they are not editable and are numberOfSubOrgs
%# We don't want to overwhelm the user by showing notifications that they can't edit anyway
% hiddenStaticNotificationsList = {}

%# If notificationType is a prompt type then present a text box
% for x in v:
% if x['notificationType'] == 'prompt':
<tr><td>{{x['notificationKey']}}</td><td><input type="text" name="{{x['notificationKey']}}"></td></tr>
% elif x['notificationType'] == 'static':
%  hiddenStaticNotificationsList.update({x['notificationKey'] : x['recipients']})
%#<tr><td>{{x['notificationKey']}}</td><td>{{x['recipients']}}</td></tr>

%# If notificationType is a list type then present a drop down box with each list choice
% elif x['notificationType'] == 'list':
<tr><td>{{x['notificationKey']}}</td><td>
<select name="{{x['notificationKey']}}">
% for z in x['validInput']:
<option value={{z}}>{{z}}</option>
% end
</select></td></tr>


% end

%#{{x}}<br/>



% end

%# Everything else
%else:
<tr><td><input type="hidden" name="{{k}}" value="{{v}}"/>
{{k}}</td><td>{{v}}</td></tr>
% end
% end

</table>
<input type="submit" value="Submit">
</form>


</div>


<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>
<p>&nbsp;</p>

%# Show the notifications that the user can't change. Just as an FYI for the user
<font color = "#9c9ea1"><strong>Static Notifications</strong></font>
<table>
% for x, y in hiddenStaticNotificationsList.items():

<tr><td><font color = "#9c9ea1">{{x}}</font></td><td><font color = "#9c9ea1">{{y}}</font></td></tr>

% end
</table>

%rebase base
