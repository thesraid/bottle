<h2>Output</h2>
% import json

<div align="left">
<button onclick="goBack()">Go Back</button>

<script>
function goBack() {
  window.history.back();
}
</script>

% cloud = (output['environment'])

<form action="/submitClass" method="post">
<p>&nbsp;</p>

%# The following are required for every request and are not stored in the course document in the database

sender: <input type="text" name="sender"><br/>
instructor: <input type="text" name="instructor"><br/>


numberOfSubOrgs: <select name="numberOfSubOrgs">
% for num in range(20):
<option value={{num}}>{{num}}</option>
% end
</select><br/>

sensor: <select name="sensor"><option value="yes">yes</option><option value="no">no</option></select><br/>

% for doc in config:
%   for title in doc:
%     if title not in ["_id", "key"]:

%        if title == "region":
          {{title}}:<select name="region">
%          for cloudList in (doc[title]):

%             for k, v in cloudList.items():
%              if k == cloud:
%                for l in v:
                  
%                  for o, p in l.items():
                    <option value="{{o}}">{{o}}</option>
%                  end


%               end
%              end
%             end


%          end

          </select> <br/>

%       else:
        {{title}}:
        % listOfItems = doc[title]
        <select name="{{title}}">
        %for item in listOfItems:
          <option value="{{item}}">{{item}}</option>
        %end
        </select>
        <br/>

%       end
%     end
%   end
% end

tag: <input type="text" name="tag"><br/>


startDate: <input type="date" name="startDate"> &nbsp; <input type="checkbox" name="startDate" value="now"> Now<br>
finishDate: <input type="date" name="finishDate""><br/>
suspend: <select name="suspend"><option value="yes">yes</option><option value="no">no</option></select><br/>


% for k, v in sorted(output.items()):
%#print (k, v)

%# List of parameters that we don't want to pass to the API
% if k in ["_id", "sensorParameters", "courseTemplate", "environment", "resumeScriptName", "sensorTemplate", "startScriptName", "suspendScriptName", "finishScriptName"]:
% pass

%elif k == "courseName":
<input type="hidden" name="course" value="{{v}}"/>
{{k}} : {{v}} <br/>
% elif k == "cloudFormationParameters":
<br/><b>cloudFormationParameters:</b> <br/>

% for x in v:

% if x['paramType'] == 'plugin-prompt':
{{x['paramKey']}}: <input type="text" name="{{x['paramKey']}}"><br/>
% elif x['paramType'] == 'prompt':
{{x['paramKey']}}: <input type="text" name="{{x['paramKey']}}"><br/>


% elif x['paramType'] == 'list':
{{x['paramKey']}} : 
<select name="{{x['paramKey']}}">
% for z in x['paramValidInput']:
<option value={{z}}>{{z}}</option>
% end
</select><br/>

% elif x['paramType'] == 'plugin-list':
{{x['paramKey']}} : 
<select name="{{x['paramKey']}}">
% for z in x['paramValidInput']:
<option value={{z}}>{{z}}</option>
% end
</select><br/>

% end


% end

% elif k == "notifications":
<br/><b>notifications:</b> <br/>

% for x in v:
% if x['notificationType'] == 'prompt':
{{x['notificationKey']}}: <input type="text" name="{{x['notificationKey']}}"><br/>



% elif x['notificationType'] == 'list':
{{x['notificationKey']}} : 
<select name="{{x['notificationKey']}}">
% for z in x['validInput']:
<option value={{z}}>{{z}}</option>
% end
</select>

% end

%#{{x}}<br/>

% end

%else:
<br/>
<input type="hidden" name="{{k}}" value="{{v}}"/>
{{k}} : {{v}} <br/>
% end
% end

<input type="submit" value="Submit">
</form>

</div>


%rebase base
