%import json



<div align="left">

<button onclick="goBack()">Go Back</button>

<script>
function goBack() {
  window.history.back();
}
</script>

% id = Output.get("_id")
% sub = Output.get("subOrgName")

<p> The subOrg with the
% if id:
id:   {{ id }}
% elif sub:
name   "{{ sub }}" 
%end
is now marked as ready</p>
</div>

%rebase base