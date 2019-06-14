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

% cloud = (output['environment'])
<br>
<form action="/submitClass" method="post" accept-charset="utf-8">
<table>

%# The following are required for every request and are not stored in the course document in the database

<tr><td>sender:</td><td><input type="text" name="sender" value="{{user['user']}}" readonly></td></tr>
<tr><td>instructor:</td><td><input type="text" name="instructor" pattern="[a-zA-Z][-a-zA-Z0-9]*" placeholder="Letters and numbers only. No spaces" required></td></tr>


<tr><td>numberOfSubOrgs</td><td><select name="numberOfSubOrgs">
% for num in range(1,21):
<option value={{num}}>{{num}}</option>
% end
</select></td></tr>

<tr><td>sensor</td><td><select name="sensor"><option value="yes">yes</option><option value="no">no</option></select></td></tr>

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

<tr><td>timeszone</td><td><select name="timezone">
  %for zone in timezone:
      <option value="{{zone}}">{{zone}}</option>
  %end
</select></td></tr>



<tr><td>tag</td><td><input type="text" name="tag" pattern="[a-zA-Z][-a-zA-Z0-9]*" placeholder="Letters and numbers only. No spaces" required></td></tr>


<tr><td>startDate</td><td><input type="date" name="startDate"></td><td><input type="checkbox" name="startDate" value="now"> Now</td></tr>
<tr><td>finishDate</td><td><input type="date" name="finishDate"></td></tr>
<tr><td>suspend</td><td><select name="suspend"><option value="yes">yes</option><option value="no">no</option></select></td></tr>


% for k, v in sorted(output.items()):
%#print (k, v)

%# List of parameters that we don't want to pass to the API
% if k in ["_id", "sensorParameters", "courseTemplate", "environment", "resumeScriptName", "sensorTemplate", "startScriptName", "suspendScriptName", "finishScriptName"]:
% pass


% elif k == "cloudFormationParameters":
<tr><td> &nbsp; </td><td> &nbsp; </td></tr>
<tr><td><b>Cloud Parameters</b></td><td> &nbsp; </td></tr>

% for x in v:

% if x['paramType'] == 'plugin-prompt':
<tr><td>{{x['paramKey']}}</td><td><input type="text" name="{{x['paramKey']}}"></td></tr>
% elif x['paramType'] == 'prompt':
<tr><td>{{x['paramKey']}}</td><td><input type="text" name="{{x['paramKey']}}"></td></tr>

% elif x['paramType'] == 'plugin-static':
<tr><td>{{x['paramKey']}}</td><td>{{x['paramValue']}}</td></tr>
% elif x['paramType'] == 'static':
<tr><td>{{x['paramKey']}}</td><td>{{x['paramValue']}}</td></tr>

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

% elif k == "notifications":
<tr><td><b> &nbsp; </b></td><td> &nbsp; </td></tr>
<tr><td><b>Notifications:</b></td><td> &nbsp; </td></tr>

% for x in v:
% if x['notificationType'] == 'prompt':
<tr><td>{{x['notificationKey']}}</td><td><input type="text" name="{{x['notificationKey']}}"></td></tr>
% elif x['notificationType'] == 'static':
<tr><td>{{x['notificationKey']}}</td><td>{{x['recipients']}}</td></tr>



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

%elif k == "courseName":
<tr><td><input type="hidden" name="course" value="{{v}}"/>
{{k}}</td><td>{{v}}</td></tr>

%else:
<tr><td><input type="hidden" name="{{k}}" value="{{v}}"/>
{{k}}</td><td>{{v}}</td></tr>
% end
% end

</table>
<input type="submit" value="Submit">
</form>


</div>


%rebase base
