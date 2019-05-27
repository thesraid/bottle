%import json



<div aligh="left">

% if (type(jobId) is str ):
%  jsonInput = json.loads(jobId)
%else:
%  jsonInput = jobId
%end

</p>Retrieved  {{ jsonInput['deleted'] }} </p>

<p><small>_id:   {{ jsonInput['_id'] }} </small></p>
</div>

%rebase base