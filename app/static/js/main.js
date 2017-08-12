/**
 * Created by dmitry on 7/27/17.
 */
;(
    function () {
        $(document).ready(function () {
            console.log(window.location.hash + '-collapse-id');
            $(window.location.hash + '-collapse-id').collapse();
        })
    }
)();
