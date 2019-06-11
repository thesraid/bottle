<h2>Schedule</h2>
% import json


<button onclick="goBack()">Go Back</button>

<script>
function goBack() {
  window.history.back();
}
</script>
<div align="center">
<form method="post">
% jOutput = json.loads(output)

<form>

<select name = "course">
%for doc in jOutput:
%#<input type="radio" name="course" value="{{doc['courseName']}}"> {{doc['courseName']}}<br>
<option value="{{doc['courseName']}}"> {{doc['courseName']}}<br>
% end
</select>
<input type="submit" value="Submit">

</form>

</div>


%rebase base

