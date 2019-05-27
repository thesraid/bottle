<script>
    setInterval(function() {window.location.reload();}, 10000);
</script>
<style>
    pre {
        text-align: left;
    }
</style>

%with open(pathToFile, "r") as myfile:
%       data = myfile.read()
%       myfile.close()

<pre>{{ data }}</pre>
%rebase base
