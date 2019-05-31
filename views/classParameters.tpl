<h2>Output</h2>
% import json

<div align="left">
<button onclick="goBack()">Go Back</button>

<script>
function goBack() {
  window.history.back();
}
</script>

<form action="/submitClass" method="post">
<p>&nbsp;</p>
% for k, v in sorted(output.items()):
% print (k, v)

% if k == "cloudFormationParameters":
<br/>cloudFormationParameters: <br/><br/>

% for x in v:

% if x['paramType'] == 'plugin-prompt':
{{x['paramKey']}}: <input type="text" name="{{x['paramKey']}}"><br/>
% elif x['paramType'] == 'prompt':
{{x['paramKey']}}: <input type="text" name="{{x['paramKey']}}"><br/>
% elif x['paramType'] == 'static':
<input type="hidden" name="{{x['paramKey']}}" value="{{x['paramValue']}}"/>
{{x['paramKey']}}: {{x['paramValue']}}<br/>
% elif x['paramType'] == 'plugin-static':
<input type="hidden" name="{{x['paramKey']}}" value="{{x['paramValue']}}"/>
{{x['paramKey']}}: {{x['paramValue']}}<br/>

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
<br/>notifications: <br/>

% for x in v:
% if x['notificationType'] == 'prompt':
{{x['notificationKey']}}: <input type="text" name="{{x['notificationKey']}}"><br/>

% elif x['notificationType'] == 'static':
<input type="hidden" name="{{x['notificationKey']}}" value="{{x['recipients']}}"/>
{{x['notificationKey']}}: {{x['recipients']}}<br/>

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

% elif k == "sensorParameters":
<br/>sensorParameters : <br/>

% for x in v:

<input type="hidden" name="{{x['paramKey']}}" value="{{x['paramFile']}}"/>
 {{x['paramKey']}}: {{x['paramFile']}}<br/>
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
