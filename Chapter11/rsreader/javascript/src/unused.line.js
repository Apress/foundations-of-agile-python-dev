
function line(m, x, b) {
   return m*x + b;
}

function validateSlope() {
    var slope  = document.lineForm.slope.value;
    var errorMsg = document.getElementById('errorMsg');
    if (!slope) {
        errorMsg.innerHTML = 'You must define a slope';
    } else if (isNaN(parseInt(slope))) {
        errorMsg.innerHTML = "The slope must be a number";
    } else {
        errorMsg.innerHTML = '';
    }
}
