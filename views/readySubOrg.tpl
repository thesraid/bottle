%import json



<div align="left">

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