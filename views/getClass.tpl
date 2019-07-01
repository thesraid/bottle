<h2>Schedule</h2>
% import json



<div align="center">
<form method="post">
% jOutput = json.loads(output)

<form>

<select name = "course">
%for doc in jOutput:
%try:
%# print (doc['courseName'])
<option value="{{doc['courseName']}}"> {{doc['courseName']}}<br>
% except:
% pass
% end
% end
% end
</select>
<input type="submit" value="Submit">

</form>

</div>


%rebase base

